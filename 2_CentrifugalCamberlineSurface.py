# Script creates a 3D average surface of a blade

class ModelOfBlade3D:
	def __init__(self, obj):
		obj.Proxy = self
		obj.addProperty("App::PropertyFloat", "AngleBeta1Shroud", "Angles of a Shroud streamline", "Inlet angle").AngleBeta1Shroud=15
		obj.addProperty("App::PropertyFloat", "AngleBeta2Shroud", "Angles of a Shroud streamline", "Outlet angle").AngleBeta2Shroud=25
		obj.addProperty("App::PropertyVector", "AngleBetaPoint1Shroud", "Angles of a Shroud streamline", "Point of a B-spline, z-coodrinate non active").AngleBetaPoint1Shroud=(40,18,0)
		obj.addProperty("App::PropertyVector", "AngleBetaPoint2Shroud", "Angles of a Shroud streamline", "Point of a B-spline, z-coodrinate non active").AngleBetaPoint2Shroud=(75,22.5,0)
		obj.addProperty("App::PropertyBool", "AnglesChartShroud", "Angles of a Shroud streamline", "It is shows chart angle Beta-Streamline").AnglesChartShroud=False

		obj.addProperty("App::PropertyFloat", "AngleBeta1Hub", "Angles of a Hub streamline", "Inlet angle").AngleBeta1Hub=32
		obj.addProperty("App::PropertyFloat", "AngleBeta2Hub", "Angles of a Hub streamline", "Outlet angle").AngleBeta2Hub=25
		obj.addProperty("App::PropertyVector", "AngleBetaPoint1Hub", "Angles of a Hub streamline", "Point of a B-spline, z-coodrinate non active").AngleBetaPoint1Hub=(40,29,0)
		obj.addProperty("App::PropertyVector", "AngleBetaPoint2Hub", "Angles of a Hub streamline", "Point of a B-spline, z-coodrinate non active").AngleBetaPoint2Hub=(75,27,0)
		obj.addProperty("App::PropertyBool", "AnglesChartHub", "Angles of a Hub streamline", "It is shows chart angle Beta-Streamline").AnglesChartShroud=False

		obj.addProperty("App::PropertyFloat", "AngleBeta1Ave", "Angles of an Average streamline (when Cylindrical blade = False)").AngleBeta1Ave=26
		obj.addProperty("App::PropertyFloat", "AngleBeta2Ave", "Angles of an Average streamline (when Cylindrical blade = False)").AngleBeta2Ave=25
		obj.addProperty("App::PropertyVector", "AngleBetaPoint1Ave", "Angles of an Average streamline (when Cylindrical blade = False)").AngleBetaPoint1Ave=(40,25.5,0)
		obj.addProperty("App::PropertyVector", "AngleBetaPoint2Ave", "Angles of an Average streamline (when Cylindrical blade = False)").AngleBetaPoint2Ave=(75,25,0)
		obj.addProperty("App::PropertyBool", "AnglesChartAverage", "Angles of an Average streamline (when Cylindrical blade = False)").AnglesChartAverage=False
		obj.addProperty("App::PropertyInteger", "N", "Number of the calculation points").N=1000
	
	def execute (self,obj):
		import  Part, FreeCAD
		import numpy as np
		import matplotlib.pyplot as plt

		N=obj.N
		Mer=FreeCAD.ActiveDocument.getObject("Meridional")

		shroudEdge = Mer.Shape.Edges[3]
		shroudEdgeDiscret = shroudEdge.discretize(Number = N)
		shroudEdgeDiscret.append(shroudEdge.lastVertex().Point)

		hubEdge = Mer.Shape.Edges[7]
		hubEdgeDiscret = hubEdge.discretize(Number = N)
		hubEdgeDiscret.append(hubEdge.lastVertex().Point)

		N = len(shroudEdgeDiscret)

##### THIS IS FUNCTION FOR CREATION OF A STREAMLINES FROM MERIDIONAL PLAN ###############################################
		def streamlineBlade (AngleBeta1, AngleBetaPoint1, AngleBetaPoint2, AngleBeta2, DiscretEdgeOfMeridional):
		
			# Creation of a Beta angle curve
			betaPoints = [FreeCAD.Vector(0, AngleBeta1, 0), AngleBetaPoint1, AngleBetaPoint2 ,FreeCAD.Vector(100, AngleBeta2, 0)]
			betaCurve = Part.BSplineCurve()
			betaCurve.interpolate(betaPoints)
			betaCurveDiscret = []
			for i in range (1, (N+1), 1):
				vector_line1 = FreeCAD.Vector(float(i)/(float(N)/100.), -180, 0)
				vector_line2 = FreeCAD.Vector(float(i)/(float(N)/100.), 180, 0)
				line = Part.LineSegment(vector_line1, vector_line2)
				betaIntersect = betaCurve.intersectCC(line)
				betaCurveDiscret.append(betaIntersect)

			# Calculation of the Theta angle streamline

			ri = []
			for i in range (0,N,1):
				vector_i = DiscretEdgeOfMeridional[i]
				ri.append(vector_i.y) 

			betai = []
			for i in range (0,N,1):
				vector_betai = betaCurveDiscret[i][0]
				betai.append(vector_betai.Y)

			BfuncList = []
			for i in range (0,N,1):
				BfuncList.append(1./(ri[i]*np.tan(betai[i]*np.pi/180.)))

			BfuncListSr = []
			for i in range (0, (N-1), 1):
				funcX = (BfuncList[i]+BfuncList[i+1])/2.
				BfuncListSr.append(funcX)


			ds_x = []
			ds_y = []
			for i in range (0, N, 1):
				vector_Edge = DiscretEdgeOfMeridional[i]
				ds_x.append(vector_Edge.x)
				ds_y.append(vector_Edge.y)

			ds = []
			for i in range (0, (N-1), 1):
				ds.append(np.sqrt((ds_x[i+1]-ds_x[i])**2+(ds_y[i+1]-ds_y[i])**2))

			dTheta = []
			for i in range (0,(N-1),1):
				dTheta.append(ds[i]*BfuncListSr[i]*180./np.pi)

			dThetaSum = [dTheta[0]]
			for i in range (0,(N-2),1):
				dThetaSum.append(dThetaSum[i]+dTheta[i+1])

			# Coordinates is XYZ of the streamline	
			coord_x = ds_x

			coord_y = [ds_y[0]]
			for i in range(0, (N-1), 1):
				coord_y.append(ds_y[i]*np.cos(np.pi*dThetaSum[i]/180))

			coord_z = [0.0]
			for i in range(0, (N-1), 1):
				coord_z.append(ds_y[i]*np.sin(np.pi*dThetaSum[i]/180))

			# Streamline
			list_of_vectors = []
			for i in range (0, N, 1):
				vector = FreeCAD.Vector(coord_x[i],coord_y[i], coord_z[i])
				list_of_vectors.append(vector)

			streamline = Part.BSplineCurve()
			streamline.interpolate(list_of_vectors)
			return streamline.toShape(), betai, dThetaSum
######################################THE END OF THIS FUNCTION ##########################################################

######################################THIS FUNCTION CREATES A CHART OF THE PARAMETERS STREAMLINE#########################
		def chartBetaTheta (betai, dThetaSum, AnglesChart):
			if AnglesChart ==True:
				x_streamline = np.linspace(0, 1, N)
				y_beta = betai
				y_theta = [0.0]
				for i in range(0, (N-1), 1):
					y = y_theta.append(dThetaSum[i])
				plt.plot(x_streamline, y_beta, x_streamline, y_theta)
				plt.xlabel("Streamline from 0 to 1")
				plt.ylabel("Angle Beta and Angle Theta, [degree]")
				plt.legend(["Beta angle","Theta angle = "+"%.2f" %dThetaSum[-1]], loc='upper right', bbox_to_anchor=(0.5, 1.00))
				plt.grid()
				plt.show()
#####################################THE END OF THIS FUNCTION ###########################################################
		streamlineShroud, betaiShroud, dThetaShroudSum = streamlineBlade(obj.AngleBeta1Shroud, obj.AngleBetaPoint1Shroud, obj.AngleBetaPoint2Shroud, obj.AngleBeta2Shroud, shroudEdgeDiscret)
		streamlineShroudDisc = streamlineShroud.discretize(Number = 10)
		streamlineShroudBad = Part.BSplineCurve()
		streamlineShroudBad.interpolate(streamlineShroudDisc)


		streamlineHub, betaiHub, dThetaHubSum = streamlineBlade(obj.AngleBeta1Hub, obj.AngleBetaPoint1Hub, obj.AngleBetaPoint2Hub, obj.AngleBeta2Hub, hubEdgeDiscret)
		streamlineHubDisc = streamlineHub.discretize(Number = 10)
		streamlineHubBad = Part.BSplineCurve()
		streamlineHubBad.interpolate(streamlineHubDisc)

		chartShroud = chartBetaTheta(betaiShroud, dThetaShroudSum, obj.AnglesChartShroud)
		chartHub = chartBetaTheta(betaiHub, dThetaHubSum, obj.AnglesChartHub)
#################################################################################################################

		if Mer.CylinricalBlades == False:
			aveCurveEdge = Mer.Shape.Edges[11]
			aveCurveEdgeDiscret = aveCurveEdge.discretize(Number = obj.N)
			aveCurveEdgeDiscret.append(aveCurveEdge.lastVertex().Point)

			streamlineAverage, betaiAve, dThetaAveSum = streamlineBlade(obj.AngleBeta1Ave, obj.AngleBetaPoint1Ave, obj.AngleBetaPoint2Ave, obj.AngleBeta2Ave, aveCurveEdgeDiscret)
			streamlineAverageDisc = streamlineAverage.discretize(Number = 10)
			streamlineAveBad = Part.BSplineCurve()
			streamlineAveBad.interpolate(streamlineAverageDisc)	

			chartAve = chartBetaTheta(betaiAve, dThetaAveSum, obj.AnglesChartAverage)
			
			#pointMatrix1 = [streamlineHubDisc, streamlineAverageDisc, streamlineShroudDisc]
			#sur1 = Part.BSplineSurface()
			#sur1.interpolate(pointMatrix1)
			c = Part.makeLoft([streamlineShroudBad.toShape(), streamlineAveBad.toShape(),streamlineHubBad.toShape()])

		else:
			#pointMatrix1 = [streamlineHubDisc, streamlineShroudDisc]

			#sur1 = Part.BSplineSurface()
			#sur1.interpolate(pointMatrix1)

			c = Part.makeLoft([streamlineShroudBad.toShape(), streamlineHubBad.toShape()])


##########################################################################################################
	
		obj.Shape = c
	



myObj2 = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'ModelOfBlade3D')
ModelOfBlade3D(myObj2)
myObj2.ViewObject.Proxy = 0 # this is mandatory unless we code the ViewProvider too
FreeCAD.ActiveDocument.recompute()

