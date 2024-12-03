"""
liftBlockWithCoupledMass.py
Analyse the coupled mass impact on the U3  

"""


from abaqus import * 
from abaqusConstants import *
backwardCompatibility.setValues(includeDeprecated=True,
                                reportDeprecated=False)


depthOfStiff=600.0 ## the first stringers from 1 to 5
depthOfWeb=2400.0
depthOflongTrans=1800.0 ## the second stringers from 5 to 10
thicknessOfStiff=10.0
thicknessOfDeck=10.0

gravityConstant = 10.e3
stiffDistance=900.00
webFrameDistance=stiffDistance*5
heightY=webFrameDistance*6
widthX=stiffDistance*46


liftPointCoodinationOfMain1=( stiffDistance*13,  0.0, 0.0)
liftPointCoodinationOfMain2=(-stiffDistance*10,  webFrameDistance*2, 0.0)
liftPointCoodinationOfMain3=(-stiffDistance*10, -webFrameDistance*2, 0.0)
massCoupleCoodination1=(stiffDistance*5, webFrameDistance*1, 0.0)
massCoupleCoodination2=(-stiffDistance*5, -webFrameDistance*1, 0.0)

elasticProperties = (209.E3, 0.3)
densityProperties1 = (7850.0E-12,)
densityProperties2 = (0.0,)


liftModel=mdb.Model(name='Block')


import part

deckSketch = liftModel.ConstrainedSketch(name='blockProfile',
    sheetSize=widthX)
deckSketch.rectangle(point1=(- widthX/2 ,- heightY/2),point2=(widthX/2, heightY/2))    
block50D = liftModel.Part(name='block', dimensionality=THREE_D,
    type=DEFORMABLE_BODY)

block50D.BaseShell(sketch=deckSketch)

stiffSketch=liftModel.ConstrainedSketch(name='stiffnessProfile', sheetSize=widthX)
for i in range(45):
    addDistance=(i+1)*stiffDistance
    xForStiffness = - widthX/2 + addDistance
    stiffSketch.Line(point1=(xForStiffness,- heightY/2),point2=(xForStiffness, heightY/2))

webFrameSketch=liftModel.ConstrainedSketch(name='webFrameProfile', sheetSize=widthX)
for j in range(5):
    addDistance=(j+1)*webFrameDistance
    yForWebFrame = - heightY/2 + addDistance
    webFrameSketch.Line(point1=(- widthX/2,yForWebFrame),point2=(widthX/2, yForWebFrame))
  

longTransSketch=liftModel.ConstrainedSketch(name='longTransProfile', sheetSize=widthX)
for k in range(6):
    addDistance=(15+k)*stiffDistance
    xForStiffness = - widthX/2 + addDistance
    longTransSketch.Line(point1=(xForStiffness,- heightY/2),point2=(xForStiffness, heightY/2))
    addDistance=(31-k)*stiffDistance
    xForStiffness = - widthX/2 + addDistance
    longTransSketch.Line(point1=(xForStiffness,- heightY/2),point2=(xForStiffness, heightY/2))

## longitical stringers
f=block50D.faces.findAt((1,1,0),)
e=block50D.edges.findAt((1,heightY/2,0),)

block50D.ShellExtrude(sketchPlane=f, sketchUpEdge=e, sketchPlaneSide=SIDE1, 
    sketchOrientation=TOP, sketch=stiffSketch, depth=depthOfStiff, flipExtrudeDirection=ON)
# ## longtrans bulkhead
f=block50D.faces.findAt((1,1,0),)
e=block50D.edges.findAt((1,heightY/2,0),)

block50D.ShellExtrude(sketchPlane=f, sketchUpEdge=e, 
    sketchPlaneSide=SIDE1, sketchOrientation=TOP, sketch=longTransSketch, depth=depthOflongTrans, 
    flipExtrudeDirection=ON)

## beams
f=block50D.faces.findAt((1,1,0),)
e=block50D.edges.findAt((1,heightY/2,0),)

block50D.ShellExtrude(sketchPlane=f, sketchUpEdge=e, 
    sketchPlaneSide=SIDE1, sketchOrientation=TOP, sketch=webFrameSketch, depth=depthOfWeb, 
    flipExtrudeDirection=ON)


import material
deckSteel = liftModel.Material(name='deckSteel')
deckSteel.Elastic(table=(elasticProperties, ) )
deckSteel.Density(table=(densityProperties1, ))
stfSteel = liftModel.Material(name='stfSteel')
stfSteel.Elastic(table=(elasticProperties, ) )
stfSteel.Density(table=(densityProperties2, ))

import section
allFaces=block50D.Set(name='allFaces',faces=block50D.faces)
deckFaces=block50D.Set(name='deckFaces',faces=block50D.faces.getByBoundingBox( zMin=-0.1,zMax=0.1))
stfFaces=block50D.SetByBoolean(name='stfFaces',operation=DIFFERENCE,sets=(allFaces,deckFaces,))
## thickness of the plate

deckSection=liftModel.HomogeneousShellSection(name='deckSection',material='deckSteel',thickness=thicknessOfDeck)
stfSection=liftModel.HomogeneousShellSection(name='stfSection',material='stfSteel',thickness=thicknessOfStiff)

block50D.SectionAssignment(region=deckFaces,sectionName='deckSection')
block50D.SectionAssignment(region=stfFaces,sectionName='stfSection')

import assembly
myAssembly = liftModel.rootAssembly
myInstance = myAssembly.Instance(name='blockInstance', part=block50D, dependent=OFF)

import mesh
region=((myInstance.faces,))
## element type
elemType1 = mesh.ElemType(elemCode=S4R, elemLibrary=STANDARD, 
    secondOrderAccuracy=OFF, hourglassControl=DEFAULT)
myAssembly.setElementType(regions=region, elemTypes=(elemType1, ))
partInstances =(myAssembly.instances['blockInstance'], )
myAssembly.seedPartInstance(regions=partInstances, size=stiffDistance/3, deviationFactor=0.1, 
    minSizeFactor=0.1)
myAssembly.generateMesh(regions=partInstances)
