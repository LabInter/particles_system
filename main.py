import os
import math
import random
from sys import exit

import pygame
from PIL import Image
from pygame.math import Vector2

from Particle import Particle
from double_slit import *
from particles_manager import *
from osc_client import *
from floating_letters import *
from phrases import *
from wave_movement import *
from face_detection import *

class ParticleSimulation:

    def init_sound_variables(self):
        self.peak_width_1 = 400
        self.peak_width_2 = 394
        self.bands = 146
    
    def init_text_variables(self):
        self.text_animation = None

    def init_particles_variables(self):
        self.use_image = True  
        self.use_collision = True
        self.number_of_particles = 4000
        self.particles_speed = 2
        self.particles_radius = 2
        self.particles = []
        self.particle_timer = 0
        self.particle_interval = 1 
        self.wave_movement = False
    
    def init_double_slit_points(self):
        points_x, points_y = self.generate_points()
        x_min, x_max = -10, 10
        y_min, y_max = -4, 4
        self.points = self.transform_points(points_x, points_y, x_min, x_max, y_min, y_max, self.WIDTH, self.HEIGHT)

    def init_particles_from_collision_variables(self):
        self.removed_particles = []
        self.removed_particles_incrementer = 1
        self.particles_from_collision = []
        self.num_particles_from_collision = 0
        self.index_next_to_alive = 0
        self.last_activation_time = 0  # Timer para controlar a ativação das partículas
        self.move_particle_status = False
        self.restart_status = False
        self.particle_index_to_create_final_image = 0
        self.move_particles_velocity = 0.01

    def init_background(self):
        self.bg = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.bg.fill((0, 0, 0))

    def init_restart_transition_variables(self):
        self.speed_particle_restart = 2
        self.speed_incrementer_particle_restart = 0.01
        self.time_transition_to_final_image = 13000
        self.time_transition_to_final_image_counter = 0
        self.count_particles_to_restart = 0
    
    def init_timer(self):
        self.timer = 0

    def choise_final_image(self):
        random_image = random.choice(self.images_paths)
        self.final_image_path = os.path.join('final_images/', random_image)

    def config_text_animation(self, screen_width, screen_height, text_pos):
        self.text_animation = TextAnimation(phrases[random.randint(0, len(phrases)-1)], screen_width, screen_height, text_pos)

    def init_variables(self):
        self.face_detector.init_variables()
        self.init_text_variables()
        self.init_sound_variables()
        self.init_particles_variables()        
        self.init_particles_from_collision_variables()
        self.init_restart_transition_variables()
        self.init_timer()
        self.choise_final_image()
        self.create_final_image(self.final_image_path)
        self.half = len(self.particles_from_collision)//15
        self.config_text_animation(self.WIDTH, self.HEIGHT, self.image_bottom)
        self.clock = pygame.time.Clock()
        self.init_double_slit_points()
        self.init_background()
    
        if self.use_image:
            self.number_of_particles = len(self.images)
        
        self.running = True

    def create_osc_client(self):
        self.osc_client = OscClient("127.0.0.1", 7400)
    
    def create_screen(self):
        pygame.display.set_caption("Particle Simulation")
        # self.screen = pygame.display.set_mode((2560,1080))
        # self.screen = pygame.display.set_mode((1512,982))
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        WIDTH, HEIGHT = pygame.display.get_surface().get_size()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.center = Vector2(WIDTH//2, HEIGHT//2)
        self.box = [0, WIDTH, 0, HEIGHT]
    
    def create_face_detector(self):
        self.face_detector = FaceDetection()
        self.face_detector.config_camera(self.WIDTH, self.HEIGHT)

    def create_particles_manager(self):
        self.particles_manager = ParticlesManager(self.WIDTH, self.HEIGHT, 15)

    def __init__(self):
        pygame.init()
        self.create_screen()
        self.create_osc_client()
        self.create_face_detector()
        self.create_particles_manager()
        self.generate_images()
        self.get_image_paths()
        self.init_variables()

    def move_particles_restart(self):
        self.send_sound_params(400, 394, 146, self.speed_incrementer_particle_restart)
        self.speed_particle_restart += self.speed_incrementer_particle_restart

        should_restart = True

        for particle in self.particles_from_collision:
            if particle.alive:
                particle.noise_offset_x += 0.01
                particle.noise_offset_y += 0.01

                # Gerar deslocamento baseado em Perlin Noise
                angle = math.sin(particle.noise_offset_x) * math.cos(particle.noise_offset_y) * 2 * math.pi
                
                # Desvio orgânico a partir do Perlin Noise
                noise_dx = math.cos(angle) * 0.5  # Pequena variação no x
                noise_dy = math.sin(angle) * 0.5  # Pequena variação no y

                # Atualizar posição movendo para fora, com ruído perlin aplicado
                particle.pos.x += (particle.direction_x + noise_dx) * particle.speed
                particle.pos.y += (particle.direction_y + noise_dy) * particle.speed

                should_restart = False
                pygame.draw.circle(self.screen, particle.color, (particle.pos.x, particle.pos.y), particle.radius)
                if particle.pos.x > self.WIDTH or particle.pos.x < 0 or particle.pos.y > self.HEIGHT or particle.pos.y < 0:
                    particle.alive = False
        
        if should_restart:
            self.restart_status = False
            self.init_variables()

    def move_particles(self):
        self.restart_status = False
        cont = 0

        for particle in self.particles_from_collision:
            dx = (particle.original_pos.x - particle.pos.x)
            dy = (particle.original_pos.y - particle.pos.y)
            particle.pos.x += dx * self.move_particles_velocity
            particle.pos.y += dy * self.move_particles_velocity
            pygame.draw.circle(self.screen, particle.color, (particle.pos.x, particle.pos.y), particle.radius)
            if abs(dx) > 0.1 or abs(dy) > 0.1:
                cont+=1

        self.move_particles_velocity += 0.00001
        
        self.particle_index_to_create_final_image += self.removed_particles_incrementer
        self.removed_particles_incrementer += 2

        if self.particle_index_to_create_final_image > self.removed_particles_lenght-1:
            self.particle_index_to_create_final_image = self.removed_particles_lenght-1
            self.removed_particles_incrementer = 0

        for i in range(self.particle_index_to_create_final_image):
            particle = self.removed_particles[i]
            pygame.draw.circle(self.screen, particle.color, (particle.pos.x, particle.pos.y), particle.radius)
        
        if cont <= self.factor_to_restart:
            self.restart_status = True
            # Remove 30% das partículas aleatoriamente
            num_to_remove = int(len(self.particles_from_collision) * 0.30)
            particles_to_remove = random.sample(self.particles_from_collision, num_to_remove)
            for particle in particles_to_remove:
                particle.alive = False
                # self.particles_from_collision.remove(particle)

            for particle in self.particles_from_collision:
                particle.noise_offset_x = random.uniform(0, 1000)
                particle.noise_offset_y = random.uniform(0, 1000)
                particle.speed = random.uniform(2.5, 3.5)
                
                # Vetor de direção com base na distância do centro
                particle.center_x, particle.center_y = self.WIDTH / 2, self.HEIGHT / 2
                direction_angle = math.atan2(particle.pos.y - particle.center_y, particle.pos.x - particle.center_x)
                particle.direction_x = math.cos(direction_angle)
                particle.direction_y = math.sin(direction_angle)

    def get_image_paths(self):
        folder = 'final_images/'
        extensions = ('.png', '.jpg', '.jpeg')
        self.images_paths = [f for f in os.listdir(folder) if f.lower().endswith(extensions)]

            
    def create_final_image(self, final_image_path):
        image = Image.open(final_image_path)
        self.image = image

        image = image.resize((self.WIDTH//2,self.HEIGHT//2), Image.Resampling.LANCZOS)
        image_data = image.load()

        # Calcula a posição superior da imagem para centralizá-la na tela
        image_x = (self.WIDTH - image.width) // 2
        image_y = (self.HEIGHT - image.height) // 2

        # Calcula a posição inferior da imagem
        image_bottom = image_y + image.height

        # Armazena as posições para uso posterior
        self.image_bottom = image_bottom

        offset_x = (self.WIDTH - image.width) // 2
        offset_y = (self.HEIGHT - image.height) // 2
        for i in range(image.width):
            for j in range(image.height):
                color = image_data[i,j]
                if color != (0,0,0):
                    position = (i + offset_x, j + offset_y)
                    particle_generated = Particle(position, Vector2(0,0), 1, 1, color, False, False)
                    particle_generated.alive = False
                    r = random.randint(0,1)
                    r2 = random.randint(0,1)
                    if r == 1 and r2 == 1:
                        self.particles_from_collision.append(particle_generated)
                    else:
                        self.removed_particles.append(particle_generated)

        self.num_particles_from_collision = len(self.particles_from_collision)
        self.factor_to_restart = self.num_particles_from_collision * 0.80
        self.removed_particles_lenght = len(self.removed_particles)
        random.shuffle(self.removed_particles)
      

    def generate_images(self):
        self.images = []
        path = "output_images_resized"
        valid_images = [".jpg",".gif",".png",".tga"]
        for f in os.listdir(path):
            ext = os.path.splitext(f)[1]
            if ext.lower() in valid_images:
                self.images.append(pygame.image.load(os.path.join(path, f)))
                self.images.append(pygame.image.load(os.path.join(path, f)))

    def generate_points(self):
        experiment = doubleSlit()
        experiment.distance_to_screen = 10
        experiment.slit_dist = 3 
        experiment.clear_screen()
        if self.use_image:
            self.number_of_particles = len(self.images)
        experiment.electron_beam(num_electrons=self.number_of_particles)
        return experiment.get_positions()

    def transform_points(self, pontos_x, pontos_y, x_min, x_max, y_min, y_max, screen_width, screen_height):
        novos_pontos = []
        scale_x = screen_width - 10
        scale_y = screen_height - 10
        range_x = x_max - x_min
        range_y = y_max - y_min
        for i, e in enumerate(pontos_x):
            x = pontos_x[i]
            y = pontos_y[i]
            novo_x = ((x - x_min) / range_x) * scale_x
            novo_y = ((y - y_min) / range_y) * scale_y
            novos_pontos.append((novo_x, novo_y))
        return novos_pontos

    def add_particle(self, position, direction, speed, radius, color_or_image, use_image):
        self.particles.append(Particle(position, direction, speed, radius, color_or_image, use_image))

    def set_particles_speed(self, speed):
        for particle in self.particles:
            particle.speed = speed

    def send_sound_params(self, peak_width_1_target, peak_width_2_target, bands_target, factor):
        self.osc_client.send_message("peak_width_1", int(self.peak_width_1))
        self.osc_client.send_message("peak_width_2", int(self.peak_width_2))
        self.osc_client.send_message("bands", int(self.bands))
        
        self.peak_width_1 += (peak_width_1_target - self.peak_width_1) * factor
        self.peak_width_2 += (peak_width_2_target - self.peak_width_2) * factor
        self.bands += (bands_target - self.bands) * factor

    def draw_particles_final_image(self):
        self.move_particles()
        self.send_sound_params(1024, 1024, 532, 0.01)
        self.text_animation.draw_and_update(self.screen)

    def draw_generated_particles(self, index_next_to_alive):
        for i in range(index_next_to_alive):
            particle = self.particles_from_collision[i]
            particle.update_pos()
            self.draw_particle(particle)

    def create_generated_particles(self, result):
        self.to_alive_created_particle(result)
        x = random.uniform(result.pos.x - 20.0, result.pos.x + 20.0)
        y = random.uniform(result.pos.y - 20.0, result.pos.y + 20.0)
        self.to_alive_created_particle(Particle((x,y), result.dir, 1, 1, (0,0,0), False, False))
        x = random.uniform(result.pos.x - 40.0, result.pos.x + 40.0)
        y = random.uniform(result.pos.y - 40.0, result.pos.y + 40.0)
        self.to_alive_created_particle(Particle((x,y), result.dir, 1, 1, (0,0,0), False, False))
        x = random.uniform(result.pos.x - 80.0, result.pos.x + 80.0)
        y = random.uniform(result.pos.y - 80.0, result.pos.y + 80.0)
        self.to_alive_created_particle(Particle((x,y), result.dir, 1, 1, (0,0,0), False, False))
        self.to_alive_created_particle(result)

    def to_alive_created_particle(self, result):
        if self.index_next_to_alive < self.num_particles_from_collision:
            self.particles_from_collision[self.index_next_to_alive].pos = result.pos
            self.particles_from_collision[self.index_next_to_alive].dir = result.dir
            self.particles_from_collision[self.index_next_to_alive].speed = result.speed
            self.particles_from_collision[self.index_next_to_alive].radius = result.radius
            self.particles_from_collision[self.index_next_to_alive].alive = True
            self.index_next_to_alive += 1
        else:
            self.move_particle_status = True
            self.use_collision = False

    def should_create_generated_particles_from_collision(self, result):
        return result != None and not self.move_particle_status

    def handle_particle_collisions(self, particle):
        self.particles_manager.add_particle_to_grid(particle)
        i, j = self.particles_manager.get_particle_position_on_grid(particle)
        result = particle.guidance(self.particles_manager.grid[i][j], self.use_collision if self.face_detector.face_detected else False)
        if self.should_create_generated_particles_from_collision(result):
            self.create_generated_particles(result)

    def update_particle_position(self, particle):
        if self.wave_movement:
            update_wave_movement(self.timer, particle)
        else:
            particle.update_pos()

    def draw_particles(self):

        if self.restart_status:
            self.move_particles_restart()
            return
        
        if self.move_particle_status:
            self.draw_particles_final_image()
            return
        
        self.particles_manager.clear_grid()

        self.draw_generated_particles(self.index_next_to_alive)

        for particle in self.particles:
            self.update_particle_position(particle)
            self.draw_particle(particle)
            self.handle_particle_collisions(particle)
        
        self.timer += self.clock.get_time()
        if self.use_collision and self.face_detector.face_detected:
            self.time_transition_to_final_image_counter += self.timer//1000

        if self.time_transition_to_final_image_counter > self.time_transition_to_final_image: # esse trecho limita a geração de partículas a um tempo "time_transition_to_final_image". se passar disso, cria todas as partículas que faltam 
            qt = (int) ((len(self.particles_from_collision) - self.index_next_to_alive) // 2)
            for _ in range(qt):
                particle = random.choice(self.particles)
                x = particle.pos.x
                y = particle.pos.y
                self.to_alive_created_particle(Particle((x,y), particle.dir, 1, 1, (0,0,0), False, False))

    def draw_particle(self, particle):
          if particle.alive:
            if particle.use_image:
                self.screen.blit(particle.image, (particle.pos.x - particle.radius, particle.pos.y - particle.radius))
            else:
                pygame.draw.circle(self.screen, particle.color, (particle.pos.x, particle.pos.y), particle.radius)

    def create_particles(self):
        for _ in range(self.number_of_particles):
            self.create_particle()

    def create_particle(self):
        if len(self.particles) < self.number_of_particles:
            pos = self.points[len(self.particles)]
            angle = random.uniform(0, 2 * math.pi)  
            dir = Vector2(math.cos(angle), math.sin(angle)).normalize()
            speed = self.particles_speed if self.face_detector.face_detected else 0
            radius = self.particles_radius
            if self.use_image:
                self.add_particle(pos, dir, speed, radius, self.images[len(self.particles)], use_image=True)
            else:
                self.add_particle(pos, dir, speed, radius, (255, 255, 255), use_image=False)

    def handle_face_detection(self):
        self.face_detector.face_detected = self.face_detector.process_face_detection()
        if self.face_detector.face_detected:
            self.set_particles_speed(self.particles_speed)
        else:
            self.set_particles_speed(0)

    def should_create_particle(self):
        return len(self.particles) < self.number_of_particles
    
    def handle_keyboard_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def finish_simulation(self):
        pygame.quit()
        self.face_detector.cap.release()
        exit()

    def render(self):
        while self.running:

            dt = self.clock.tick(15) / 1000

            self.handle_keyboard_events()

            self.screen.blit(self.bg, (0, 0))

            if not self.face_detector.face_detected:
                self.handle_face_detection()

            if self.should_create_particle():
                self.create_particle()
                self.create_particle()
                self.create_particle()
            else:
                self.wave_movement = not self.face_detector.face_detected

            self.draw_particles()
            pygame.display.update()

        self.finish_simulation()

if __name__ == "__main__":
    simulation = ParticleSimulation()
    simulation.render()