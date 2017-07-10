import numpy as np
import scipy.spatial as sp
import matplotlib.pyplot as plt

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

# sp.voronoi_plot_2d(voronoi)
n_vertices = voronoi.points.shape[0] + new_vertices.shape[0]
# plt.show()
all_vertices = np.append(new_vertices, points, 0)


from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import math

from direct.task import Task

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        texture = self.loader.loadTexture('terrain-color.jpg')
        # create GeomVertexFormat
        format = GeomVertexFormat.getV3n3t2()
        # create GeomVertexData
        vdata = GeomVertexData('name', format, Geom.UHStatic)
        # set the number of rows, which in this case is the number of vertices
        vdata.setNumRows(n_vertices)
        # create VertexWriter
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        texcoord = GeomVertexWriter(vdata, 'texcoord')
        
        # fill vertices
        height_vertices = NoiseHeightmap.height_from_coords(all_vertices)
        
        maxSqrDistance = (0 - MAX/float(2)) **2 + (0 - MAX/float(2)) **2
        maxHeight = int(np.amax(height_vertices))
        minHeight = int(np.amin(height_vertices))
        maxHeightDiff = math.fabs(minHeight - maxHeight)
        for i in xrange(all_vertices.shape[0]):
            vertex.addData3f(all_vertices[i][0], all_vertices[i][1], height_vertices[i])
            
            sqrDistance = (all_vertices[i][0] - MAX / float(2)) ** 2 + (all_vertices[i][1] - MAX / float(2)) ** 2
            heightDiff = math.fabs(int(height_vertices[i]) - maxHeight)
            humidity = .5 * (sqrDistance / maxSqrDistance) + .5 * (heightDiff / maxHeightDiff)
            temperature = heightDiff / maxHeightDiff

            texcoord.addData2f(temperature, humidity)
        
        # fill geoprimitive which are triangles
        triangles = GeomTriangles(Geom.UH_static)
        
        normals = np.zeros((len(all_vertices), 3))
        
        for p_index in xrange(len(voronoi.point_region)):
            p_region_index = voronoi.point_region[p_index]
            region = voronoi.regions[p_region_index]
            for i in xrange(len(region)):
                vert_index1 = region[i]
                vert_index2 = region[(i+1) % len(region)]
                if vert_index1 > -1 and vert_index2 > -1 and not removed[vert_index1] and not removed[vert_index2]:
                    v1 = [all_vertices[new_indices[vert_index1]][0],
                          all_vertices[new_indices[vert_index1]][1],
                          height_vertices[new_indices[vert_index1]]]
                    v2 = [all_vertices[new_indices[vert_index2]][0],
                          all_vertices[new_indices[vert_index2]][1],
                          height_vertices[new_indices[vert_index2]]]
                    p = [all_vertices[len(new_vertices) + p_index][0],
                         all_vertices[len(new_vertices) + p_index][1],
                         height_vertices[len(new_vertices) + p_index]]
                    
                    cross_product = np.cross(np.subtract(v1,v2), np.subtract(v2,p))
                    if (cross_product[2] < 0): #inverte o sinal
                        cross_product *= -1
                    normals[new_indices[vert_index1]] += cross_product
                    normals[new_indices[vert_index2]] += cross_product
                    normals[len(new_vertices) + p_index] += cross_product
                    triangles.addVertices(new_indices[vert_index1],
                                          new_indices[vert_index2],
                                          len(new_vertices) + p_index)
                if (len(region) == 2):  # para nao repetir a combinacao quando forem apenas 2 vertices na regiao
                    break

        for i in xrange(all_vertices.shape[0]):
            norm = math.sqrt(normals[i][0] ** 2 + normals[i][1] ** 2 + normals[i][2] ** 2)
            if norm == 0: # no caso de ponto sem triangulos
                n = [0,0,0]
            else:
                n = [normals[i][0] / norm, normals[i][1] / norm, normals[i][2] / norm]
            normal.addData3f(n[0], n[1], n[2])
        
        # specifics of panda3d, geom and geomnode and scene graph
        terrainGeom = Geom(vdata)
        terrainGeom.addPrimitive(triangles)
        #
        terrainNode = GeomNode('gnode')
        terrainNode.addGeom(terrainGeom)
        
        terrainNP = self.render.attachNewNode(terrainNode)
        terrainNP.setPos(-MAX / 2, -10, -MAX / 2)
        terrainNP.setTexture(texture, 1)
        terrainNP.setTwoSided(True)
        # terrainNP.setShaderAuto()
        # terrainNP.setDepthOffset(1)
        
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
        # self.render.setRenderModeWireframe()
        #
        # directionalLightNP.setDepthOffset(1)
        
        
        self.trackball.node().setPos(0, 250, 100)

        self.disableMouse()

        self.cameraModel = self.loader.loadModel("models/camera")
        self.cameraModel.reparentTo(self.render)
        self.cameraModel.setPos(0, 15, 0)

        self.camera.reparentTo(self.cameraModel)
        self.camera.setY(self.camera, 5)

        self.keyMap = {"w": False, "s": False, "a": False, "d": False, }

        self.accept("w", self.setKey, ["w", True])
        self.accept("s", self.setKey, ["s", True])
        self.accept("a", self.setKey, ["a", True])
        self.accept("d", self.setKey, ["d", True])

        self.accept("w-up", self.setKey, ["w", False])
        self.accept("s-up", self.setKey, ["s", False])
        self.accept("a-up", self.setKey, ["a", False])
        self.accept("d-up", self.setKey, ["d", False])

        self.taskMgr.add(self.cameraControl, "Camera Control")

    def setKey(self, key, value):
        self.keyMap[key] = value

    def cameraControl(self, task):
        dt = globalClock.getDt()
        if (dt > .20):
            return task.cont
    
        if (self.mouseWatcherNode.hasMouse() == True):
            mpos = self.mouseWatcherNode.getMouse()
            self.camera.setP(mpos.getY() * 30)
            self.camera.setH(mpos.getX() * -50)
            if (mpos.getX() < 0.1 and mpos.getX() > -0.1):
                self.cameraModel.setH(self.cameraModel.getH())
            else:
                self.cameraModel.setH(self.cameraModel.getH() + mpos.getX() * -1)
    
        if (self.keyMap["w"] == True):
            self.cameraModel.setY(self.cameraModel, 100 * dt)
            print("camera moving forward")
        if (self.keyMap["s"] == True):
            self.cameraModel.setY(self.cameraModel, -100 * dt)
            print("camera moving backwards")
        if (self.keyMap["a"] == True):
            self.cameraModel.setX(self.cameraModel, -100 * dt)
            print("camera moving left")
        if (self.keyMap["d"] == True):
            self.cameraModel.setX(self.cameraModel, 100 * dt)
            print("camera moving right")
        return task.cont

    def moveCamera(self):
        print self.camera.getPos()
        self.camera.setPos(self.camera.getPos[0] - 1, self.camera.getPos[1], self.camera.getPos[2])
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