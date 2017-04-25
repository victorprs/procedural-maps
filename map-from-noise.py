from noise_heightmap import NoiseHeightmap
from PIL import Image
import vtk

MAX = 512
DENSITY = 1.0

heightmap = NoiseHeightmap.noise_heightmap()
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

for y in xrange(MAX):
    for x in xrange(MAX):
        pid = points.InsertNextPoint(x, heightmap[x,y], y)
        # points.InsertNextPoint(x, heightmap[x,y], y)
        # vertices.InsertNextCell(1)
        # vertices.InsertCellPoint(pid)


triangles = vtk.vtkCellArray()
for y in xrange(MAX-1):
    for x in xrange(MAX-1):
        triangle = vtk.vtkTriangle()
        triangle.GetPointIds().SetId(0, y*MAX+x)
        triangle.GetPointIds().SetId(1, y*MAX+x+1)
        triangle.GetPointIds().SetId(2, (y+1)*MAX+x)
        triangles.InsertNextCell(triangle)

        triangle = vtk.vtkTriangle()
        triangle.GetPointIds().SetId(0, y*MAX+x+1)
        triangle.GetPointIds().SetId(1, (y+1)*MAX+x)
        triangle.GetPointIds().SetId(2, (y+1)*MAX+x+1)
        triangles.InsertNextCell(triangle)

# polydata object
polyData = vtk.vtkPolyData()
polyData.SetPoints(points)
polyData.SetPolys(triangles)
# polyData.SetVerts(vertices)



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
