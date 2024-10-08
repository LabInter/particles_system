from pygame.math import Vector2
import math
import pygame
import random

# Pré-calcular os vetores correspondentes a 10 ângulos entre 0 e 2 * PI
ANGLE_COUNT = 10
PRECOMPUTED_DIRECTIONS = []

for i in range(ANGLE_COUNT):
    angle = (2 * math.pi * i) / ANGLE_COUNT
    direction = Vector2(math.cos(angle), math.sin(angle))
    PRECOMPUTED_DIRECTIONS.append(direction)

class Particle:

    __slots__ = [
        'pos', 'r', 'original_pos', 'dir', 'speed', 'radius', 'use_image', 'alive', 'collidable',
        'image', 'color', 'collisions_count',
        'noise_offset_x', 'noise_offset_y', 'direction_x', 'direction_y', 'center_x', 'center_y'
    ]

    def __init__(self, position, direction, speed, radius, color_or_image, use_image=False, collidable=True):
        self.pos = Vector2(position)
        self.original_pos = Vector2(position)
        self.dir = direction
        self.speed = speed
        self.radius = radius
        self.use_image = use_image
        self.alive = True
        self.collidable = collidable
        # self.angle = 0  # Ângulo para movimento de onda
        self.r = 50  # Raio da onda
        # self.wave_speed = 0.05  # Velocidade do movimento da onda
        if use_image:
            self.image = pygame.transform.scale(color_or_image, (2 * radius, 2 * radius))
        else:
            self.color = color_or_image
        # self.collision_status = False
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
                       return Particle(self.pos, self.dir, 1, 1, (255,255,0), False, False)
    
    def guidance(self, particles, use_collision):
        if self.alive: 
            if self.collidable:
                return self.check_collision(use_collision, particles)

    def boundary_update_dir(self, box):
        if self.alive:
            if not (box[0] + self.radius <= self.pos.x <= box[1] - self.radius):
                self.dir.x *= -1
            if not (box[2] + self.radius <= self.pos.y <= box[3] - self.radius):
                self.dir.y *= -1
    
    def increase_size(self):
        self.radius += 5
        if self.use_image:
            self.image = pygame.transform.scale(self.image, (2 * self.radius, 2 * self.radius))

    def remove_particle(self):
        self.alive = False

    def is_collided(self, particle):
        if self.alive and particle.alive:
            distance_squared = (self.pos - particle.pos).length_squared()
            radius_sum = self.radius + particle.radius
            return distance_squared <= radius_sum ** 2
        return False

    def update_pos(self):
        if not self.alive:
            return
        
        self.dir = random.choice(PRECOMPUTED_DIRECTIONS)
        self.pos += self.dir * self.speed
    
    def update_pos_dla(self):
        if self.alive:
            self.dir = Vector2(random.randint(-1,1), random.randint(-1,1))
            self.pos = self.pos + self.dir
            return self.dir
    
    def change_pos(self, x, y):
        self.pos = Vector2(x, y)

    def euclidean_distance(self, point_1, point_2):
        s = 0.0
        for i in range(len(point_1)):
            s += ((point_1[i] - point_2[i]) ** 2)
        return s ** 0.5
