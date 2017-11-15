from math import pi, sin, cos
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from fractal_heightmap import FractalHeightmap
import math

import numpy
from direct.task import Task

MAX = 512
DENSITY = 1.0

import time

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        texture = self.loader.loadTexture('terrain-color.jpg')
        # create GeomVertexFormat
        format = GeomVertexFormat.getV3n3t2()
        # create GeomVertexData
        vdata = GeomVertexData('name', format, Geom.UHStatic)
        # set the number of rows, which in this case is the number of vertices
        vdata.setNumRows(MAX * MAX)
        # create VertexWriter
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        texcoord = GeomVertexWriter(vdata, 'texcoord')
        
        init_time = time.clock()
        # fill vertices
        height = FractalHeightmap.dsm_heightmap(MAX)
        final_time = time.clock()
        print "time to generate heightmap:",final_time - init_time
        
        init_time = time.clock()
        maxSqrDistance = (0 - MAX/float(2)) **2 + (0 - MAX/float(2)) **2
        maxHeight = int(numpy.amax(height))
        minHeight = int(numpy.amin(height))
        maxHeightDiff = math.fabs(minHeight - maxHeight)
        for x in xrange(MAX):
            for y in xrange(MAX):
                vertex.addData3f(x, y, height[x, y])
                
                sqrDistance = (x - MAX / float(2)) ** 2 + (y - MAX / float(2)) ** 2
                heightDiff = math.fabs(int(height[x,y]) - maxHeight)
                humidity = .5 * (sqrDistance / maxSqrDistance) + .5 * (heightDiff / maxHeightDiff)
                temperature = heightDiff / maxHeightDiff

                texcoord.addData2f(temperature, humidity)
        final_time = time.clock()
        print "time to texturing:",final_time - init_time

        init_time = time.clock()
        for x in xrange(MAX):
            for y in xrange(MAX):
                if (x == MAX - 1 or y == MAX - 1 or x == 0 or y == 0):
                    normal.addData3f(1, 1, 1)
                    continue
                hL = int(height[x - 1, y])
                hR = int(height[x + 1, y])
                hD = int(height[x, y + 1])
                hU = int(height[x, y - 1])
                n = numpy.zeros(3)
                # n = numpy.zeros(3, numpy.int32)
                n[0] = hL - hR
                n[1] = hU - hD
                n[2] = 1
                norm = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
                n = [n[0] / norm, n[1] / norm, n[2] / norm]
                normal.addData3f(n[0], n[1], n[2])
        final_time = time.clock()
        print "time to normals:", final_time - init_time
        
        init_time = time.clock()
        # fill geoprimitive which are triangles
        triangles = GeomTriangles(Geom.UH_static)
        n_tri = 0
        for y in xrange(MAX - 1):
            for x in xrange(MAX - 1):
                n_tri = n_tri + 2
                triangles.addVertices(y * MAX + x,
                                      (y + 1) * MAX + x,
                                      y * MAX + x + 1)
                
                triangles.addVertices(y * MAX + x + 1,
                                      (y + 1) * MAX + x,
                                      (y + 1) * MAX + x + 1)
        final_time = time.clock()
        print "time to triangulate:",final_time - init_time
        print "# triangles = ", n_tri
        
        # specifics of panda3d, geom and geomnode and scene graph
        terrainGeom = Geom(vdata)
        terrainGeom.addPrimitive(triangles)
        
        terrainNode = GeomNode('gnode')
        terrainNode.addGeom(terrainGeom)
        
        terrainNP = self.render.attachNewNode(terrainNode)
        terrainNP.setPos(-MAX / 2, -10, -MAX / 2)
        terrainNP.setTexture(texture, 1)
        
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
        # self.directionalLight.showFrustum()
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

        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_confined)
        self.win.requestProperties(props)
        self.win.movePointer(0, int(800 / 2), int(600 / 2))
        
    def setKey(self, key, value):
        self.keyMap[key] = value

    def cameraControl(self, task):
        dt = globalClock.getDt()
        if (dt > .20):
            return task.cont
    
        if (self.mouseWatcherNode.hasMouse() == True):
            mpos = self.mouseWatcherNode.getMouse()
            if (mpos.getX() != 0 or mpos.getY() != 0):
                self.cameraModel.setH(self.cameraModel.getH() + mpos.getX() * -50)
                self.cameraModel.setP(self.cameraModel.getP() + mpos.getY() * 30)
            props = self.win.getProperties()
            self.win.movePointer(0,int(props.getXSize() / 2),int(props.getYSize() / 2))
    
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
        #
        #     self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        #
        # # Define a procedure to move the camera.
        # def spinCameraTask(self, task):
        #     angleDegrees = task.time * 6.0
        #     angleRadians = angleDegrees * (pi / 180.0)
        #     # self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        #     self.directionalLightNP.setHpr(0, angleDegrees, 0)
        #     return Task.cont


myApp = MyApp()
myApp.run()

exit(0)