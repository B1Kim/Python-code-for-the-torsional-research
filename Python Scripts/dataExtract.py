from odbAccess import *
import numpy as np
import visualization

myOdb = visualization.openOdb(path=jobName + '.odb')


frame = myOdb.steps['blocklifting'].frames[-1]
dispField = frame.fieldOutputs['U']
reactionForces = frame.fieldOutputs['RF']
reactionForces = frame.fieldOutputs['RF']
nodes=myInstance.nodes.getClosest(liftPointCoodinationOfMain1,)
reactionForcesOfLifting1=reactionForces.values[nodes.label-1].data[2]



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