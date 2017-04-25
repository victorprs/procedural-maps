from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from noise_heightmap import NoiseHeightmap

MAX = 512
DENSITY = 1.0

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # create GeomVertexFormat
        format = GeomVertexFormat.getV3c4()
        # create GeomVertexData
        vdata = GeomVertexData('name', format, Geom.UHStatic)
        # set the number of rows, which in this case is the number of vertices
        vdata.setNumRows(MAX * MAX)
        # create VertexWriter
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')

        # fill vertices
        height = NoiseHeightmap.noise_heightmap()
        for x in xrange(MAX):
            for y in xrange(MAX):
                vertex.addData3f(x, height[x,y], y)
                color.addData4f(.5, 1, 1, 1)
        
        # fill geoprimitive which are triangles
        triangles = GeomTriangles(Geom.UH_static)
        for y in xrange(MAX - 1):
            for x in xrange(MAX - 1):
                triangles.addVertices(y * MAX + x,
                                      (y + 1) * MAX + x,
                                      y * MAX + x + 1)

                triangles.addVertices(y * MAX + x + 1,
                                      (y + 1) * MAX + x,
                                      (y + 1) * MAX + x + 1)

        # specifics of panda3d, geom and geomnode and scene graph
        geom = Geom(vdata)
        geom.addPrimitive(triangles)
        
        node = GeomNode('gnode')
        node.addGeom(geom)
        
        nodePath = self.render.attachNewNode(node)


myApp = MyApp()
myApp.run()

exit(0)