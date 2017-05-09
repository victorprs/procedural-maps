import noise
import numpy

class NoiseHeightmap():
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
        height = numpy.zeros((max, max), numpy.uint16)
        for x in xrange(max):
            for y in xrange(max):
                value = NoiseHeightmap.normalize(noise.pnoise2(x / (frequency * octaves), y / (frequency * octaves), octaves))
                value = pow(value, exponent)
                height[x, y] = value * max_height
        return height
