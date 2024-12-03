"""
skewExample.py

This script performs a parameter study of element type versus 
skew angle. For more details, see Problem 2.3.4 in the 
Abaqus Benchmarks manual.

Before executing this script you must fetch the appropriate 
files: abaqus fetch job=skewExample
       abaqus fetch job=skewExampleUtils.py
"""

import part
import mesh
from mesh import S4, S8R, STANDARD, STRUCTURED
import job
from skewExampleUtils import getResults, createXYPlot

# Create a list of angle parameters and a list of
# element type parameters.

angles = [90, 80, 60, 40, 30]
elemTypeCodes = [S4, S8R]

# Open the model database.
openMdb('skew.cae')

model = mdb.models['Model-1']
part = model.parts['Plate']
feature = part.features['Shell planar-1']
assembly = model.rootAssembly
instance = assembly.instances['Plate-1']
job = mdb.jobs['skew']

allFaces = instance.faces
regions =(allFaces[0], allFaces[1], allFaces[2], allFaces[3])
assembly.setMeshControls(regions=regions,
    technique=STRUCTURED)
face1 = allFaces.findAt((0.,0.,0.), )
face2 = allFaces.findAt((0.,1.,0.), )
face3 = allFaces.findAt((1.,1.,0.), )
face4 = allFaces.findAt((1.,0.,0.), )
allVertices = instance.vertices
v1 = allVertices.findAt((0.,0.,0.), )
v2 = allVertices.findAt((0.,.5,0.), )
v3 = allVertices.findAt((0.,1.,0.), )
v4 = allVertices.findAt((.5,1.,0.), )
v5 = allVertices.findAt((1.,1.,0.), )
v6 = allVertices.findAt((1.,.5,0.), )
v7 = allVertices.findAt((1.,0.,0.), )
v8 = allVertices.findAt((.5,0.,0.), )
v9 = allVertices.findAt((.5,.5,0.), )
  
# Create a copy of the feature sketch to modify.

tmpSketch = model.ConstrainedSketch('tmp', feature.sketch)
v, d = tmpSketch.vertices, tmpSketch.dimensions

# Create some dictionaries to hold results. Seed the
# dictionaries with the theoretical results.

dispData, maxMomentData, minMomentData = {}, {}, {}
dispData['Theoretical'] = ((90, -.001478), (80, -.001409),
    (60, -0.000932), (40, -0.000349), (30, -0.000148))
maxMomentData['Theoretical'] = ((90, 0.0479), (80, 0.0486),
    (60, 0.0425), (40, 0.0281), (30, 0.0191))
minMomentData['Theoretical'] = ((90, 0.0479), (80, 0.0448),
    (60, 0.0333), (40, 0.0180), (30, 0.0108))
    
# Loop over the parameters to perform the parameter study.

for elemCode in elemTypeCodes:
  
    # Convert the element type codes to strings.
  
    elemName = repr(elemCode)
    dispData[elemName], maxMomentData[elemName], \
        minMomentData[elemName] = [], [], []

    # Set the element type.
    
    elemType = mesh.ElemType(elemCode=elemCode,
        elemLibrary=STANDARD)
    assembly.setElementType(regions=(instance.faces,), 
        elemTypes=(elemType,))
    
    for angle in angles:  
     
        # Skew the geometry and regenerate the mesh.
        assembly.deleteMesh(regions=(instance,))

        d[0].setValues(value=angle, )
        feature.setValues(sketch=tmpSketch)
        part.regenerate()
        assembly.regenerate()
        assembly.setLogicalCorners(
            region=face1, corners=(v1,v2,v9,v8))
        assembly.setLogicalCorners(
            region=face2, corners=(v2,v3,v4,v9))
        assembly.setLogicalCorners(
            region=face3, corners=(v9,v4,v5,v6))
        assembly.setLogicalCorners(
            region=face4, corners=(v8,v9,v6,v7))
        assembly.generateMesh(regions=(instance,))
        
        # Run the job, then process the results.
        
        job.submit()
        job.waitForCompletion()
        print 'Completed job for %s at %s degrees' % (elemName,
            angle)
        disp, maxMoment, minMoment = getResults()
        dispData[elemName].append((angle, disp))
        maxMomentData[elemName].append((angle, maxMoment))
        minMomentData[elemName].append((angle, minMoment))
        
# Plot the results.

createXYPlot((10,10), 'Skew 1', 'Displacement - 4x4 Mesh',
    dispData)
createXYPlot((160,10), 'Skew 2', 'Max Moment - 4x4 Mesh',
    maxMomentData)
createXYPlot((310,10), 'Skew 3', 'Min Moment - 4x4 Mesh',
    minMomentData)
