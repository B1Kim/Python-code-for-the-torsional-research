
"""
skewExampleUtils.py

Utilities for the scripting tutorial Skew Example.
"""

from abaqus import *
import visualization

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getResults():

    """
    Retrieve the displacement and calculate the minimum 
    and maximum bending moment at the center of plate.
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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def createXYPlot(vpOrigin, vpName, plotName, data):
    
    """
    Display curves of theoretical and computed results in
    a new viewport.
    """

    from visualization import  USER_DEFINED
    
    vp = session.Viewport(name=vpName, origin=vpOrigin, 
        width=150, height=100)
    xyPlot = session.XYPlot(plotName)
    chart = xyPlot.charts.values()[0]
    curveList = []
    for elemName, xyValues in sorted(data.items()):
        xyData = session.XYData(elemName, xyValues)
        curve = session.Curve(xyData)
        curveList.append(curve)
    chart.setValues(curvesToPlot=curveList)
    chart.axes1[0].axisData.setValues(useSystemTitle=False,title='Skew Angle')
    chart.axes2[0].axisData.setValues(useSystemTitle=False,title=plotName)
    vp.setValues(displayedObject=xyPlot)
   
     