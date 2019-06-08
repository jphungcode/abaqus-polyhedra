from abaqus import *
from abaqusConstants import *
import numpy as np
import os
import __main__

import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

def checkWire(index, wireSet):
	for i in wireSet:
		if i == index:
			return True
		else:
			return False

			
def isCollinear(point, pointA,pointB): #points are tuple
	MA = np.sqrt((point[0]-pointA[0])**2+(point[1]-pointA[1])**2+(point[2]-pointA[2])**2)
	BM = np.sqrt((pointB[0]-point[0])**2+(pointB[1]-point[1])**2+(pointB[2]-point[2])**2)
	BA = np.sqrt((pointB[0]-pointA[0])**2+(pointB[1]-pointA[1])**2+(pointB[2]-pointA[2])**2)
	if abs(MA+BM-BA) < 1e-9:
		return True
	else:
		return False


csvPath = r"/path" #path storing the polygon data
os.chdir(csvPath)

data = [];
convexHull = [];
data = np.genfromtxt('polygon1.csv', delimiter=',')
convexHull = np.genfromtxt('polygon1-hull.csv', delimiter=',')

# create coordinate reference and supress
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p.ReferencePoint(point=(0.0, 0.0, 0.0))	
p.features['RP'].suppress()

for item in data:
	p.DatumPointByCoordinate(coords=(item[0], item[1], item[2]))
	
d1 = p.datums;

# join datum for edges
for hull in convexHull:
	p.WirePolyLine(points=((d1[int(hull[0])+1], d1[int(hull[1])+1]),), mergeType=IMPRINT, meshable=ON)
	p.WirePolyLine(points=((d1[int(hull[1])+1], d1[int(hull[2])+1]),), mergeType=IMPRINT, meshable=ON)
	p.WirePolyLine(points=((d1[int(hull[2])+1], d1[int(hull[0])+1]),), mergeType=IMPRINT, meshable=ON)
	
eg = p.edges

# create faces
for p in convexHull:
	seq = []
	wireSet = []
	for edge in eg:
		point = edge.pointOn[0]
		if isCollinear(point, d1[int(p[0])+1].pointOn,d1[int(p[1])+1].pointOn):	
			if checkWire(1,wireSet):
				continue
			else:
				seq.append(edge)
				wireSet.append(1)
		if isCollinear(point, d1[int(p[1])+1].pointOn,d1[int(p[2])+1].pointOn):
			if checkWire(2,wireSet):
				continue
			else:
				seq.append(edge)
				wireSet.append(2)
		if isCollinear(point, d1[int(p[2])+1].pointOn,d1[int(p[0])+1].pointOn):
			if checkWire(3,wireSet):
				continue
			else:
				seq.append(edge)
				wireSet.append(3)
		if len(seq) == 3:
			p = mdb.models['Model-1'].parts['Part-1']
			p.CoverEdges(edgeList = seq, tryAnalytical=True)
			break
			
# create solid
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
p.AddCells(faceList = f)

