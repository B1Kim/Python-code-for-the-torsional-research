from abaqus import *
import visualization

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getResults():

    """
    Retrieve the displacement
    """

    from visualization import ELEMENT_NODAL

    # Open the output database.
    
    odb = visualization.openOdb('skew.odb')
    centerNSet = odb.rootAssembly.nodeSets['CENTER']
    frame = odb.steps['Step-1'].frames[-1]
    
    # Retrieve Z-displacement at the center of the plate.
    
    dispField = frame.fieldOutputs['U']
    dispSubField = dispField.getSubset(region=centerNSet)
    disp = dispSubField.values[0].data[2]

    # Average the contribution from each element to the moment,
    # then calculate the minimum and maximum bending moment at
    # the center of the plate using Mohr's circle.
     
    momentField = frame.fieldOutputs['SM']
    momentSubField = momentField.getSubset(region=centerNSet, 
        position=ELEMENT_NODAL)
    m1, m2, m3 = 0, 0, 0
    for value in momentSubField.values:
        m1 = m1 + value.data[0]
        m2 = m2 + value.data[1]
        m3 = m3 + value.data[2]
    numElements = len(momentSubField.values)    
    m1 = m1 / numElements
    m2 = m2 / numElements
    m3 = m3 / numElements
    momentA = 0.5 * (abs(m1) + abs(m2))
    momentB = sqrt(0.25 * (m1 - m2)**2 + m3**2)
    maxMoment = momentA + momentB
    minMoment = momentA - momentB

    odb.close()
    
    return disp, maxMoment, minMoment