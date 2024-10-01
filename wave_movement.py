import math
from Particle import *

# Wave parameters
A = 10  # Wave amplitude
T = 1000  # Wave period (time for one complete cycle in milliseconds)
wavelength = 100 
time = 0
wave_movement_velocity = 0.2

def update_wave_movement(t, particle):
    x = particle.original_pos.x
    deslocamento = A * math.sin((2 * math.pi / T) * t - (2 * math.pi / wavelength) * x)
    particle.pos.x += deslocamento * wave_movement_velocity
