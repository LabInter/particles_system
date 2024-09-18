from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image, ImageDraw, ImageFont
import random
import numpy as np

class TextAnimation:

    def split_phrase(self, phrase, max_width, letter_size):
        words = phrase.split(' ')
        lines = []
        current_line = ""

        for word in words:
            if current_line:  # Se já houver texto na linha, adicione um espaço antes da palavra
                test_line = current_line + " " + word
            else:
                test_line = word

            if len(test_line) * letter_size > max_width:
                lines.append(current_line.strip())
                current_line = word
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines

    def calculate_final_positions(self, lines, start_x, start_y, letter_size, line_height):
        self.positions = []
        y = start_y
        for line in lines:
            x = start_x - (len(line) * letter_size) // 2
            for char in line:
                if char.strip():  # Verifica se o caractere não é um espaço vazio
                    self.positions.append((char, (x, y)))
                x += letter_size
            y += line_height

    def calculate_start_x_position(self, phrase, text_position, letter_size):
        total_width = len(phrase) * letter_size
        return text_position[0] - (total_width // 2)

    def __init__(self, phrase, screen_width, screen_height, text_position):
        self.phrase = phrase
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.initial_font_size = 2
        self.final_font_size = 20
        self.growth_duration = 300
        self.animation_velocity = 0.025
        self.letter_size_px = self.final_font_size // 2
        self.line_height_px = self.final_font_size
        max_width = screen_width // 2

        lines = self.split_phrase(phrase, max_width, self.letter_size_px)
        self.calculate_final_positions(lines, text_position[0], text_position[1], self.letter_size_px, self.line_height_px)

        # Cria GrowingLetter para cada letra
        self.letters = [GrowingLetter(letter, pos, self.initial_font_size, self.final_font_size, self.growth_duration, self.screen_width, self.screen_height) 
                        for letter, pos in self.positions if letter.strip()]

    def draw_and_update(self):
        for letter in self.letters:
            letter.update(self.animation_velocity)
            letter.draw()

class GrowingLetter:
    def __init__(self, letter, final_position, initial_font_size, final_font_size, growth_duration, screen_width, screen_height):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.letter = letter
        self.final_x, self.final_y = final_position
        self.initial_font_size = initial_font_size
        self.final_font_size = final_font_size
        self.font_size = initial_font_size
        self.growth_counter = 0
        self.growth_duration = growth_duration

        # Criando a imagem de texto com Pillow
        self.font = ImageFont.load_default()
        self.image, self.image_data = self.create_letter_image(self.letter, self.font)
        self.texture_id = self.create_texture(self.image_data, self.image.size)

    def create_letter_image(self, letter, font):
        """Cria a imagem da letra com o Pillow"""
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), letter, font=font, fill=(255, 255, 255, 255))

        img_data = np.array(list(img.getdata()), np.uint8)
        return img, img_data

    def create_texture(self, image_data, size):
        """Cria uma textura OpenGL a partir de dados de imagem"""
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size[0], size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glBindTexture(GL_TEXTURE_2D, 0)
        return texture_id

    def update(self, move_factor):
        """Atualiza a posição e tamanho da letra"""
        if self.growth_counter < self.growth_duration:
            self.font_size = self.initial_font_size + (self.final_font_size - self.initial_font_size) * (self.growth_counter / self.growth_duration)
            self.font = ImageFont.truetype("arial.ttf", int(self.font_size))
            self.image, self.image_data = self.create_letter_image(self.letter, self.font)
            self.texture_id = self.create_texture(self.image_data, self.image.size)
            self.growth_counter += 1

        self.x = self.x + (self.final_x - self.x) * move_factor
        self.y = self.y + (self.final_y - self.y) * move_factor

    def draw(self):
        """Desenha a letra usando OpenGL"""
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(self.x, self.y)
        glTexCoord2f(1, 0); glVertex2f(self.x + 64, self.y)
        glTexCoord2f(1, 1); glVertex2f(self.x + 64, self.y + 64)
        glTexCoord2f(0, 1); glVertex2f(self.x, self.y + 64)
        glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)