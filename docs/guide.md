# Easement curve guide

- [Introduction][1]
- [Joining two straight tracks][2]
- [Extending a track to join another][3]
- [Other ways of using the curve data][4]

## Introduction
[1]: #introduction

Starting up the GUI gives you this:

![GUI](images/gui.jpg)

- There are two methods of calculating easement curves - you can select them with the `Select method` menu. Below is a short description of what each method does.
- Then there is the speed tolerance and minimum radius. The speed tolerance, which can either be in mph or km/h, determines how long the easement curves are. The minimum radius of curvature sets an upper limit on the curvature.
- The Curve data section is where you enter the data needed to recreate the tracks and curves.
- The `Clear` button clears away all the fields in the 'Curve data' section. The `Calculate` button does what it says on the tin.
- At the bottom is the table which gives you the curve coordinates you need to recreate the curve in Train Simulator.

Let us get started with some examples of joining up tracks with easement curves.

## Joining two straight tracks
[2]: #joining-two-straight-tracks

Suppose we have two straight tracks, and we want to create a section with easement curves of radius of curvature 3,200 m to join them. The track rule we are using has a speed tolerance of 120 mph and minimum radius of curvature 1,000 m.

![Two straight tracks](images/ig01.jpg)

1. As we need a specific radius of curvature, we select method 1. We double click on the first track - it doesn not matter where exactly, as it is the straight line which is used for the calculations. The coordinates rolls out.

   ![Clicking on track](images/ig02_1.jpg)

   ![Coordinate rollout](images/ig02_2.jpg)

2. We want the *x* and *z* coordinates `(569.349, 662.636)` and the *y*-axis rotation `73.085`, and enter them.

   ![First set of coordinates](images/gui01.jpg)

   > :information_source: In TS2016 the *x* and *z* axes are the horizontal axes, while the *y* axis is the vertical axis. This is in contrast to the standard Cartesian coordinates where *x* and *y* are the horizontal axes.

3. We also need the quadrant. Move the camera down to the track and look down the track in the direction you want to build the curve in. The compass says it is about 75 degrees between N and E, therefore the quadrant is `NE`. We enter that in.

   ![Looking down track](images/ig03.jpg)

   > :information_source: The *y*-axis rotation value is in the [-90, 90] range only, which is half that needed for the full 360 degrees range. Including the quadrant solves this problem. See the [reference](reference.md) for more on this.

   > :warning: Take care with tracks aligned towards W (*y*-axis rotation -90) or E (*y*-axis rotation 90), as the rotation values can be the same on either side of the axis.

4. We do the same thing for the second track - again, it does not matter where exactly on the track. The coordinates are `(681.732, 700.001)` and the rotation is `69.511 NE`.

   ![Second track](images/ig04.jpg)

   ![Second set of coordinates](images/gui02.jpg)

5. Finally, we enter the radius of curvature `3200` m. The direction can be left as `N/A`, as we are only interested in the shortest curve. Clicking `Calculate` gives us the results.

   ![Results](images/gui03.jpg)

   > :information_source: Picking CW or ACW will force the curve to be aligned in that direction, even if it is a much longer curve and crosses itself. By leaving it at N/A by default the curve will be aligned in the shortest direction.

6. We need to recreate the curve in Train Simulator. The start point is at `(508.235, 644.051)`, so we find that point on the first track by double clicking it until the coordinates rollout gives us the correct values.

   ![Coordinate found](images/ig05.jpg)

7. Looking straight down at the gizmo, we use the cut tool exactly where the gizmo's centre is. The extraneous section is deleted.

   ![Cutting track](images/ig06.jpg)

8. We extend an easement curve from that point to radius of curvature `3200.0`.

   ![New easement curve](images/ig07.jpg)

9. We create a curve of constant radius of curvature, that is, a static curve, and making sure it is longer than needed so we can cut it in the right place.

   ![Extending curve](images/ig08.jpg)

10. We find the end point of the static curve by looking for the right coordinates - just keep double clicking until the coordinates show `697.867` for the *x*-axis coordinate. We cut the curve at that point.

    ![Coordinate found](images/ig09.jpg)

    > :information_source: If the radius of curvature is small you can find the correct place to cut the track by looking for the  *y*-axis rotation value - but as 3,200 m is quite large the *x* and *z* position values are more accurate.

11. Finally, we extend another easement curve, straightening it out to join the second straight track.

    ![Last section](images/ig10.jpg)

    Assuming the coordinates are correct, it should weld without any problems!

## Extending a track to join another
[3]: #extending-a-straight-track

The second method calculates easement curves starting at a specific point and extended to join a straight track. The starting track can either be straight or curved, as long as it is in the same direction as the ending track. As the radius of curvature shown by Train Simulator for a track is only accurate to 1 decimal place, the tool uses an additional pair of coordinates to acquire a more accurate radius of curvature for the starting track. If the starting track is straight, the additional pair of coordinates can be left blank.

Suppose we want to extend an curved track to join with a straight track with easement curves, using a track rule with 60 mph speed tolerance and minimum radius 400 m:

![Layout](images/ig21.jpg)

1. This time, it is important where the starting coordinate is. We hover the cursor just outside the end of the bounding box for the track loft - the yellow boundary should still be visible. Double clicking gives us the coordinates right at the end of the track. We enter the coordinates `(490.146, 786.863)` and the rotation `65.067 SW`.

   ![Starting point](images/ig22.jpg)

2. For the second set of coordinates, we double click on another point on the curved track that is not too close, and enter the coordinates `(521.558, 802.368)`. The rotation/quad values are not needed here.

   ![Second point](images/ig23.jpg)

   > :information_source: It does not matter where the second pair of coordinates is, just as long as it is on the same track section with the same radius of curvature. If you are starting on a easement curve you can extend a static curve with the easement tool and pick a pair of coordinates before deleting the curve - it will work either side of the starting point.

   ![Coordinates inputted](images/gui11.jpg)

3. Finally, we enter the coordinates of the straight track - it does not matter where exactly on the track. The coordinates are `(465.935, 775.315)` and `69.148 SW`.

   ![Straight track](images/ig24.jpg)

4. Clicking `Calculate` gives us the results.

   ![Results](images/gui12.jpg)

5. Since we have already defined a start point, we can start with extending the easement curve to radius of curvature `844.4` m.

   ![Extending easement track](images/ig25.jpg)

6. Following the rest of the instructions from first example (9 onwards) should result in us joining up with the second track.

   ![Finished](images/ig26.jpg)

## Other ways of implementing the curve data
[4]: #other-ways-of-implementing-the-curve-data

The above instructions show one way to recreate the curve in Train Simulator, but it may not always work because Train Simulator will only show radius of curvature and length for tracks with one decimal place - any hidden errors when laying down the track can easily blow up and make the curve unable to join the second track.

It is for that reason the results are laid out in a table with all the data required rather than a list of instructions.

Another way of laying down the track would be to look at the coordinates for the start and the end of the static curve, and lay down two straight tracks whose ends match up with those coordinates. Then, with Train Simulator's joining tool, the static curve is formed by joining those tracks without easements. The straight tracks are deleted and new easement curves created in place, both of which should join up with the starting and ending tracks without problems.
