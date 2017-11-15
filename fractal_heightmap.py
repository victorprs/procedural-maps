import math
import numpy
import random


class FractalHeightmap:
    @staticmethod
    def __normalize_to_8bit__(value):
        return (value * 0.5 + 0.5) * 256
    
    @staticmethod
    def __normalize_to_16bit__(value):
        return (value * 0.5 + 0.5) * 65536
    
    @staticmethod
    def normalize(value, min=-1.0, max=1.0):
        return (value - min) / (max - min)
    
    
    @staticmethod
    def dsm_heightmap(max=512, max_height=255):
        if not math.log(max, 2).is_integer():
            raise Exception(str(max) + " is not power of two")
        height = numpy.zeros((max+1, max+1))
        height[0,0]     = random.uniform(-1,1)
        height[0,max]   = random.uniform(-1,1)
        height[max,0]   = random.uniform(-1,1)
        height[max,max] = random.uniform(-1,1)
        
        side_length = max
        factor = 0.5
        while side_length >= 2:
            half_side = side_length / 2
            
            # square
            for x in xrange(0, max, side_length):
                for y in xrange(0, max, side_length):
                    sum  = height[x, y]
                    sum += height[x + side_length, y]
                    sum += height[x, y + side_length]
                    sum += height[x + side_length, y + side_length]
                    sum /= 4.0
                    sum += random.uniform(-1,1) * factor
                    
                    height[x + half_side, y + half_side] = sum
                    
            # diamond
            for x in xrange(0, max, half_side):
                for y in xrange((x + half_side) % side_length, max, side_length):
                    sum  = height[(x - half_side + max) % max, y]
                    sum += height[(x + half_side) % max, y]
                    sum += height[x, (y + half_side) % max]
                    sum += height[x, (y - half_side + max) % max]
                    sum /= 4.0
                    sum += random.uniform(-1,1) * factor
                    
                    height[x,y] = sum

                    if (x == 0):  height[max,y] = sum
                    if (y == 0):  height[x,max] = sum
                    
            side_length /= 2
            factor /= (1 + math.sqrt(5))/2
        
        array_max = numpy.amax(height)
        array_min = numpy.amin(height)
        # print (array_max)
        final_height = numpy.zeros((max+1, max+1))
        for x in xrange(0, max+1):
            for y in xrange(0, max+1):
                # print height[x,y]
                final_height[x,y] = FractalHeightmap.normalize(height[x,y], array_min, array_max) * max_height
                # print FractalHeightmap.normalize(height[x,y], 0, array_max)
        return final_height