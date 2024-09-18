
import math
import random
import numpy as np
from OpenGL.GL import *

# Implementação simples de um vetor 2D para substituir pygame.math.Vector2
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        length = self.length()
        if length != 0:
            self.x /= length
            self.y /= length

class Particle:

    @staticmethod
    def precompute_directions(num_angles=36):
        """Pré-calcula as direções em um intervalo de 0 a 2 * PI."""
        Particle.directions = []
        for i in range(num_angles):
            angle = 2 * math.pi * i / num_angles
            Particle.directions.append(Vector2(math.cos(angle), math.sin(angle)))

    def __init__(self, position, direction, speed, radius, color_or_image, use_image=False, collidable=True):
        self.pos = Vector2(position[0], position[1])
        self.original_pos = Vector2(position[0], position[1])
        self.dir = direction
        self.speed = speed
        self.radius = radius
        self.use_image = use_image
        self.alive = True
        self.collidable = collidable
        self.angle = 0  # Ângulo para movimento de onda
        self.r = 50  # Raio da onda
        self.wave_speed = 0.05  # Velocidade do movimento da onda
        Particle.precompute_directions()
        
        # No PyOpenGL, vamos usar cor em vez de imagem por enquanto
        if not use_image:
            self.color = color_or_image
        self.collision_status = False
        self.collisions_count = 0

        self.noise_offset_x = 0
        self.noise_offset_y = 0
        self.direction_x = 0
        self.direction_y = 0
        self.center_x = 0
        self.center_y = 0

    def check_collision(self, use_collision, particles):
        if self.alive and self.collidable:
            if use_collision:
                for particle in particles:
                    if particle.collidable and particle.pos != self.pos and self.is_collided(particle):
                        self.collisions_count += 1
                        return Particle((self.pos.x, self.pos.y), self.dir, 1, 1, (255, 255, 0), False, False)

    def guidance(self, box, particles, use_collision):
        if self.alive:
            self.boundary_update_dir(box)
            if self.collidable:
                return self.check_collision(use_collision, particles)

    def boundary_update_dir(self, box):
        if self.alive:
            if self.pos.x <= box[0] + self.radius and self.dir.x < 0:
                self.dir.x *= -1
            elif self.pos.x >= box[1] - self.radius and self.dir.x > 0:
                self.dir.x *= -1
            if self.pos.y <= box[2] + self.radius and self.dir.y < 0:
                self.dir.y *= -1
            elif self.pos.y >= box[3] - self.radius and self.dir.y > 0:
                self.dir.y *= -1

    def increase_size(self):
        self.radius += 5

    def remove_particle(self):
        self.alive = False

    def is_collided(self, particle):
        return self.alive and particle.alive and self.euclidean_distance(self.pos, particle.pos) <= self.radius + particle.radius

    def update_pos(self):
        if self.alive:
            self.dir = random.choice(Particle.directions)
            self.pos += self.dir * self.speed

    def update_pos_dla(self):
        if self.alive:
            self.dir = Vector2(random.randint(-1, 1), random.randint(-1, 1))
            self.pos = self.pos + self.dir
            return self.dir

    def change_pos(self, x, y):
        self.pos = Vector2(x, y)

    def euclidean_distance(self, point_1, point_2):
        return math.sqrt((point_1.x - point_2.x) ** 2 + (point_1.y - point_2.y) ** 2)