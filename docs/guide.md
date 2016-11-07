# Easement curve guide

- Introduction
- Joining two straight tracks with a specific radius of curvature
- Extending a track to join another straight track

## Introduction

Starting up the GUI gives you this:

There are two methods of calculating easement curves - you can select them with the 'Select method' menu. Below is a short description of what each method does.

Then there is the speed tolerance and minimum radius. The speed tolerance determines how long the easement curves are, and it scales linearlly - if you double the speed tolerance the length between specific radii of curvature is also doubled. The minimum radius of curvature sets an upper limit on the curvature.

The `Clear` button clears away all the fields in the 'Curve data' section. The `Calculate` button does what it says on the tin.

At the bottom is the table which gives you the easement curve coordinates you need to recreate the curve in Train Simulator.

Let's get started with some examples of joining up tracks with easement curves.

## Joining two straight tracks with a specific radius of curvature

Suppose we have two straight tracks, and we want to create a section with easement curves of radius of curvature 700 m to join them. The track rule we're using has a speed tolerance of 100 km/h and minimum radius of curvature 600 m.

Since we need a specific radius of curvature and it doesn't matter where the easement curve starts, we select method 1.

We double click on the first track - it doesn't matter where exactly. The coordinates rolls out.

We want the `x` and `z` coordinates and the `y`-axis rotation, and enter them.

We also need the quadrant - the `y`-axis rotation values does not cover the full 360 degrees range. Move the camera down to the track and look down the track in the direction you want to build the curve in. The compass says it's about `000` between `N` and `E`, therefore the quadrant is `NE`. We enter that in.

We do the same thing for the second track - again, it doesn't matter where exactly on the track.

Finally, we enter the radius of curvature `700` m. The direction can be left as `N/A`, as we're only interested in the shortest curve. Clicking `Calculate` gives us the results.

Now, we need to recreate the curve in Train Simulator. The start point is at `(000, 000)`, so we find that point on the first track by double clicking it until the coordinates rollout gives us the correct values.

Looking straight down at the gizmo, we move the cursor to the gizmo's centre and use the cut tool to split the track. The extranenous section is deleted.

We extend an easement curve from that point to radius of curvature `700.0`, and create another curve of constant radius of curvature, making sure it is longer than needed (so we can cut it in the right place).

We use the alignment of the static curve to find the end point of the static curve - just keep double clicking until the coordinates show `0.000` for the `y`-axis rotation. We cut the curve at that point, as before.

Finally, we extend another easement curve, straightening it out to join the second straight track. Assuming the coordinates are correct, it should weld without any problems!

## Extending a track to join another straight track

## Other ways of implementing the curve data