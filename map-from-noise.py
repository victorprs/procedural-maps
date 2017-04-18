import noise
import numpy
from PIL import Image
import vtk

MAX = 512
OCTAVES = 4
FREQUENCY = 16.0 * OCTAVES
EXPONENT = 1.0


def normalize_to_8bit(value):
    return (value * 0.5 + 0.5) * 256


def normalize_to_16bit(value):
    return (value * 0.5 + 0.5) * 65536


def normalize(value):
    return value * 0.5 + 0.5


def noise_heightmap():
    height = numpy.zeros((MAX, MAX), numpy.uint8)
    for x in xrange(MAX):
        for y in xrange(MAX):
            value = normalize(noise.pnoise2(x / FREQUENCY, y / FREQUENCY, OCTAVES))
            value = pow(value, EXPONENT)
            height[x, y] = normalize_to_8bit(value)
    return height


heightmap = noise_heightmap()
# print (heightmap)

# img = Image.fromarray(heightmap, 'L')
# img.save('my.png')

# create a rendering window and renderer
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

# create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)


# create points
points = vtk.vtkPoints()
vertices = vtk.vtkCellArray()

for x in xrange(MAX):
    for y in xrange(MAX):
        pid = points.InsertNextPoint(x, heightmap[x,y], y)
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(pid)


# polydata object
polyData = vtk.vtkPolyData()
polyData.SetPoints(points)
polyData.SetVerts(vertices)



# mapper
mapper = vtk.vtkPolyDataMapper()
if vtk.VTK_MAJOR_VERSION <= 5:
    mapper.SetInput(polyData)
else:
    mapper.SetInputData(polyData)

# actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)
# actor.GetProperty().SetPointSize(10)

# assign actor to the renderer
ren.AddActor(actor)

# enable user interface interactor
iren.Initialize()
renWin.Render()
iren.Start()

exit(0)
