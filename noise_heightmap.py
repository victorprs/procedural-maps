import noise
import numpy
import math
from PIL import Image

class NoiseHeightmap:

    @staticmethod
    def __normalize_to_8bit__(value):
        return (value * 0.5 + 0.5) * 256
    
    @staticmethod
    def __normalize_to_16bit__(value):
        return (value * 0.5 + 0.5) * 65536
    
    @staticmethod
    def normalize(value):
        return value * 0.5 + 0.5
    
    @staticmethod
    def noise_heightmap(max=512, octaves=4, frequency=16.0, exponent=1.0, max_height=255):
        height = numpy.zeros((max, max), numpy.uint8)
        for x in xrange(max):
            for y in xrange(max):
                value = NoiseHeightmap.normalize(
                    noise.pnoise2(x / (frequency * octaves), y / (frequency * octaves), octaves))
                value = pow(value, exponent)
                height[x, y] = value * max_height
        img = Image.fromarray(height, 'L')
        img.save('asdf.png')
        return height

    @staticmethod
    def noise_heightmap_from_points(n_points, octaves=4, frequency=16.0, exponent=1.0, max_height=255):
        new_points = math.ceil(math.sqrt(n_points)) ** 2
        print math.sqrt(new_points), 'x', math.sqrt(new_points)
        a = NoiseHeightmap.noise_heightmap(int(math.sqrt(new_points)), octaves, frequency, exponent, max_height)
        img = Image.fromarray(a, 'L')
        img.save('asdf.png')
        
        return a

    @staticmethod
    def height_from_coords(a_coords, octaves=4, frequency=16.0, exponent=1.0, max_height=255):
        a = []
        for i in xrange(a_coords.shape[0]):
            value = NoiseHeightmap.normalize(noise.pnoise2(a_coords[i][0] / (frequency * octaves), a_coords[i][1] / (frequency * octaves), octaves))
            value = pow(value, exponent) * max_height
            a.append(value)
        return a