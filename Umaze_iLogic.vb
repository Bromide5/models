' U-maze arena for Danionella cerebrum social-behaviour work.
' Base design: Penalva-Tena et al. 2025, Curr. Biol. 35:363-372 (Method Details, p. e2).
'
' V2 (2026-10-11) user revision:
'   * inner cavity 100 x 100 x 40 mm  ->  outer 110 x 110 x 45 mm (wall & floor 5 mm)
'   * both U-branch channels 28 mm wide  ->  centre island 44 mm
'   * U-bottom connecting band 40 -> 34 mm  (fish free space at the U bottom reduced)
'   * NEW guillotine-door slots on the dividing line (island end, y = 71), one per arm:
'       40.8 mm long x 2.4 mm wide  ->  takes a 40 mm-wide glass plate (0.4 mm/side clearance)
'       each slot bites 1.5 mm into the OUTER wall (3.5 mm of wall stays, so it stays watertight)
'       and 11.3 mm into the 44 mm island
'   * coverslip slits kept from the paper: 35.4 x 1.0 mm slit, 20 mm from each arm end,
'     stimulus viewing chamber 20 x 28 mm
'
' Inventor iLogic rule. Run inside a NEW EMPTY Part (mm units) to build the model natively,
' then save as .ipt.  Inventor's API is cm-based -> every mm value is divided by 10.
' buildMaze / buildBaffle / buildGlass select which part this run produces.

Sub Main()
    ' ---- parameters (mm) ----
    Dim L As Double = 110.0     ' overall X  (= innerX + 2*t)
    Dim W As Double = 110.0     ' overall Y
    Dim H As Double = 45.0      ' overall height (= t + waterD)
    Dim t As Double = 5.0       ' wall / floor thickness
    Dim innerX As Double = 100.0    ' inner cavity X
    Dim armW As Double = 28.0       ' U-branch channel width (was 35)
    Dim islandW As Double = 44.0    ' centre island width (= innerX - 2*armW)
    Dim bandD As Double = 34.0      ' U-bottom connecting-band depth (was 40)
    Dim waterD As Double = 40.0     ' inner depth Z = water column
    Dim chD As Double = 20.0        ' stimulus viewing-chamber depth
    Dim yDiv As Double = 71.0       ' dividing line = island end (= W - t - bandD)

    ' coverslip slit (kept from the paper)
    Dim csLen As Double = 35.4      ' slot length (holds the 35 mm coverslip)
    Dim csSlitW As Double = 1.0     ' slit width
    Dim biteOut As Double = 1.5     ' every slot grazes the OUTER wall by this much
    Dim csBiteIn As Double = 5.9    ' coverslip slit bite into the island
    ' branch-partition door (new)
    Dim doorLen As Double = 40.8    ' slot length  = 40 mm plate + 0.8 mm clearance
    Dim doorSlitW As Double = 2.4   ' slot width (plate thickness direction)
    Dim doorBiteIn As Double = 11.3 ' door slot bite into the island

    ' printed baffle (new part)
    Dim bfL As Double = 40.4        ' baffle plate length
    Dim bfT As Double = 2.0         ' baffle plate thickness
    Dim bfH As Double = 39.95       ' baffle plate height
    Dim tabL As Double = 14.0, tabT As Double = 8.0, tabH As Double = 12.0
    Dim tabHoleD As Double = 4.0

    Dim buildMaze As Boolean = True
    Dim buildBaffle As Boolean = False
    Dim buildGlass As Boolean = False   ' 40 x 40 x 2 mm reference plate

    Dim doc As PartDocument = ThisDoc.Document
    Dim comp As PartComponentDefinition = doc.ComponentDefinition
    Dim tg As TransientGeometry = ThisApplication.TransientGeometry

    ' ================= coverslip / glass-plate branch =================
    If buildGlass Then
        Dim skg As PlanarSketch = comp.Sketches.Add(comp.WorkPlanes.Item(3)) ' XY
        skg.SketchLines.AddAsTwoPointRectangle( _
            tg.CreatePoint2d(0, 0), tg.CreatePoint2d(40 / 10, 2 / 10))
        Dim pg As Profile = skg.Profiles.AddForSolid
        comp.Features.ExtrudeFeatures.AddByDistanceExtent( _
            pg, (waterD - 0.4) / 10, kPositiveExtentDirection, kJoinOperation)
        doc.Views.Item(1).GoHome()
        MsgBox("Glass baffle plate built: 40 x 2 x 39.6 mm (reference part).", , "U-maze")
        Exit Sub
    End If

    ' ================= printed baffle branch =================
    If buildBaffle Then
        Dim skb As PlanarSketch = comp.Sketches.Add(comp.WorkPlanes.Item(3))
        skb.SketchLines.AddAsTwoPointRectangle( _
            tg.CreatePoint2d(0, 0), tg.CreatePoint2d(bfL / 10, bfT / 10))
        Dim pb As Profile = skb.Profiles.AddForSolid
        Dim eb As ExtrudeFeature = comp.Features.ExtrudeFeatures.AddByDistanceExtent( _
            pb, bfH / 10, kPositiveExtentDirection, kJoinOperation)
        eb.Name = "BafflePlate"

        ' handle tab (wider than the slot -> acts as a stop on the rim)
        Dim faceTop As Face = Nothing
        For Each f As Face In comp.SurfaceBodies.Item(1).Faces
            If f.SurfaceType = kPlaneSurface Then
                Dim n As UnitVector = CType(f.Geometry, Plane).Normal
                Dim c As Point = CType(f.Geometry, Plane).RootPoint
                If Math.Abs(n.Z - 1) < 0.001 And Math.Abs(c.Z * 10 - bfH) < 0.01 Then
                    faceTop = f : Exit For
                End If
            End If
        Next
        Dim skt As PlanarSketch = comp.Sketches.Add(faceTop)
        Dim tabX0 As Double = (bfL / 2 - tabL / 2) / 10
        Dim tabY0 As Double = (bfT / 2 - tabT / 2) / 10
        skt.SketchLines.AddAsTwoPointRectangle( _
            tg.CreatePoint2d(tabX0, tabY0), tg.CreatePoint2d(tabX0 + tabL / 10, tabY0 + tabT / 10))
        Dim pt As Profile = skt.Profiles.AddForSolid
        comp.Features.ExtrudeFeatures.AddByDistanceExtent( _
            pt, tabH / 10, kPositiveExtentDirection, kJoinOperation).Name = "Tab"

        ' finger / thread hole through the tab (sketch on the XZ plane, cut both ways)
        Dim skh As PlanarSketch = comp.Sketches.Add(comp.WorkPlanes.Item(2)) ' XZ
        Dim cx As Double = (bfL / 2) / 10
        Dim cz As Double = (bfH + tabH / 2) / 10
        skh.SketchCircles.AddByCenterRadius(tg.CreatePoint2d(cx, cz), tabHoleD / 2 / 10)
        Dim ph As Profile = skh.Profiles.AddForSolid
        comp.Features.ExtrudeFeatures.AddByDistanceExtent( _
            ph, (tabT + 4) / 10, kSymmetricExtentDirection, kCutOperation).Name = "TabHole"

        doc.Views.Item(1).GoHome()
        MsgBox("Printed gate baffle built: " & bfL & " x " & bfT & " x " & bfH & _
               " mm + tab (print 2).", , "U-maze")
        Exit Sub
    End If

    ' ================= arena branch =================
    Dim sk1 As PlanarSketch = comp.Sketches.Add(comp.WorkPlanes.Item(3)) ' XY
    sk1.SketchLines.AddAsTwoPointRectangle( _
        tg.CreatePoint2d(0, 0), tg.CreatePoint2d(L / 10, W / 10))
    Dim prof1 As Profile = sk1.Profiles.AddForSolid
    comp.Features.ExtrudeFeatures.AddByDistanceExtent( _
        prof1, H / 10, kPositiveExtentDirection, kJoinOperation).Name = "BaseBlock"

    ' ---- top face (all cuts are sketched on it and extruded down to the floor) ----
    Dim topFace As Face = Nothing
    For Each f As Face In comp.SurfaceBodies.Item(1).Faces
        If f.SurfaceType = kPlaneSurface Then
            Dim n1 As UnitVector = CType(f.Geometry, Plane).Normal
            Dim c1 As Point = CType(f.Geometry, Plane).RootPoint
            If Math.Abs(n1.Z - 1) < 0.001 And Math.Abs(c1.Z * 10 - H) < 0.01 Then
                topFace = f : Exit For
            End If
        End If
    Next

    ' ---- U-shaped channel: two arms + connecting band ----
    Dim x0 As Double = t / 10
    Dim x1 As Double = (t + armW) / 10
    Dim x2 As Double = (t + armW + islandW) / 10
    Dim x3 As Double = (L - t) / 10
    Dim y0 As Double = t / 10
    Dim y1 As Double = (W - t) / 10
    Dim yd As Double = yDiv / 10
    Dim sk2 As PlanarSketch = comp.Sketches.Add(topFace)
    Dim P(7) As Point2d
    P(0) = tg.CreatePoint2d(x0, y0) : P(1) = tg.CreatePoint2d(x1, y0)
    P(2) = tg.CreatePoint2d(x1, yd) : P(3) = tg.CreatePoint2d(x2, yd)
    P(4) = tg.CreatePoint2d(x2, y0) : P(5) = tg.CreatePoint2d(x3, y0)
    P(6) = tg.CreatePoint2d(x3, y1) : P(7) = tg.CreatePoint2d(x0, y1)
    Dim i As Integer
    For i = 0 To 7
        sk2.SketchLines.AddByTwoPoints(P(i), P((i + 1) Mod 8))
    Next
    Dim prof2 As Profile = sk2.Profiles.AddForSolid
    comp.Features.ExtrudeFeatures.AddByDistanceExtent( _
        prof2, waterD / 10, kNegativeExtentDirection, kCutOperation).Name = "UChannel"

    ' ---- NEW: two guillotine-door slots on the dividing line ----
    Dim sk4 As PlanarSketch = comp.Sketches.Add(topFace)
    Dim dY0 As Double = (yDiv - doorSlitW / 2) / 10
    Dim dL As Double = doorLen / 10
    Dim dW As Double = doorSlitW / 10
    Dim dXl As Double = (t - biteOut) / 10                                  ' left arm
    sk4.SketchLines.AddAsTwoPointRectangle( _
        tg.CreatePoint2d(dXl, dY0), tg.CreatePoint2d(dXl + dL, dY0 + dW))
    Dim dXr As Double = (L - t - armW - doorBiteIn) / 10                    ' right arm
    sk4.SketchLines.AddAsTwoPointRectangle( _
        tg.CreatePoint2d(dXr, dY0), tg.CreatePoint2d(dXr + dL, dY0 + dW))
    Dim prof4 As Profile = sk4.Profiles.AddForSolid
    comp.Features.ExtrudeFeatures.AddByDistanceExtent( _
        prof4, waterD / 10, kNegativeExtentDirection, kCutOperation).Name = "DoorSlots"

    ' ---- coverslip slits near the arm ends (kept from the paper) ----
    Dim sk3 As PlanarSketch = comp.Sketches.Add(topFace)
    Dim sy As Double = (t + chD) / 10
    Dim sl As Double = csLen / 10
    Dim sw As Double = csSlitW / 10
    Dim sx As Double = (t - biteOut) / 10
    sk3.SketchLines.AddAsTwoPointRectangle( _
        tg.CreatePoint2d(sx, sy - sw / 2), tg.CreatePoint2d(sx + sl, sy + sw / 2))
    sx = (L - t - armW - csBiteIn) / 10
    sk3.SketchLines.AddAsTwoPointRectangle( _
        tg.CreatePoint2d(sx, sy - sw / 2), tg.CreatePoint2d(sx + sl, sy + sw / 2))
    Dim prof3 As Profile = sk3.Profiles.AddForSolid
    comp.Features.ExtrudeFeatures.AddByDistanceExtent( _
        prof3, waterD / 10, kNegativeExtentDirection, kCutOperation).Name = "CoverslipSlits"

    ' ---- soften the exposed top edges only (never the slot mouths) ----
    Dim fe As EdgeCollection = ThisApplication.TransientObjects.CreateEdgeCollection()
    For Each f As Face In comp.SurfaceBodies.Item(1).Faces
        If f.SurfaceType = kPlaneSurface Then
            Dim n2 As UnitVector = CType(f.Geometry, Plane).Normal
            If Math.Abs(n2.Z - 1) < 0.001 Then
                For Each e As Edge In f.Edges
                    fe.Add(e)
                Next
            End If
        End If
    Next
    If fe.Count > 0 Then
        comp.Features.FilletFeatures.AddSimple(fe, 0.03, False)
    End If

    doc.Views.Item(1).GoHome()
    MsgBox("U-maze built: outer 110x110x45, inner 100x100x40, arms 28, island 44, " & _
           "U-bottom band 34, door slots 40.8x2.4 on the dividing line (y=71), " & _
           "coverslip slits 35.4 at 20 mm from the arm ends.", , "U-maze")
End Sub
