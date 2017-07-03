import numpy as np
import scipy.spatial as sp
import matplotlib.pyplot as plt
from nose.config import all_config_files

from noise_heightmap import NoiseHeightmap

n_points=10000
MAX = 512

# points = np.random.randint(0, MAX, (n_points, 2))
points = np.random.rand(n_points, 2) * MAX
voronoi = sp.Voronoi(points)
to_remove = []
removed = []
new_indices = []
j = 0
for i in xrange(voronoi.vertices.shape[0]):
    if (voronoi.vertices[i][0] < 0 or
        voronoi.vertices[i][0] > MAX or
        voronoi.vertices[i][1] < 0 or
        voronoi.vertices[i][1] > MAX):
        to_remove.append(i)
        removed.append(True)
        new_indices.append(-1)
    else:
        removed.append(False)
        new_indices.append(j)
        j = j + 1
new_vertices = np.delete(voronoi.vertices, to_remove, 0)

# print 'removed', to_remove
# print voronoi.vertices
# print removed
# sp.voronoi_plot_2d(voronoi)
# print "n of vertices: ", (voronoi.points.shape[0] + new_vertices.shape[0])
n_vertices = voronoi.points.shape[0] + new_vertices.shape[0]

# print voronoi.points
# print voronoi.vertices

# plt.show()
all_vertices = np.append(new_vertices, points, 0)


from math import pi, sin, cos
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import math

import numpy
from direct.task import Task

DENSITY = 1.0




class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # create GeomVertexFormat
        # format = GeomVertexFormat.getV3n3c4()
        format = GeomVertexFormat.getV3c4()
        # create GeomVertexData
        vdata = GeomVertexData('name', format, Geom.UHStatic)
        # set the number of rows, which in this case is the number of vertices
        vdata.setNumRows(n_vertices)
        # create VertexWriter
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        
        # fill vertices
        # height = NoiseHeightmap.noise_heightmap_from_points(n_vertices)
        height_vertices = NoiseHeightmap.height_from_coords(all_vertices)
        
        for i in xrange(all_vertices.shape[0]):
            vertex.addData3f(all_vertices[i][0], all_vertices[i][1], height_vertices[i])
            color.addData4f(.5, 1, 1, 1)
        # for i in xrange(voronoi.points.shape[0]):
        #     vertex.addData3f(voronoi.points[i][0], voronoi.points[i][1], height[voronoi.points[i][0], voronoi.points[i][1]])
        #     color.addData4f(.5, 1, 1, 1)

        # for i in xrange(all_vertices.shape[0]):
        #     if (all_vertices[i][0] == MAX - 1 or all_vertices[i][1] == MAX - 1 or all_vertices[i][0] == 0 or all_vertices[i][1] == 0):
        #         normal.addData3f(1, 1, 1)
        #         continue
        #     hL = int(height[new_vertices[i][0] - 1, new_vertices[i][1]])
        #     hR = int(height[new_vertices[i][0] + 1, new_vertices[i][1]])
        #     hD = int(height[new_vertices[i][0], new_vertices[i][1] + 1])
        #     hU = int(height[new_vertices[i][0], new_vertices[i][1] - 1])
        #     n = numpy.zeros(3, numpy.int32)
        #     n[0] = hL - hR
        #     n[1] = hU - hD
        #     n[2] = 1
        #     norm = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
        #     n = [n[0] / norm, n[1] / norm, n[2] / norm]
        #     normal.addData3f(n[0], n[1], n[2])

        # for i in xrange(voronoi.points.shape[0]):
        #     if (voronoi.points[i][0] == MAX - 1 or voronoi.points[i][1] == MAX - 1 or voronoi.points[i][0] == 0 or voronoi.points[i][1] == 0):
        #         normal.addData3f(1, 1, 1)
        #         continue
        #     hL = int(height[voronoi.points[i][0] - 1, voronoi.points[i][1]])
        #     hR = int(height[voronoi.points[i][0] + 1, voronoi.points[i][1]])
        #     hD = int(height[voronoi.points[i][0], voronoi.points[i][1] + 1])
        #     hU = int(height[voronoi.points[i][0], voronoi.points[i][1] - 1])
        #     n = numpy.zeros(3, numpy.int32)
        #     n[0] = hL - hR
        #     n[1] = hU - hD
        #     n[2] = 1
        #     norm = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
        #     n = [n[0] / norm, n[1] / norm, n[2] / norm]
        #     normal.addData3f(n[0], n[1], n[2])
        
        # fill geoprimitive which are triangles
        triangles = GeomTriangles(Geom.UH_static)
        
        for p_index in xrange(len(voronoi.point_region)):
            p_region_index = voronoi.point_region[p_index]
            region = voronoi.regions[p_region_index]
            for i in xrange(len(region)):
                vert_index1 = region[i]
                vert_index2 = region[(i+1) % len(region)]
                if vert_index1 > -1 and vert_index2 > -1 and not removed[vert_index1] and not removed[vert_index2]:
                    triangles.addVertices(new_indices[vert_index1],
                                          new_indices[vert_index2],
                                          len(new_vertices) + p_index)
        
        # specifics of panda3d, geom and geomnode and scene graph
        terrainGeom = Geom(vdata)
        terrainGeom.addPrimitive(triangles)
        #
        terrainNode = GeomNode('gnode')
        terrainNode.addGeom(terrainGeom)
        
        terrainNP = self.render.attachNewNode(terrainNode)
        terrainNP.setPos(-MAX / 2, -10, -MAX / 2)
        terrainNP.setTwoSided(True)
        terrainNP.setShaderAuto()
        terrainNP.setDepthOffset(1)
        
        # ambient light
        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        ambientLightNP = self.render.attachNewNode(ambientLight)
        self.render.setLight(ambientLightNP)
        
        # directional light pointing to object
        self.directionalLight = DirectionalLight('directionalLight')
        self.directionalLight.setColor(Vec4(.8, .8, .8, 1))
        # self.directionalLight.getLens().setFov(90)
        self.directionalLight.setShadowCaster(True, 4096, 4096)
        self.directionalLight.getLens().setNearFar(.1, 1000)
        self.directionalLight.showFrustum()
        self.directionalLightNP = self.render.attachNewNode(self.directionalLight)
        self.directionalLightNP.setPos(20, 20, 100)
        self.directionalLightNP.lookAt(terrainNP)
        self.render.setLight(self.directionalLightNP)
        #
        # Enable the shader generator for the receiving nodes
        self.render.setShaderAuto()
        #
        # directionalLightNP.setDepthOffset(1)
        
        
        self.trackball.node().setPos(0, 250, 100)
        # self.trackball.node().setHpr()

        # self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

    # Define a procedure to move the camera.
    # def spinCameraTask(self, task):
    #     angleDegrees = task.time * 6.0
    #     angleRadians = angleDegrees * (pi / 180.0)
    #     # self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
    #     self.directionalLightNP.setHpr(0, angleDegrees, 0)
    #     return Task.cont


myApp = MyApp()
myApp.run()

exit(0)