import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
import numpy as np
import ctypes
import random
import math
import time
from PIL import Image
import os

# Inicialização do Pygame e contexto OpenGL
pygame.init()
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
print(f"Versão do OpenGL: {glGetString(GL_VERSION).decode()}")

# Compilação dos shaders
def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    # Verificação de erros de compilação
    result = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not result:
        error = glGetShaderInfoLog(shader)
        print(f"Erro ao compilar shader: {error.decode()}")
        glDeleteShader(shader)
        return None
    return shader

vertex_shader_source = '''
#version 330 core
layout(location = 0) in vec2 in_position;
layout(location = 1) in vec3 in_color;
out vec3 frag_color;
void main()
{
    gl_Position = vec4(in_position, 0.0, 1.0);
    frag_color = in_color;
    gl_PointSize = 2.0;
}
'''

fragment_shader_source = '''
#version 330 core
in vec3 frag_color;
out vec4 out_color;
void main()
{
    out_color = vec4(frag_color, 1.0);
}
'''

vertex_shader = compile_shader(vertex_shader_source, GL_VERTEX_SHADER)
fragment_shader = compile_shader(fragment_shader_source, GL_FRAGMENT_SHADER)

shader_program = glCreateProgram()
glAttachShader(shader_program, vertex_shader)
glAttachShader(shader_program, fragment_shader)
glLinkProgram(shader_program)

# Verificação de erros de linkagem
result = glGetProgramiv(shader_program, GL_LINK_STATUS)
if not result:
    print(glGetProgramInfoLog(shader_program))
    glDeleteProgram(shader_program)
    exit()
else:
    glUseProgram(shader_program)

# Classe Particle otimizada
class Particle:
    def __init__(self, position, direction, speed, radius, color):
        self.position = np.array(position, dtype=np.float32)
        self.direction = np.array(direction, dtype=np.float32)
        self.speed = speed
        self.radius = radius
        self.color = np.array(color, dtype=np.float32) / 255.0

    def update(self):
        self.position += self.direction * self.speed

# Criação das partículas
num_particles = 5000
particles = []
for _ in range(num_particles):
    position = [random.uniform(-1, 1), random.uniform(-1, 1)]
    angle = random.uniform(0, 2 * math.pi)
    direction = [math.cos(angle), math.sin(angle)]
    speed = 0.01
    color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    particles.append(Particle(position, direction, speed, 1, color))

# Criação dos VBOs e VAO
vao = glGenVertexArrays(1)
vbo_positions = glGenBuffers(1)
vbo_colors = glGenBuffers(1)

glBindVertexArray(vao)

# VBO para posições
glBindBuffer(GL_ARRAY_BUFFER, vbo_positions)
positions = np.array([p.position for p in particles], dtype=np.float32).flatten()
glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_DYNAMIC_DRAW)
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

# VBO para cores
glBindBuffer(GL_ARRAY_BUFFER, vbo_colors)
colors = np.array([p.color for p in particles], dtype=np.float32).flatten()
glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_DYNAMIC_DRAW)
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)

# Loop principal
running = True
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60) / 1000.0  # Delta time em segundos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Atualização das partículas
    for particle in particles:
        particle.update()
        # Condição de borda
        if particle.position[0] > 1 or particle.position[0] < -1:
            particle.direction[0] *= -1
        if particle.position[1] > 1 or particle.position[1] < -1:
            particle.direction[1] *= -1

    # Atualização dos VBOs
    positions = np.array([p.position for p in particles], dtype=np.float32).flatten()
    colors = np.array([p.color for p in particles], dtype=np.float32).flatten()

    glBindBuffer(GL_ARRAY_BUFFER, vbo_positions)
    glBufferSubData(GL_ARRAY_BUFFER, 0, positions.nbytes, positions)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_colors)
    glBufferSubData(GL_ARRAY_BUFFER, 0, colors.nbytes, colors)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    # Limpeza da tela
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Renderização
    glUseProgram(shader_program)
    glBindVertexArray(vao)
    glDrawArrays(GL_POINTS, 0, num_particles)
    glBindVertexArray(0)

    # Atualização da tela
    pygame.display.flip()

pygame.quit()
