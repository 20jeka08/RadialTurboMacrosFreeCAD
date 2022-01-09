# Script creates a meridional plane of a radial impeller

class Meridional:
	def __init__(self, obj):
		obj.Proxy = self
		obj.addProperty("App::PropertyFloat", "D2", "Dimensions", "Diameter of an impeller").D2=1070
		obj.addProperty("App::PropertyFloat", "d0", "Dimensions", "Diameter of a hub").d0=100
		obj.addProperty("App::PropertyFloat", "D0", "Dimensions", "Suction diameter").D0=850
		obj.addProperty("App::PropertyFloat", "b2", "Dimensions", "Width of a outlet").b2=250
		obj.addProperty("App::PropertyFloat", "L", "Dimensions", "Length").L=300
		obj.addProperty("App::PropertyBool", "CylinricalBlades", "Type of blades", "Number of streamlines").CylinricalBlades=False
		obj.addProperty("App::PropertyPercent", "LePositionShroud", "Place of a Leading edge, %").LePositionShroud=15
		obj.addProperty("App::PropertyPercent", "LePositionHub", "Place of a Leading edge, %").LePositionHub=55
		obj.addProperty("App::PropertyPercent", "LePositionAverage", "Place of a Leading edge, %").LePositionAverage=40
		


	def execute (self, obj):
		import Part, FreeCAD, DraftTools, Draft

		R2 = obj.D2/2.
		r0 = obj.d0/2.
		R0 = obj.D0/2.

		# Create points:
		shroudP1 = FreeCAD.Vector(0, R0,0)
		shroudP2 = FreeCAD.Vector(obj.L,R0,0)
		shroudP3 = FreeCAD.Vector(obj.L,(R2+R0)/2.,0)
		shroudP4 = FreeCAD.Vector(obj.L,R2,0)
		
		hubP1 = FreeCAD.Vector(0,r0,0)
		hubP2 = FreeCAD.Vector(obj.L+obj.b2,r0,0)
		hubP3 = FreeCAD.Vector(obj.L+obj.b2,(R2+R0)/2,0)
		hubP4 = FreeCAD.Vector(obj.L+obj.b2, R2,0)

		aveCurveP1 = FreeCAD.Vector(0, (R0+r0)/2., 0)
		aveCurveP2 = FreeCAD.Vector((obj.L+obj.b2+obj.L)/2.,(R0+r0)/2., 0)
		aveCurveP3 = FreeCAD.Vector((obj.L+obj.b2+obj.L)/2., (R2+R0)/2., 0)
		aveCurveP4 = FreeCAD.Vector((obj.L+obj.b2+obj.L)/2., R2, 0)


		shroudP = [shroudP1, shroudP2, shroudP3, shroudP4]
		hubP = [hubP1, hubP2, hubP3, hubP4]
		aveCurveP = [aveCurveP1, aveCurveP2, aveCurveP3, aveCurveP4]
		
		shroud = Part.BezierCurve()
		shroud.setPoles(shroudP)
		shroud.toShape()
		shroudDiscret = shroud.discretize(Number = 100)

		hub = Part.BezierCurve()
		hub.setPoles(hubP)
		hub.toShape()
		hubDiscret = hub.discretize(Number = 100)			

		aveCurve = Part.BezierCurve()
		aveCurve.setPoles(aveCurveP)
		aveCurve.toShape()
		aveCurveDiscret = aveCurve.discretize(Number = 100)

		inlet1 = Part.LineSegment(shroudP1,FreeCAD.Vector(0, (R0+r0)/2., 0)).toShape()
		inlet2 = Part.LineSegment(FreeCAD.Vector(0, (R0+r0)/2., 0),hubP1).toShape()
		outlet1 = Part.LineSegment(shroudP4,FreeCAD.Vector((obj.L+obj.b2+obj.L)/2., R2, 0)).toShape()
		outlet2 = Part.LineSegment(FreeCAD.Vector((obj.L+obj.b2+obj.L)/2., R2, 0), hubP4).toShape()

		# Creation of the separating meridional plane
		shroud1Discret = shroudDiscret[0:(obj.LePositionShroud+1)]
		shroud2Discret = shroudDiscret[obj.LePositionShroud:101]

		hub1Discret = hubDiscret[0:(obj.LePositionHub+1)]
		hub2Discret = hubDiscret[obj.LePositionHub:101]

		aveCurve1Discret = aveCurveDiscret[0:(obj.LePositionAverage+1)]
		aveCurve2Discret = aveCurveDiscret[obj.LePositionAverage:101]

		# Creation of the Le curve

		LePoints = [shroud2Discret[0],aveCurve2Discret[0], hub2Discret[0]]
		LeCurve = Part.BSplineCurve()
		LeCurve.interpolate(LePoints)
		
		LeCurveDiscret = LeCurve.discretize(Number = 100)

		Le1CurveDiscret = LeCurveDiscret[0:51]
		Le2CurveDiscret = LeCurveDiscret[50:101]

		# Creation a Wire of the Meridional plane of a blades
		shroud1 = Part.BSplineCurve()
		shroud1.interpolate(shroud1Discret)

		shroud2 = Part.BSplineCurve()
		shroud2.interpolate(shroud2Discret)

		hub1 = Part.BSplineCurve()
		hub1.interpolate(hub1Discret)

		hub2 = Part.BSplineCurve()
		hub2.interpolate(hub2Discret)

		Le1Curve = Part.BSplineCurve()
		Le1Curve.interpolate(Le1CurveDiscret)

		Le2Curve = Part.BSplineCurve()
		Le2Curve.interpolate(Le2CurveDiscret)

		aveCurve1 = Part.BSplineCurve()
		aveCurve1.interpolate(aveCurve1Discret)

		aveCurve2 = Part.BSplineCurve()
		aveCurve2.interpolate(aveCurve2Discret)

		if obj.CylinricalBlades==False:
			w = Part.Wire([inlet1,inlet2, shroud1.toShape(), shroud2.toShape(), outlet1, outlet2, hub1.toShape(), hub2.toShape(), Le1Curve.toShape(), Le2Curve.toShape(), aveCurve1.toShape(), aveCurve2.toShape()], closed = False)
		else:
			w = Part.Wire([inlet1,inlet2, shroud1.toShape(), shroud2.toShape(), outlet1, outlet2, hub1.toShape(), hub2.toShape(), Le1Curve.toShape(), Le2Curve.toShape()], closed = False)


		

		shroudSurface = shroud.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)
		hubSurface = hub.toShape().revolve(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 360)


		obj.Shape = Part.Compound([w, shroudSurface, hubSurface])


myObj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Meridional") 
Meridional(myObj)
myObj.ViewObject.Proxy = 0 # this is mandatory unless we code the ViewProvider too
FreeCAD.ActiveDocument.recompute()
FreeCADGui.ActiveDocument.getObject("Meridional").Transparency = 50