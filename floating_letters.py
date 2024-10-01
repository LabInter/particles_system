import pygame
import random

class TextAnimation:
    def __init__(self, phrase, screen_width, screen_height, image_bottom):
        self.phrase = phrase
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.initial_font_size = 2
        self.final_font_size = 20
        self.growth_duration = 300
        self.animation_velocity = 0.025
        self.font_name = 'arial'
        self.color = (255, 255, 255)
        self.line_spacing = 1.2  # Multiplicador de espaçamento entre linhas

        # Inicializa a fonte com o tamanho final para obter medições precisas
        self.final_font = pygame.font.SysFont(self.font_name, self.final_font_size)

        # Define a largura máxima para a quebra de linha (ajustado)
        max_line_width = self.screen_width // 2

        # Divide a frase em linhas
        self.lines = self.split_phrase(self.phrase, self.final_font, max_line_width)

        # Calcula as posições finais
        self.positions = self.calculate_final_positions(self.lines, image_bottom, self.final_font)

        # Cria os sprites GrowingLetter
        self.letters = pygame.sprite.Group()
        for letter, pos in self.positions:
            if letter.strip():
                gl = GrowingLetter(letter, pos, self.initial_font_size, self.final_font_size,
                                   self.growth_duration, self.screen_width, self.screen_height,
                                   self.font_name, self.color)
                self.letters.add(gl)


    def split_phrase(self, phrase, font, max_width):
        words = phrase.split(' ')
        lines = []
        current_line = ""

        for word in words:
            if current_line:
                test_line = current_line + " " + word
            else:
                test_line = word

            test_line_width, _ = font.size(test_line)
            if test_line_width > max_width and current_line:
                lines.append(current_line.strip())
                current_line = word
            elif test_line_width > max_width:
                # A palavra individual é maior que o max_width, então a cortamos
                split_word = self.split_long_word(word, font, max_width)
                lines.extend(split_word[:-1])
                current_line = split_word[-1]
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line.strip())

        return lines

    def split_long_word(self, word, font, max_width):
        chars = list(word)
        current_part = ''
        parts = []

        for char in chars:
            test_part = current_part + char
            part_width, _ = font.size(test_part)
            if part_width > max_width and current_part:
                parts.append(current_part)
                current_part = char
            else:
                current_part = test_part

        if current_part:
            parts.append(current_part)

        return parts

    def calculate_final_positions(self, lines, image_bottom, font):
        positions = []
        total_height = len(lines) * font.get_linesize() * self.line_spacing

        # Calcula o espaço disponível entre a imagem e o final da tela
        available_space = self.screen_height - image_bottom

        # Verifica se o texto cabe no espaço disponível
        if total_height > available_space:
            print("Aviso: O texto é muito alto e pode ser cortado.")
            # Opcionalmente, você pode reduzir o tamanho da fonte aqui

        # Calcula a posição inicial do texto para centralizar verticalmente no espaço disponível
        start_y = image_bottom + (available_space - total_height) // 2

        y = start_y

        for line in lines:
            line_width, _ = font.size(line)
            start_x = (self.screen_width - line_width) // 2  # Centraliza horizontalmente
            x = start_x
            for char in line:
                char_width, _ = font.size(char)
                if char.strip():
                    positions.append((char, (x + char_width // 2, y + font.get_linesize() // 2)))
                x += char_width
            y += font.get_linesize() * self.line_spacing

        return positions


    def draw_and_update(self, screen):
        self.letters.update(self.animation_velocity)
        self.letters.draw(screen)

class GrowingLetter(pygame.sprite.Sprite):
    def __init__(self, letter, final_position, initial_font_size, final_font_size,
                 growth_duration, screen_width, screen_height, font_name, color):
        super().__init__()
        self.letter = letter
        self.final_x, self.final_y = final_position
        self.initial_font_size = initial_font_size
        self.final_font_size = final_font_size
        self.growth_duration = growth_duration
        self.font_name = font_name
        self.color = color

        # Posição inicial aleatória
        self.x = random.uniform(0, screen_width)
        self.y = random.uniform(0, screen_height)

        self.growth_counter = 0
        self.font_size = self.initial_font_size
        self.previous_font_size = 0
        self.font = pygame.font.SysFont(self.font_name, int(self.font_size))
        self.image = self.font.render(self.letter, True, self.color)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, move_factor):
        # Atualiza o tamanho da fonte
        if self.growth_counter < self.growth_duration:
            self.font_size = self.initial_font_size + (self.final_font_size - self.initial_font_size) * (self.growth_counter / self.growth_duration)
            self.growth_counter += 1

            # Recria a fonte e a imagem apenas se o tamanho inteiro da fonte mudou
            if int(self.font_size) != self.previous_font_size:
                self.font = pygame.font.SysFont(self.font_name, int(self.font_size))
                self.image = self.font.render(self.letter, True, self.color)
                self.previous_font_size = int(self.font_size)
                # Atualiza o rect com o novo tamanho da imagem
                self.rect = self.image.get_rect(center=(self.x, self.y))

        # Atualiza a posição
        self.x += (self.final_x - self.x) * move_factor
        self.y += (self.final_y - self.y) * move_factor
        self.rect.center = (self.x, self.y)




# # Inicialização do Pygame e da animação
# pygame.init()
# screen_width = 800
# screen_height = 600
# screen = pygame.display.set_mode((screen_width, screen_height))
# pygame.display.set_caption("Text Animation")
# clock = pygame.time.Clock()

# phrase = "Are some technical objects just in the background, while the closer one gets to an epistemic situation, the more attention needs to be paid to the technical objects that are implied"
# text_position = (screen_width // 2, screen_height // 2)
# animation = TextAnimation(phrase, screen_width, screen_height, text_position)

# # Loop principal
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
    
#     screen.fill((0, 0, 0))
#     animation.draw_and_update(screen)
#     pygame.display.flip()
#     clock.tick(30)

# pygame.quit()
