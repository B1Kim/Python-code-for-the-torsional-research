from abaqus import * 
from abaqusConstants import *
backwardCompatibility.setValues(includeDeprecated=True,
                                reportDeprecated=False)

testModel=mdb.Model(name='shell4R')

import part
mySketch=testModel.ConstrainedSketch(name='plate',sheetSize=1000)
mySketch.rectangle(point1=(0.0,0.0),point2=(1200.0,1200.0))
myPart=testModel.Part(name='plate',dimensionality=THREE_D,type=DEFORMABLE_BODY)
myPart.BaseShell(sketch=mySketch)
mdb.models['shell4R'].parts['plate'].features['Shell planar-1']
import material
mySteel=testModel.Material(name='Steel')
mySteel.Elastic(table=((209.E3, 0.3),) )
mdb.models['shell4R'].materials['Steel'].elastic
import section
mySection=testModel.HomogeneousShellSection(name='section',material='Steel',thickness=10)
allFaces=myPart.Set(name='allFaces',faces=myPart.faces)
myPart.SectionAssignment(region=allFaces,sectionName='section')
import assembly
myAssembly=testModel.rootAssembly
myInstance =myAssembly.Instance(name='plateInstance',part=myPart,dependent=OFF)
import mesh
elemType1 = mesh.ElemType(elemCode=S4R, elemLibrary=STANDARD, secondOrderAccuracy=OFF, hourglassControl=DEFAULT)
myAssembly.setElementType(regions=allFaces, elemTypes=(elemType1, ))
partInstances =(myAssembly.instances['plateInstance'], )
myAssembly.seedPartInstance(regions=partInstances, size=300, deviationFactor=0.1, minSizeFactor=0.1)
myAssembly.generateMesh(regions=partInstances)
import step 
testModel.StaticStep(name='test1', 
                    previous='Initial',
                    timePeriod=1.0, 
                    initialInc=0.1,
                    description='Lifting the block.')
mdb.models['shell4R'].FieldOutputRequest(name='F-Output-U', 
        createStepName='test1', variables=('U', 'S','MISES'), 
        frequency=LAST_INCREMENT, region=MODEL, exteriorOnly=OFF, 
        sectionPoints=DEFAULT, rebar=EXCLUDE)
import load
