import noise
import numpy
from PIL import Image

MAX = 256
OCTAVES = 4
FREQUENCY = 16.0 * OCTAVES


def normalize_to_8bit(value):
    return (value * 0.5 + 0.5) * 256


def normalize(value):
    return value * 0.5 + 0.5


def noise_heightmap():
    height = numpy.zeros((MAX, MAX), numpy.uint8)
    for x in xrange(MAX):
        for y in xrange(MAX):
            height[x, y] = normalize_to_8bit(noise.pnoise2(x / FREQUENCY, y / FREQUENCY, OCTAVES))
    return height


heightmap = noise_heightmap()
# print (heightmap)

img = Image.fromarray(heightmap, 'L')
img.save('my.png')

exit(0)
