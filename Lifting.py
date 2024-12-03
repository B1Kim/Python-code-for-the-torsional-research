"""
Lifting.py

"""

stiffDistance=900.00
depthOfStiff=500.0
gravityConstant = 10.e3

webFrameDistance=stiffDistance*6
heightY=webFrameDistance*5
widthX=stiffDistance*46


liftPointCoodinationOfMain1=( stiffDistance*13,  0.0, 0.0)
liftPointCoodinationOfMain2=(-stiffDistance*10,  webFrameDistance*1.5, 0.0)
liftPointCoodinationOfMain3=(-stiffDistance*10, -webFrameDistance*1.5, 0.0)
massCoupleCoodination1=(stiffDistance*10, webFrameDistance*1, 0.0)
massCoupleCoodination2=(-stiffDistance*10, -webFrameDistance*1, 0.0)
elasticProperties = (209.E3, 0.3)
densityProperties = (7850.0E-12,)


import string
from abaqus import *
from abaqusConstants import *
backwardCompatibility.setValues(includeDeprecated=True,
                                reportDeprecated=False)

liftModel=mdb.Model(name='Block')
myViewport = session.Viewport(name='Block Lifting Analysis',
              origin=(40, 40), width=100.00, height=100.00)

import part
## deck structure part
deckSketch = liftModel.ConstrainedSketch(name='blockProfile',
    sheetSize=widthX)
deckSketch.rectangle(point1=(- widthX/2 ,- heightY/2),point2=(widthX/2, heightY/2))    
block50D = liftModel.Part(name='block', dimensionality=THREE_D,
    type=DEFORMABLE_BODY)

block50D.BaseShell(sketch=deckSketch)
f=block50D.faces.findAt((0,0,0),)
e=block50D.edges.findAt((0,heightY/2,0),)
stiffSketch=liftModel.ConstrainedSketch(name='stiffnessProfile', sheetSize=widthX)

for i in range(45):

    addDistance=(i+1)*stiffDistance
    xForStiffness = - widthX/2 + addDistance
    stiffSketch.Line(point1=(xForStiffness,- heightY/2),point2=(xForStiffness, heightY/2))
for j in range(9):
    addDistance=(j+1)*webFrameDistance/2
    yForWebFrame = - heightY/2 + addDistance
    stiffSketch.Line(point1=(- widthX/2,yForWebFrame),point2=(widthX/2, yForWebFrame))

block50D.ShellExtrude(sketchPlane=f, sketchUpEdge=e, sketchPlaneSide=SIDE1, 
    sketchOrientation=TOP, sketch=stiffSketch, depth=depthOfStiff, flipExtrudeDirection=ON)
# liftpoint sets
pickPoint=block50D.vertices.findAt((liftPointCoodinationOfMain1,))
block50D.Set(vertices=pickPoint, name='liftpoint1')
pickPoint=block50D.vertices.findAt((liftPointCoodinationOfMain2,))
block50D.Set(vertices=pickPoint, name='liftpoint2')
pickPoint=block50D.vertices.findAt((liftPointCoodinationOfMain3,))
block50D.Set(vertices=pickPoint, name='liftpoint3')
pickPoint=block50D.vertices.findAt(((0.0,0.0,0.0),))
block50D.Set(vertices=pickPoint, name='massMiddle')

import material
mySteel = liftModel.Material(name='Steel')
mySteel.Elastic(table=(elasticProperties, ) )
mySteel.Density(table=(densityProperties, ))

import section
deckSection=liftModel.HomogeneousShellSection(name='deckSection',material='Steel',thickness=10.0)
region=(block50D.faces,)
block50D.SectionAssignment(region=region,
                           sectionName='deckSection')

import assembly
myAssembly = liftModel.rootAssembly
myInstance = myAssembly.Instance(name='blockInstance', part=block50D, dependent=OFF)

import mesh
region=((myInstance.faces,))
elemType1 = mesh.ElemType(elemCode=S4R, elemLibrary=STANDARD, 
    secondOrderAccuracy=OFF, hourglassControl=DEFAULT)
elemType2 = mesh.ElemType(elemCode=S3, elemLibrary=STANDARD)
myAssembly.setElementType(regions=region, elemTypes=(elemType1, elemType2))
partInstances =(myAssembly.instances['blockInstance'], )
myAssembly.seedPartInstance(regions=partInstances, size=900.0, deviationFactor=0.1, 
    minSizeFactor=0.1)
myAssembly.generateMesh(regions=partInstances)


for massPositionX in range(22)
    for massPositionY in range(14)

        massCoupleCoodination1=(stiffDistance*massPositionX, stiffDistance * massPositionY, 0.0)
        massCoupleCoodination2=(-stiffDistance*massPositionX, -stiffDistance*massPositionY, 0.0)

        import step 
        liftModel.StaticStep(name='blocklifting', 
                            previous='Initial',
                            timePeriod=1.0, 
                            initialInc=0.1,
                            description='Lifting the block.')
        import load

        # loads
        mdb.models['Block'].Gravity(name='gravity', createStepName='blocklifting', 
            comp3=-gravityConstant, distributionType=UNIFORM, field='') 
        region = myInstance.nodes.getClosest((massCoupleCoodination1,))
        mdb.models['Block'].ConcentratedForce(name='massCouple1', 
            createStepName='blocklifting', region=region, cf3=-5000.0, 
            distributionType=UNIFORM, field='', localCsys=None)   
        region = myInstance.nodes.getClosest((massCoupleCoodination2,))
        mdb.models['Block'].ConcentratedForce(name='massCouple2', 
            createStepName='blocklifting', region=region, cf3=-5000.0, 
            distributionType=UNIFORM, field='', localCsys=None)    
        #BC
        region = myAssembly.instances['blockInstance'].sets['liftpoint1']
        mdb.models['Block'].DisplacementBC(name='BC-1', createStepName='Initial', 
            region=region, u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
            amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        region = myAssembly.instances['blockInstance'].sets['liftpoint2']
        mdb.models['Block'].DisplacementBC(name='BC-2', createStepName='Initial', 
            region=region, u1=SET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
            amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        region = myAssembly.instances['blockInstance'].sets['liftpoint3']
        mdb.models['Block'].DisplacementBC(name='BC-3', createStepName='Initial', 
            region=region, u1=SET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
            amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

        import job
        jobName = 'liftTask'+'_'+'X'+string(massPositionX)+'_'+'Y'+string(massPositionY)
        myJob = mdb.Job(name=jobName, model='Block',
            description='first susccess')
        # Wait for the job to complete.

        myJob.submit()
        myJob.waitForCompletion()


import visualization

# Open the output database and display a
# default contour plot.

myOdb = visualization.openOdb(path=jobName + '.odb')
myViewport.setValues(displayedObject=myOdb)
myViewport.odbDisplay.display.setValues(plotState=CONTOURS_ON_DEF)
myViewport.odbDisplay.commonOptions.setValues(renderStyle=FILLED)




# session.printToFile(fileName='contourPlot', format=PNG,
#     canvasObjects=(myViewport,)) 