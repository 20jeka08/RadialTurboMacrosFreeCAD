# Script creates a 3D blade with thickness
Mer = App.ActiveDocument.getObject("Meridional")

# Creation of parameters for change geometry
class Blades:
	def __init__(self, obj):
		obj.Proxy = self
		obj.addProperty("App::PropertyFloat", "ThicknessLEShroud", "Shroud profile", "Value of the LE").ThicknessLEShroud = Mer.D2*0.02
		obj.addProperty("App::PropertyVector", "ThicknessPoint1Shroud", "Shroud profile", "Point for B-Spline thickness").ThicknessPoint1Shroud = (40, Mer.D2*0.02, 0)
		obj.addProperty("App::PropertyVector", "ThicknessPoint2Shroud", "Shroud profile", "Point for B-Spline thickness").ThicknessPoint2Shroud = (75, Mer.D2*0.02, 0)
		obj.addProperty("App::PropertyFloat", "ThicknessTEShroud", "Shroud profile", "Value of the TE").ThicknessTEShroud = Mer.D2*0.02

		obj.addProperty("App::PropertyFloat", "ThicknessLEHub", "Hub profile", "Value of the thickness LE").ThicknessLEHub = Mer.D2*0.02
		obj.addProperty("App::PropertyVector", "ThicknessPoint1Hub", "Hub profile", "Point for B-Spline thickness").ThicknessPoint1Hub = (40, Mer.D2*0.02, 0)
		obj.addProperty("App::PropertyVector", "ThicknessPoint2Hub", "Hub profile", "Point for B-Spline thickness").ThicknessPoint2Hub = (75, Mer.D2*0.02, 0)
		obj.addProperty("App::PropertyFloat", "ThicknessTEHub", "Hub profile", "Value of the thickness TE").ThicknessTEHub = Mer.D2*0.02

		obj.addProperty("App::PropertyFloat", "ThicknessLEAve", "Average profile", "Value of the thickness LE").ThicknessLEAve = Mer.D2*0.02
		obj.addProperty("App::PropertyVector", "ThicknessPoint1Ave", "Average profile", "Value of the thickness"). ThicknessPoint1Ave = (40, Mer.D2*0.02, 0)
		obj.addProperty("App::PropertyVector", "ThicknessPoint2Ave", "Average profile", "Value of The thickness"). ThicknessPoint2Ave = (75, Mer.D2*0.02, 0)
		obj.addProperty("App::PropertyFloat", "ThicknessTEAve", "Average profile", "Value of the thickness TE"). ThicknessTEAve = Mer.D2*0.02

		obj.addProperty("App::PropertyBool", "TraillingEdgeEllipse", "Type of the LE and TE", "Type of the trailling edge").TraillingEdgeEllipse = False
		obj.addProperty("App::PropertyInteger", "LeadingEdgeType", "Type of the LE and TE", "Type of the leading edge").LeadingEdgeType = 1
		obj.addProperty("App::PropertyInteger", "TraillingEdgeType", "Type of the LE and TE", "Type of the trailling edge" ).TraillingEdgeType = 1
		obj.addProperty("App::PropertyInteger", "NumberOfBlades", "Number of blades").NumberOfBlades=7

		obj.addProperty("App::PropertyBool", "FullDomainCFD", "CFD", "Create full CFD Domain").FullDomainCFD = False
		obj.addProperty("App::PropertyBool", "PeriodicDomainCFD", "CFD", "Create periodic CFD Domain").PeriodicDomainCFD = False
		obj.addProperty("App::PropertyFloat", "HalfD3toD2", "CFD", "Value of half relationship D3/D2").HalfD3toD2 = 1.2


	def execute (self, obj):
		import Part, FreeCAD, DraftTools, Draft
		import numpy as np
		import copy

		# Creation of the profile of streamlines:
		Blade = App.ActiveDocument.getObject("ModelOfBlade3D")
		BladeFace = Blade.Shape.Faces[0]
		BladeSurface = BladeFace.Surface
		BladeEdgeShroud = BladeFace.Edges[0]
		BladeEdgeHub = BladeFace.Edges[2]

		BladeEdgeTe = BladeFace.Edges[1]

		R2 = Mer.D2/2.
		R0 = Mer.D0/2.
		r0 = Mer.d0/2.

		def thicknessProfile (ThicknessLE, ThicknessPoint1, ThicknessPoint2, ThicknessTE, BladeStreamlineEdge, BladeFace, BladeSurface, NameOfDisk, EdgeTe, LECoeff1, TECoeff1,TraillingEdgeEllipse, UVoutlet, Extend):
			
			BladesEdgeDicretForLe = BladeStreamlineEdge.discretize(Distance = ThicknessLE/4.)
			BladesEdgeDicretForSide = BladeStreamlineEdge.discretize(Number = 20)

			if Mer.CylinricalBlades == False:
				BladesEdgeDicret = []
				for i in range (0, 10, 1):
					BladesEdgeDicret.append(BladesEdgeDicretForLe[i])

				for i in range (3, len(BladesEdgeDicretForSide), 1):
					BladesEdgeDicret.append(BladesEdgeDicretForSide[i])

				OutletVector = BladeFace.valueAt(Extend, UVoutlet)

				BladesEdgeDicret.append(OutletVector)
			else:
				BladesEdgeDicret = []
				for i in range (0, 10, 1):
					BladesEdgeDicret.append(BladesEdgeDicretForLe[i])

				for i in range (3, len(BladesEdgeDicretForSide), 1):
					BladesEdgeDicret.append(BladesEdgeDicretForSide[i])

				OutletVector = BladeFace.valueAt(1.1*BladeEdgeShroud.Length, UVoutlet)

				BladesEdgeDicret.append(OutletVector)

	#################
			# Creation of Thickness curve of the Shroud
			ThicknessPoints = [FreeCAD.Vector(0, ThicknessLE, 0), ThicknessPoint1, ThicknessPoint2, FreeCAD.Vector(100, ThicknessTE, 0)]
			ThicknessCurve = Part.BSplineCurve()
			ThicknessCurve.interpolate(ThicknessPoints)
			ThicknessCurveDiscret = []
			for i in range (0, len(BladesEdgeDicret), 1):
				vector_line1 = FreeCAD.Vector(float(i)/(float(len(BladesEdgeDicret))/100.), -180, 0)
				vector_line2 = FreeCAD.Vector(float(i)/(float(len(BladesEdgeDicret))/100.), 180, 0)
				line = Part.LineSegment(vector_line1, vector_line2)
				ThicknessIntersect = ThicknessCurve.intersectCC(line)
				ThicknessCurveDiscret.append(ThicknessIntersect)

				vu = []
			for i in range (0, len(BladesEdgeDicret), 1):
				vuVector = BladeSurface.parameter(BladesEdgeDicret[i])
				vu.append(vuVector)

			 				

			normalPressure = []
			for i in range (0, len(vu), 1):
				normalVector = BladeFace.normalAt(vu[i][0], vu[i][1])
				normalPressure.append(normalVector.normalize())

			normalSuction = []
			for i in range (0, len(vu), 1):
				normalVector = BladeFace.normalAt(vu[i][0], vu[i][1])
				normalSuction.append(normalVector.normalize())

			if TraillingEdgeEllipse == False:

				pressureSide = []
				for i in range (2*LECoeff1, len(normalPressure), 1):
					vectorPressureSide = normalPressure[i]
					valueThickness = ThicknessCurveDiscret[i][0]
					vectorPressureSide = vectorPressureSide.multiply(valueThickness.Y/2.)
					vectorPressureSide = vectorPressureSide.add(BladesEdgeDicret[i])
					pressureSide.append(vectorPressureSide)

				suctionSide = []
				for i in range (2*LECoeff1, len(normalSuction), 1):
					vectorSuctionSide = normalSuction[i]
					valueThickness = ThicknessCurveDiscret[i][0]
					vectorSuctionSide = vectorSuctionSide.multiply(-valueThickness.Y/2.)
					vectorSuctionSide = vectorSuctionSide.add(BladesEdgeDicret[i])
					suctionSide.append(vectorSuctionSide)

			else:

				pressureSide = []
				for i in range (2*LECoeff1, len(normalPressure)-2*TECoeff1, 1):
					vectorPressureSide = normalPressure[i]
					valueThickness = ThicknessCurveDiscret[i][0]
					vectorPressureSide = vectorPressureSide.multiply(valueThickness.Y/2.)
					vectorPressureSide = vectorPressureSide.add(BladesEdgeDicret[i])
					pressureSide.append(vectorPressureSide)

				suctionSide = []
				for i in range (2*LECoeff1, len(normalSuction)-2*TECoeff1, 1):
					vectorSuctionSide = normalSuction[i]
					valueThickness = ThicknessCurveDiscret[i][0]
					vectorSuctionSide = vectorSuctionSide.multiply(-valueThickness.Y/2.)
					vectorSuctionSide = vectorSuctionSide.add(BladesEdgeDicret[i])
					suctionSide.append(vectorSuctionSide)


			# Points of the LE Shroud curve
			LePointsList = []

			for i in range (1, LECoeff1*2):
				lengthLePi = ThicknessLE/2*np.sqrt(1.-(i*ThicknessLE/4.)**2/(float(LECoeff1)/2.*ThicknessLE)**2)
				LePointsList.append(lengthLePi)
			LePointsList.reverse()

			LeCurvePressure = [BladesEdgeDicret[0]]
			for i in range (1, len(LePointsList)+1):
				vectorPressureLe = normalPressure[i]
				vectorPressureLe = vectorPressureLe.multiply(LePointsList[i-1])
				vectorPressureLe = vectorPressureLe.add(BladesEdgeDicret[i])
				LeCurvePressure.append(vectorPressureLe)
			LeCurvePressure.append(pressureSide[0])
			LeCurvePressure.reverse()

			LeCurveSuction = []
			for i in range (1, len(LePointsList)+1):
				vectorSuctionLe = normalSuction[i]
				vectorSuctionLe = vectorSuctionLe.multiply(-LePointsList[i-1])
				vectorSuctionLe = vectorSuctionLe.add(BladesEdgeDicret[i])
				LeCurveSuction.append(vectorSuctionLe)
			LeCurveSuction.append(suctionSide[0])
			
			Le = LeCurvePressure+LeCurveSuction

			# Line of the TE Shroud curve
			if TraillingEdgeEllipse == False:
			
				TeP1 = pressureSide[-1]
				TeP2 = suctionSide[-1]
				TeSpline = Part.LineSegment(TeP1, TeP2)
		
			else:
########################################## For realization ####################				
				TePointsList = []

				for i in range (1, TECoeff1*2):
					lengthTePi = ThicknessTE/2*np.sqrt(1.-(i*ThicknessTE/4.)**2/(float(TECoeff1)/2.*ThicknessTE)**2)
					TePointsList.append(lengthTePi)
				TePointsList.reverse()

				TeCurvePressure = [BladesEdgeDicret[-1]]
				for i in range (-2, -len(TePointsList)-2, -1):
					vectorPressureTe = normalPressure[i]
					vectorPressureTe = vectorPressureTe.multiply(TePointsList[-i-2])
					vectorPressureTe = vectorPressureTe.add(BladesEdgeDicret[i])
					TeCurvePressure.append(vectorPressureTe)
				TeCurvePressure.append(pressureSide[-1])
				TeCurvePressure.reverse()

				TeCurveSuction = []
				for i in range (-2, -len(TePointsList)-2, -1):
					vectorSuctionTe = normalSuction[i]
					vectorSuctionTe = vectorSuctionTe.multiply(-TePointsList[-i-2])
					vectorSuctionTe = vectorSuctionTe.add(BladesEdgeDicret[i])
					TeCurveSuction.append(vectorSuctionTe)
				TeCurveSuction.append(suctionSide[-1])
				
				Te = TeCurvePressure+TeCurveSuction
				TeSpline = Part.BSplineCurve()
				TeSpline.interpolate(Te)
################################################### THE END ######################

			pressureSide2 = Part.BSplineCurve()
			pressureSide2.interpolate(pressureSide)
			suctionSide2 = Part.BSplineCurve()
			suctionSide2.interpolate(suctionSide)

			pressureSide2Discr = pressureSide2.discretize(Number = 100)
			suctionSide2Discr = suctionSide2.discretize(Number = 100)



			e = Part.BSplineCurve()
			e.interpolate(pressureSide2Discr)
			e2 = Part.BSplineCurve()
			e2.interpolate(suctionSide2Discr)
			e3 = Part.BSplineCurve()
			e3.interpolate(Le)


			w = Part.Wire([e3.toShape(), e.toShape(), e2.toShape(), TeSpline.toShape()])

			return w


##########################################################################


		

		ShroudProfile = thicknessProfile(obj.ThicknessLEShroud, obj.ThicknessPoint1Shroud, obj.ThicknessPoint2Shroud, obj.ThicknessTEShroud, BladeEdgeShroud, BladeFace, BladeSurface, "Hub", BladeEdgeTe, obj.LeadingEdgeType, obj.TraillingEdgeType, obj.TraillingEdgeEllipse, 0.0, 1.05)
		HubProfile = thicknessProfile(obj.ThicknessLEHub, obj.ThicknessPoint1Hub, obj.ThicknessPoint2Hub, obj.ThicknessTEHub, BladeEdgeHub, BladeFace, BladeSurface, "Shroud", BladeEdgeTe, obj.LeadingEdgeType, obj.TraillingEdgeType, obj.TraillingEdgeEllipse, 1.0, 1.05)

		
		BladeEdgeShroudDiscret = BladeEdgeShroud.discretize(Distance = obj.ThicknessLEShroud/4.)

		uv = []
		for i in range (0, len(BladeEdgeShroudDiscret), 1):
			uv_value = BladeSurface.parameter(BladeEdgeShroudDiscret[i])
			uv.append(uv_value)

		tangentShroud = []
		for i in range (0, len(BladeEdgeShroudDiscret), 1):
			tangentVector = BladeFace.tangentAt(uv[i][0], uv[i][1])
			tangentShroud.append(tangentVector)

		curveShroud2 = []
		for i in range (0, len(BladeEdgeShroudDiscret), 1):
			vectorCurveShroud = tangentShroud[i][1]
			valueTranslate = obj.ThicknessLEShroud*1.5
			vectorCurveShroud = vectorCurveShroud.multiply(-valueTranslate)
			vectorCurveShroud = vectorCurveShroud.add(BladeEdgeShroudDiscret[i])
			curveShroud2.append(vectorCurveShroud)
		
		splineShroud2 = Part.BSplineCurve()
		splineShroud2.interpolate(curveShroud2)



		BladeEdgeHubDiscret = BladeEdgeHub.discretize(Distance = obj.ThicknessLEHub/4.)

		uvHub = []
		for i in range (0, len(BladeEdgeHubDiscret), 1):
			uv_valueHub = BladeSurface.parameter(BladeEdgeHubDiscret[i])
			uvHub.append(uv_valueHub)		

		tangentHub = []
		for i in range (0, len(BladeEdgeHubDiscret), 1):
			tangentVectorHub = BladeFace.tangentAt(uvHub[i][0], uvHub[i][1])
			tangentHub.append(tangentVectorHub)

		curveHub2 = []
		for i in range (0, len(BladeEdgeHubDiscret), 1):
			vectorCurveHub = tangentHub[i][1]
			valueTranslate = obj.ThicknessLEHub
			vectorCurveHub = vectorCurveHub.multiply(valueTranslate)
			vectorCurveHub = vectorCurveHub.add(BladeEdgeHubDiscret[i])
			curveHub2.append(vectorCurveHub)
		splineHub2 = Part.BSplineCurve()
		splineHub2.interpolate(curveHub2)
		BladeEdgeHubReverse = BladeEdgeHub.reverse()

		faceShroud2 = Part.makeRuledSurface(splineShroud2.toShape(), BladeEdgeShroud)
		faceHub2 = Part.makeRuledSurface(BladeEdgeHub, splineHub2.toShape())

		BladeEdgeTeShroud2 = faceShroud2.Edges[1]
		BladeEdgeTeHub2 = faceHub2.Edges[1] 

		ShroudProfile2 = thicknessProfile(obj.ThicknessLEShroud, obj.ThicknessPoint1Shroud, obj.ThicknessPoint2Shroud, obj.ThicknessTEShroud, splineShroud2, faceShroud2, faceShroud2.Surface, "Hub", BladeEdgeTeShroud2, obj.LeadingEdgeType, obj.TraillingEdgeType, obj.TraillingEdgeEllipse, 0.0, BladeEdgeShroud.Length*1.05)
		HubProfile2 = thicknessProfile(obj.ThicknessLEHub, obj.ThicknessPoint1Hub, obj.ThicknessPoint2Hub, obj.ThicknessTEHub, splineHub2, faceHub2, faceHub2.Surface, "Shroud", BladeEdgeTeHub2, obj.LeadingEdgeType, obj.TraillingEdgeType, obj.TraillingEdgeEllipse, 1.0, BladeEdgeHub.Length*1.05)

		if Mer.CylinricalBlades == False:

			# Creation of the average streamline in surface blade
			aveMerLine = Mer.Shape.Edges[11]
			revolveAveLine = aveMerLine.revolve(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), 360)

			aveCurveIntersect = revolveAveLine.Surface.intersectSS(BladeSurface)
			aveCurve = aveCurveIntersect[0]

			AveProfile = thicknessProfile(obj.ThicknessLEAve, obj.ThicknessPoint1Ave, obj.ThicknessPoint2Ave, obj.ThicknessTEAve, aveCurve, BladeFace, BladeSurface, "Average", BladeEdgeTe, obj.LeadingEdgeType, obj.TraillingEdgeType, obj.TraillingEdgeEllipse, 0.5, 1.05)

			#BladeSurfaceModel = Part.makeLoft([ShroudProfile2, ShroudProfile, AveProfile, HubProfile, HubProfile2])
			BladeSurfaceModel = Part.makeLoft([ShroudProfile2,AveProfile, HubProfile2])
		else:
			#BladeSurfaceModel = Part.makeLoft([ShroudProfile2, ShroudProfile, HubProfile, HubProfile2])
			BladeSurfaceModel = Part.makeLoft([ShroudProfile2, HubProfile2])

		if obj.TraillingEdgeEllipse == False:

			ListEdges1 = [BladeSurfaceModel.Edges[0], BladeSurfaceModel.Edges[4], BladeSurfaceModel.Edges[7], BladeSurfaceModel.Edges[10]]
			Surface1 = Part.makeFilledFace(ListEdges1)

			ListEdges2 = [BladeSurfaceModel.Edges[2], BladeSurfaceModel.Edges[6], BladeSurfaceModel.Edges[9], BladeSurfaceModel.Edges[11]]
			Surface2 = Part.makeFilledFace(ListEdges2)
			
			ListSurfaces = Part.Compound([BladeSurfaceModel.Faces[0], BladeSurfaceModel.Faces[1], BladeSurfaceModel.Faces[2], BladeSurfaceModel.Faces[3], Surface1, Surface2])
			ListSurfaces.removeSplitter()
			BladeShell = Part.makeShell(ListSurfaces.Faces)
			BladeShell.removeSplitter()
			BladeSolidInit = Part.makeSolid(BladeShell)

		# Cut of the TE 

		LineShroudBlock = Part.LineSegment(FreeCAD.Vector(Mer.L/2, R2), FreeCAD.Vector(Mer.L/2, R2*1.2))
		LineHubBlock = Part.LineSegment(FreeCAD.Vector((Mer.L+Mer.b2)*2, R2), FreeCAD.Vector((Mer.L+Mer.b2)*2, R2*1.2))
		LineTopBlock = Part.LineSegment(FreeCAD.Vector(Mer.L/2, R2*1.2), FreeCAD.Vector((Mer.L+Mer.b2)*2, R2*1.2))
		LineDownBlock = Part.LineSegment(FreeCAD.Vector(Mer.L/2, R2), FreeCAD.Vector((Mer.L+Mer.b2)*2, R2))

		FaceShroudBlock = LineShroudBlock.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)
		FaceHubBlock = LineHubBlock.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)
		FaceTopBlock = LineTopBlock.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)
		FaceDownBlock = LineDownBlock.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)

		BlockShell = Part.makeShell([FaceShroudBlock, FaceHubBlock, FaceTopBlock, FaceDownBlock])
		BlockSolid = Part.makeSolid(BlockShell)

		BladeSolidSecond = BladeSolidInit.cut(BlockSolid)


		if obj.FullDomainCFD == False and obj.PeriodicDomainCFD == False:
			#Cut of the Shroud Side of Blade 
			FaceShroudCut =Mer.Shape.Faces[0]		
			LineTopShroudCut = Part.LineSegment(FreeCAD.Vector(Mer.L, R2, 0), FreeCAD.Vector(0, R2, 0))
			FaceTopShroudCut = LineTopShroudCut.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)
			LineInletShroudCut = Part.LineSegment(FreeCAD.Vector(0, R2, 0), FreeCAD.Vector(0, R0, 0))
			FaceInletShroudCut = LineInletShroudCut.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)

			ShroudCutBLockShell = Part.makeShell([FaceShroudCut, FaceTopShroudCut, FaceInletShroudCut])
			ShroudCutBLockSolid = Part.makeSolid(ShroudCutBLockShell)

			BladeSolidThree = BladeSolidSecond.cut(ShroudCutBLockSolid)

			# Cut of the Hub Side Of Blade
			FaceHubCut = Mer.Shape.Faces[1]
			LineTopHubCut = Part.LineSegment(FreeCAD.Vector(Mer.L+Mer.b2, R2, 0), FreeCAD.Vector(Mer.L+Mer.b2*2, R2, 0))
			FaceTopHubCut = LineTopHubCut.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)
			LineSideHubCut = Part.LineSegment(FreeCAD.Vector(Mer.L+Mer.b2*2, R2, 0), FreeCAD.Vector(Mer.L+Mer.b2*2, 0, 0))
			FaceSideHubCut = LineSideHubCut.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)
			LineSide2HubCut = Part.LineSegment(FreeCAD.Vector(0, r0, 0), FreeCAD.Vector(0, 0, 0))
			FaceSide2HubCut = LineSide2HubCut.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)

			HubCutBLockShell = Part.makeShell([FaceHubCut, FaceTopHubCut, FaceSideHubCut, FaceSide2HubCut])
			HubCutBLockSolid = Part.makeSolid(HubCutBLockShell)	

			BladeSolid = BladeSolidThree.cut(HubCutBLockSolid)	

		# Creation of a massive of blades		
			AngleRotateBlade = 360./float(obj.NumberOfBlades)
			BladesList = []
			for i in range (0, obj.NumberOfBlades, 1):
				BladeSolidi = BladeSolid.copy()
				BladeSolidi.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), AngleRotateBlade*(i))
				BladesList.append(BladeSolidi)

		elif obj.FullDomainCFD==True and obj.PeriodicDomainCFD == False:
		# Creation of a massive of blades without cut of shroud and hub parts
			AngleRotateBlade = 360./float(obj.NumberOfBlades)
			Blades = []
			for i in range (0, obj.NumberOfBlades, 1):
				BladeSolidi = BladeSolidSecond.copy()
				BladeSolidi.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), AngleRotateBlade*(i))
				Blades.append(BladeSolidi)
		# Creation of a CFD part without blades
			FaceShroudCut =Mer.Shape.Faces[0]
			FaceHubCut = Mer.Shape.Faces[1]

			EdgeInlet = Part.LineSegment(FreeCAD.Vector(0,r0,0), FreeCAD.Vector(0,R0, 0))
			FaceInlet = EdgeInlet.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)

			EdgeShroud2 = Part.LineSegment(FreeCAD.Vector(Mer.L, R2, 0), FreeCAD.Vector(Mer.L, R2*obj.HalfD3toD2, 0))
			FaceShroud2 = EdgeShroud2.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)

			EdgeHub2 = Part.LineSegment(FreeCAD.Vector(Mer.L+Mer.b2, R2, 0), FreeCAD.Vector(Mer.L+Mer.b2, R2*obj.HalfD3toD2, 0))
			FaceHub2 = EdgeHub2.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)

			EdgeOutlet = Part.LineSegment(FreeCAD.Vector(Mer.L, R2*obj.HalfD3toD2, 0), FreeCAD.Vector(Mer.L+Mer.b2, R2*obj.HalfD3toD2, 0))
			FaceOutlet = EdgeOutlet.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)

			CFDDomainShell = Part.makeShell([FaceInlet, FaceShroudCut, FaceShroud2, FaceOutlet, FaceHub2, FaceHubCut])
			CFDDomainSolid = Part.makeSolid(CFDDomainShell)
			CFDDomainSolid.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), -(360/obj.NumberOfBlades)/2)

			CFDDomain = CFDDomainSolid.cut(Part.Compound(Blades))

			BladesList = [CFDDomain]

		elif obj.FullDomainCFD==False and obj.PeriodicDomainCFD == True:
		# Creation Periodic CFD Domain
			AngleRotateFacePeriodic = 180./float(obj.NumberOfBlades)

			EdgeInlet = Part.LineSegment(FreeCAD.Vector(0,r0,0), FreeCAD.Vector(0,R0, 0)).toShape()
			EdgeShroud = Mer.Shape.Edges[2]
			EdgeHub = Mer.Shape.Edges[6]
			EdgeLE = Blade.Shape.Edges[3]
			WireInlet = Part.Wire([EdgeInlet, EdgeShroud, EdgeLE, EdgeHub])
			FaceInletCFD = Part.Face(WireInlet)


			FacePeriodic1 = BladeFace.copy()
			FacePeriodic1.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), AngleRotateFacePeriodic)
			FaceInletCFD.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), AngleRotateFacePeriodic)


			CFDSolid1 = FacePeriodic1.revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), -2*AngleRotateFacePeriodic)
			CFDSolid2 = FaceInletCFD.revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), -2*AngleRotateFacePeriodic)
			
		
		# Creation of the outlet part of periodic CFD domain
			EdgeFirstOut = CFDSolid1.Edges[1]
			VertexFirstOut = EdgeFirstOut.firstVertex()
			VectorFirstOut = VertexFirstOut.Point
			VectorFirstZero = FreeCAD.Vector(Mer.L,0,0)
			LineFirstOut = Part.LineSegment(VectorFirstZero, VectorFirstOut).toShape()
			VectorFirstOutAdd = LineFirstOut.valueAt(LineFirstOut.Length*obj.HalfD3toD2)
			LineFirstOutAdd = Part.LineSegment(VectorFirstOut, VectorFirstOutAdd).toShape()

			EdgeSecondOut = CFDSolid1.Edges[4]
			VertexSecondOut = EdgeSecondOut.firstVertex()
			VectorSecondOut = VertexSecondOut.Point
			VectorSecondZero = FreeCAD.Vector(Mer.L+Mer.b2, 0, 0)
			LineSecondOut = Part.LineSegment(VectorSecondZero, VectorSecondOut).toShape()
			VectorSecondOutAdd = LineSecondOut.valueAt(LineSecondOut.Length*obj.HalfD3toD2)
			LineSecondOutAdd = Part.LineSegment(VectorSecondOut, VectorSecondOutAdd).toShape()

			LineOutlet = Part.LineSegment(VectorFirstOutAdd, VectorSecondOutAdd).toShape()
			ListEdgesOutletBlock = [CFDSolid1.Edges[5], LineFirstOutAdd, LineSecondOutAdd, LineOutlet]
			FaceOutBlock = Part.makeFilledFace(ListEdgesOutletBlock)

			SolidOutletCFD = FaceOutBlock.revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), -2*AngleRotateFacePeriodic)
			

			CFDSolid3 = CFDSolid1.fuse(CFDSolid2)
			CFDSolid = CFDSolid3.fuse(SolidOutletCFD)
			CFDSolid = CFDSolid.cut(BladeSolidSecond)
			BladesList = [CFDSolid]


		obj.Shape = Part.Compound(BladesList)
		#obj.Shape = BladeSolidInit



myObj3 = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'Blades')
Blades(myObj3)
myObj3.ViewObject.Proxy = 0 # this is mandatory unless we code the ViewProvider too
FreeCAD.ActiveDocument.recompute()


