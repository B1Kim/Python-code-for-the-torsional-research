"""
liftBlockWithCoupledMass.py
Analyse the coupled mass impact on the U3  

"""

stiffDistance=900.00
depthOfStiff=300.0
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
densityProperties1 = (7850.0E-12,)
densityProperties2 = (0.0,)

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

stiffSketch=liftModel.ConstrainedSketch(name='stiffnessProfile', sheetSize=widthX)

for i in range(45):

    addDistance=(i+1)*stiffDistance
    xForStiffness = - widthX/2 + addDistance
    stiffSketch.Line(point1=(xForStiffness,- heightY/2),point2=(xForStiffness, heightY/2))

for j in range(9):
    addDistance=(j+1)*webFrameDistance/2
    yForWebFrame = - heightY/2 + addDistance
    stiffSketch.Line(point1=(- widthX/2,yForWebFrame),point2=(widthX/2, yForWebFrame))

f=block50D.faces.findAt((0,0,0),)
e=block50D.edges.findAt((0,heightY/2,0),)
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
deckSection=liftModel.HomogeneousShellSection(name='deckSection',material='deckSteel',thickness=10.0)
stfSection=liftModel.HomogeneousShellSection(name='stfSection',material='stfSteel',thickness=10.0)

# region=(block50D.faces,)

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

dispDataOfUpperRight = []
dispDataOfDownRight = []
reactionForcesOne = []
reactionForcesTwo = []
reactionForcesThree = []



for massPositionX in range(23):     ## 23

    for massPositionY in range(15):  ## 15

        # massPositionX=20
        # massPositionY=12
        massCoupleCoodination1=(stiffDistance*massPositionX, stiffDistance * massPositionY, 0.0)
        massCoupleCoodination2=(-stiffDistance*massPositionX, -stiffDistance*massPositionY, 0.0)

        import load

        # loads
        ## the gravity
        mdb.models['Block'].Gravity(name='gravity', createStepName='blocklifting', 
            comp3=-gravityConstant, distributionType=UNIFORM, field='') 


        ## the coupled force
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
        jobName = 'liftTask'+'_'+'X'+str(massPositionX)+'_'+'Y'+str(massPositionY)
        myJob = mdb.Job(name=jobName, model='Block',
            description='first susccess')
        # Wait for the job to complete.

        myJob.submit()
        myJob.waitForCompletion()

        from odbAccess import *
        import visualization
        myOdb = visualization.openOdb(path=jobName + '.odb')
        frame = myOdb.steps['blocklifting'].frames[-1]
        dispField = frame.fieldOutputs['U']
        reactionForces = frame.fieldOutputs['RF']


        upperRightNodes=myInstance.nodes.getClosest((widthX/2-900.0,heightY/2,0.0),)
        dispOfupperRightNode = dispField.values[upperRightNodes.label-1].data[2]
        dispDataOfUpperRight.append((stiffDistance*massPositionX, stiffDistance*massPositionY, 
                                    dispOfupperRightNode))

        downRightNodes=myInstance.nodes.getClosest((widthX/2-900.0,-heightY/2,0.0),)
        dispOfdownRightNode = dispField.values[downRightNodes.label-1].data[2]
        dispDataOfDownRight.append((stiffDistance*massPositionX, stiffDistance*massPositionY, 
                                    dispOfdownRightNode ))

        ## extract the Reaction Force 
        nodesPick=myInstance.nodes.getClosest(liftPointCoodinationOfMain1,)
        reactionForcesOne.append((stiffDistance*massPositionX, stiffDistance*massPositionY,
                                    reactionForces.values[nodesPick.label-1].data[2]))
        nodesPick=myInstance.nodes.getClosest(liftPointCoodinationOfMain2,)
        reactionForcesTwo.append((stiffDistance*massPositionX, stiffDistance*massPositionY,
                                    reactionForces.values[nodesPick.label-1].data[2]))
        nodesPick=myInstance.nodes.getClosest(liftPointCoodinationOfMain3,)
        reactionForcesThree.append((stiffDistance*massPositionX, stiffDistance*massPositionY,
                                    reactionForces.values[nodesPick.label-1].data[2]))




