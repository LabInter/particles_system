import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
import numpy as np
import ctypes

# Inicialização do Pygame e contexto OpenGL
pygame.init()
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

display = (1870, 1200)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

print(f"Versão do OpenGL: {glGetString(GL_VERSION).decode()}")

# (Restante do código permanece o mesmo)


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
layout(location = 0) in vec3 in_position;
uniform mat4 projection;
uniform mat4 view;
void main()
{
    gl_Position = projection * view * vec4(in_position, 1.0);
    gl_PointSize = 3.0;
}
'''

fragment_shader_source = '''
#version 330 core
out vec4 frag_color;
void main()
{
    frag_color = vec4(1.0, 0.5, 0.0, 1.0);
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
else:
    glUseProgram(shader_program)

# Criação dos dados das partículas
num_particles = 200000
positions = np.random.uniform(-1, 1, (num_particles, 3)).astype(np.float32)
velocities = np.random.uniform(-0.005, 0.005, (num_particles, 3)).astype(np.float32)

# Criação do VBO e VAO
vao = glGenVertexArrays(1)
vbo = glGenBuffers(1)

glBindVertexArray(vao)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_DYNAMIC_DRAW)
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))
glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)

# Configuração das matrizes de projeção e visualização
projection = np.identity(4, dtype=np.float32)
view = np.identity(4, dtype=np.float32)

# Loop principal
running = True
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60) / 1000.0  # Delta time em segundos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Atualização das posições das partículas
    positions += velocities
    # Condição de borda
    positions = np.where(positions > 1, -1, positions)
    positions = np.where(positions < -1, 1, positions)

    # Atualização do VBO
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferSubData(GL_ARRAY_BUFFER, 0, positions.nbytes, positions)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    # Limpeza da tela
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Uso do programa shader
    glUseProgram(shader_program)

    # Passagem das matrizes uniformes
    projection_location = glGetUniformLocation(shader_program, 'projection')
    view_location = glGetUniformLocation(shader_program, 'view')
    glUniformMatrix4fv(projection_location, 1, GL_FALSE, projection)
    glUniformMatrix4fv(view_location, 1, GL_FALSE, view)

    # Desenho das partículas
    glBindVertexArray(vao)
    glDrawArrays(GL_POINTS, 0, num_particles)
    glBindVertexArray(0)

    # Atualização da tela
    pygame.display.flip()

pygame.quit()
