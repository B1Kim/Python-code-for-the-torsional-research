"""
liftBlockWithCoupledMass.py
Analyse the coupled mass impact on the U3  

"""


from abaqus import * 
from abaqusConstants import *
backwardCompatibility.setValues(includeDeprecated=True,
                                reportDeprecated=False)


dispDataOfUpperRight=[]
dispDataOfDownRight=[]
dispDataOfUpperLeft=[]
dispDataOfDownLeft=[]

depthOfStiff=600.0
depthOfWeb=2400.0
depthOflongTrans=4800.0
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
  

# longTransSketch=liftModel.ConstrainedSketch(name='longTransProfile', sheetSize=widthX)
# addDistance=11*stiffDistance
# xForStiffness = - widthX/2 + addDistance
# longTransSketch.Line(point1=(xForStiffness,- heightY/2),point2=(xForStiffness, heightY/2))
# addDistance=35*stiffDistance
# xForStiffness = - widthX/2 + addDistance
# longTransSketch.Line(point1=(xForStiffness,- heightY/2),point2=(xForStiffness, heightY/2))


f=block50D.faces.findAt((1,1,0),)
e=block50D.edges.findAt((1,heightY/2,0),)

block50D.ShellExtrude(sketchPlane=f, sketchUpEdge=e, sketchPlaneSide=SIDE1, 
    sketchOrientation=TOP, sketch=stiffSketch, depth=depthOfStiff, flipExtrudeDirection=ON)

# f=block50D.faces.findAt((1,1,0),)
# e=block50D.edges.findAt((1,heightY/2,0),)

# block50D.ShellExtrude(sketchPlane=f, sketchUpEdge=e, 
#     sketchPlaneSide=SIDE1, sketchOrientation=TOP, sketch=longTransSketch, depth=depthOflongTrans, 
#     flipExtrudeDirection=ON)

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

import step 
liftModel.StaticStep(name='blocklifting', 
                            previous='Initial',
                            timePeriod=1.0, 
                            initialInc=0.1,
                            description='Lifting the block.')
mdb.models['Block'].FieldOutputRequest(name='F-Output-U', 
    createStepName='blocklifting', variables=('U', 'RF', 'S','MISES','MISESMAX','E'), 
    frequency=LAST_INCREMENT, region=MODEL, exteriorOnly=OFF, 
    sectionPoints=DEFAULT, rebar=EXCLUDE)

import load

# loads
## the gravity
mdb.models['Block'].Gravity(name='gravity', createStepName='blocklifting', 
            comp3=-gravityConstant, distributionType=UNIFORM, field='') 

# BC liftpoint sets
l1=myInstance.nodes.getClosest(liftPointCoodinationOfMain1,)
region = myAssembly.SetFromNodeLabels(name = 'liftpoint1', nodeLabels=( ('blockInstance', (l1.label,) ), ) )
mdb.models['Block'].DisplacementBC(name='BC-1', createStepName='Initial', 
            region=region, u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
            amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
l2=myInstance.nodes.getClosest(liftPointCoodinationOfMain2,)
region = myAssembly.SetFromNodeLabels(name = 'liftpoint2', nodeLabels=( ('blockInstance', (l2.label,) ), ) )
mdb.models['Block'].DisplacementBC(name='BC-2', createStepName='Initial', 
            region=region, u1=SET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
            amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

l3=myInstance.nodes.getClosest(liftPointCoodinationOfMain3,)
region = myAssembly.SetFromNodeLabels(name = 'liftpoint3', nodeLabels=( ('blockInstance', (l3.label,) ), ) )
mdb.models['Block'].DisplacementBC(name='BC-3', createStepName='Initial', 
            region=region, u1=SET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
            amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            
n1=myInstance.nodes.getClosest(massCoupleCoodination1,)
region=myAssembly.SetFromNodeLabels(name = 'massCouple1', nodeLabels=( ('blockInstance', (n1.label,) ), ) )
mdb.models['Block'].ConcentratedForce(name='massCouple1', 
    createStepName='blocklifting', region=region, cf3=-5000.0, 
    distributionType=UNIFORM, field='', localCsys=None)   
n2=myInstance.nodes.getClosest(massCoupleCoodination2,)
region=myAssembly.SetFromNodeLabels(name = 'massCouple2', nodeLabels=( ('blockInstance', (n2.label,) ), ) )
mdb.models['Block'].ConcentratedForce(name='massCouple2', 
    createStepName='blocklifting', region=region, cf3=-5000.0, 
    distributionType=UNIFORM, field='', localCsys=None)    


import job
jobName = 'Code-'+str(int(thicknessOfDeck))+'-'+str(int(thicknessOfStiff))+'-'+str(int(depthOfWeb))+'-'+str(int(depthOfStiff))+'-0-1'
myJob = mdb.Job(name=jobName, model='Block',
    description='first susccess')
# Wait for the job to complete.

myJob.submit()
myJob.waitForCompletion()

from odbAccess import *
import numpy as np
import visualization
myOdb = visualization.openOdb(path=jobName + '.odb')
frame = myOdb.steps['blocklifting'].frames[-1]
dispField = frame.fieldOutputs['U']

disDataUpper=np.zeros(45)
disDataDown=np.zeros(45)
disDataMiddle=np.zeros(45)


for i in range(45):
    nodesUpper=myInstance.nodes.getClosest((-widthX/2+900.0*(i+1),heightY/2,0.0),)
    disDataUpper[i]=dispField.values[nodesUpper.label-1].data[2]
    nodesMiddle=myInstance.nodes.getClosest((-widthX/2+900.0*(i+1),0.0,0.0),)
    disDataMiddle[i]=dispField.values[nodesMiddle.label-1].data[2]
    nodesDown=myInstance.nodes.getClosest((-widthX/2+900.0*(i+1),-heightY/2,0.0),)
    disDataDown[i]=dispField.values[nodesDown.label-1].data[2]    
    
    