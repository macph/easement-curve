# Easement curve guide
## Speed tolerance

## How to find the coordinates
Every object within a Train Simulator route, including tracks and lofts, has a set of coordinates for translation, rotation and scale. They can be discovered by double clicking on the objects, which brings up a dialog on the right.

The same goes for tracks and lofts too, but you can double click on any point along the loft to get its coordinates. If you hover the cursor just outside the end of the loft's bounding box, you can get the coordinates right at the end of the loft.

The transform dialog contains entry fields for translation, rotation and scale in the `x`, `y` and `z` axes.

### Position values and the grid
The `x` and `z` axes are horiztonal and are aligned towards the North and the West respectively. They are usually relative to the grid points covering a TS2016 route, which is made up of 1,024 m x 1,024 m squares. You can tell which grid square you are in by look at the far bottom left, which shows something like `+00000000-00000001`.

You can also make grids visible by selecting this option on the left rollout:

When dealing with tracks that are far apart, you will need to bear in mind that the tracks can be positioned relative to different grid points, even if they aren't inside those grid squares. For instance, if you know that one track is near a grid square next to another south where another track is, and their coordinates don't match up with the distances shown, you would need to add 1,024 to the `z`-axis coordiante for the first track.

### Rotation values
Tracks are aligned according to their rotation values in the vertical `y`-axis. However, there are two issues with `y`-axis rotation values. Firstly, the values shown on the rollout dialog is always within the -90 to 90 range, which is half that required for a full rotation of 360 degrees. Secondly, the rotation value is relative to the direction the track was laid in, which isn't always the same as the direction you want to lay new track in. As a result, an extra coordinate is needed: the bearing quadrants `NE`, `SE`, `SW` and `NW`. 

The easiest way to find which quadrant the track is aligned towards is to pin the compass rollout dialog at the top, and look down the track. If the compass shows it's between N and E, or between the bearing values 0 and 90, the quadrant is `NE`. If it's between 90 and 180, it would be `SE`, and so on.

| Bearing    | `y`-axis rotation | Quadrant |
| ---------- | ----------------- | -------- |
| 0 to 90    | 0 to 90           | `NE`     |
| 90 to 180  | 90 to 0           | `SE`     |
| 180 to 270 | 0 to -90          | `SW`     |
| 270 to 360 | -90 to 0          | `NW`     |

## Method
There are different ways of defining the easement curves you want to join the tracks with, and I've split them up into different methods. You can select different methods by picking an option from the 'Select Method' menu.

### Method 1: set radius of curvature between two straight tracks
### Method 2: set static curve length between two straight tracks
### Method 3: extend track to join another

## Implementing the curve
Entering the coordinates and clicking `Calculate` will give you a table with different sections of the curve and their coordinates. There are many different ways to implement the curve in TS2016 based on these coordinates, and one is outlined below with an example easement curve section.

| Curve section    | Length | Radius of curvature  | Position `x` | Position `z` | Rotation | Quad |
| ---------------- | ------:| -------------------- | ------------:| ------------:| --------:| ---- |
| Start point      |        | Straight             | 231.643      | 47.282       | 48.882   | `NE` |
| Easement curve 1 | 86.0   | Straight to 600.0 CW | 297.726      | 102.241      | 52.990   | `NE` |
| Static curve     | 192.2  | 600.0 CW             | 466.933      | 191.584      | 71.341   | `NE` |
| Easement curve 2 | 86.0   | 600.0 CW to straight | 594.587      | 215.159      | 75.449   | `NE` |

- If methods 1 or 2 are used, double click on the first straight track to find the exact point `(231.643, 47.282)` where the easement curve starts. Cut the track at that point and delete the extranenous section.
- Create an easement curve from the start point to radius of curvature `600.0` clockwise.
- Create a curve of constant curvature `600.0` (static curve). To make sure it ends in the right place, the static curve is longer than it needs to be.
- Find the point on the static curve with the specific rotation value `71.341 NE` where it ends. Cut the track and delete the extranenous section.
- Finally, extend another easement curve and straighten it out. If the track sections are in the correct places, it should automatically join with the second track.

## Troubleshooting

Pictures too!