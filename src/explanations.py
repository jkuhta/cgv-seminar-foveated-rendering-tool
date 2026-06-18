# Educational explanation text for each rendering mode.

MONOCULAR_EXPLANATION = """MONOCULAR MODE

You are seeing the scene through a single virtual eye - no stereo depth.

Even without two eyes, you can still estimate depth from monocular cues:
- Object size: closer objects appear larger
- Occlusion: nearer objects block farther ones
- Perspective: parallel lines converge in the distance
- Shading: lighting reveals 3D shape

These cues are powerful but imprecise. Notice how the scene feels flat compared to what
you will experience in Anaglyph mode.

Press A / D to orbit the camera and explore the scene.
"""

ANAGLYPH_EXPLANATION = """ANAGLYPH STEREO MODE
!Important: For this mode you need to wear red-cyan anaglyph glasses!

This mode adds the most powerful depth cue: BINOCULAR DISPARITY.

Your two eyes are ~6.4cm apart. Each eye sees a slightly different image of the world -
the horizontal shift between them is called disparity. Your brain computes depth from
this shift automatically and effortlessly. This process is called stereopsis.

Here, two eye renders are combined into one image:
- Left eye  -> RED channel only
- Right eye -> CYAN (green + blue) channels

The glasses separate them: your left eye sees red, your right sees cyan. The brain
fuses the two views into a vivid 3D percept.

IPD (Inter-Pupillary Distance) controls the separation between the two virtual cameras.
The default 6.4cm matches the average human eye separation. Increasing IPD exaggerates
disparity and makes depth feel more dramatic, but if set too high, objects split into
two unfusable images (diplopia). Try sliding it to see the effect.
 

Try the Grayscale toggle: anaglyph glasses can cause colour crosstalk between the two
eyes, which slightly degrades the image. In grayscale, the red and cyan channels carry
only luminance, reducing crosstalk and making the binocular disparity easier to fuse."""

FOVEATED_EXPLANATION = """FIXED FOVEATED ANAGLYPH MODE
!Important: For this mode you need to wear red-cyan anaglyph glasses!

This mode demonstrates FOVEATED RENDERING -> the core technique studied in
Kergassner et al. (SIGGRAPH 2025).

Why foveation? VR rendering is expensive: two eyes, high resolution, 90fps. Foveated
rendering cuts GPU cost by up to 70% by exploiting a fundamental property of our vision.

The FOVEA is a tiny high-acuity region at the centre of your retina. Outside it, spatial sensitivity
drops off sharply. Foveated rendering exploits this: full quality only where you look,
progressively reduced quality further away.

In this mode the gaze is fixed at the screen centre. Center is rendered at high resolution, while the 
periphery gradually applies blur.

Enable Show foveation heatmap to visualise the blur distribution:
Blue = sharp (fovea), Red = blurred (periphery).
White ring = 1 deg fovea boundary. Yellow = 10 deg. Orange = 20 deg.
The blur intensity values per eccentricity are calculated from the model's p2 parameter, 
which shows the optimal blur levels per eccentricity. Blur strengths slider is 1.0 by default and 
shows the optimal blur levels. Try moving the slider to see the threshold where depth is still visible.

The paper's key finding: even with this peripheral blur, stereoscopic depth perception
is largely preserved.
"""

GAZE_FOVEATED_EXPLANATION = """GAZE-DRIVEN FOVEATED ANAGLYPH MODE
!Important: For this mode you need to wear red-cyan anaglyph glasses!

Same as Fixed Foveated, but the sharp region follows your mouse - simulating a real
eye-tracked VR headset. These headsets track your
gaze at ~120Hz and shift the high-quality region in real time.

Click and drag to move the gaze point across the scene. 

Notice that wherever you look stays sharp, while everything else blurs - yet the overall
3D depth impression remains intact. This is the core perceptual insight the paper
quantifies: the visual system extracts disparity even from blurry, low-acuity images.

You can also try it with a heatmap to see how the gaze-centred blur distribution shifts as you drag.
"""

VALIDATION_EXPLANATION = """VALIDATION EXPERIMENT (2AFC)
!Important: For this mode you need to wear red-cyan anaglyph glasses!

This mode replicates the validation study from Kergassner et al. (SIGGRAPH 2025).

The screen is split in two. One half shows a STEREO anaglyph (real IPD - binocular
disparity), the other shows a FLAT image (IPD = 0, no depth). The assignment is randomised
each trial. The central region is blacked out, forcing you to judge
depth from peripheral vision only.

Fix your gaze on the red fixation dot and try to judge which half has depth. Use the LEFT /
RIGHT arrow keys or the buttons to answer. Scores are tracked separately for SHARP trials
(no blur) and FOVEATED trials (applied blur).

The paper found no significant difference between the two conditions - observers reliably
identified the stereo side even with strong peripheral blur, validating that stereopsis
survives foveated rendering.

Try increasing Blur Strength beyond 1x. At some point accuracy on foveated trials will
start to drop - you have found the limit where blur begins to impair depth perception.
"""

MODE_TITLES = {
    "monocular": "Monocular (One Eye)",
    "anaglyph": "Anaglyph Stereo",
    "foveated": "Fixed Foveated Anaglyph",
    "gaze_foveated": "Gaze-Driven Foveated Anaglyph",
    "validation": "Validation Experiment (2AFC)",
}

MODE_EXPLANATIONS = {
    "monocular": MONOCULAR_EXPLANATION,
    "anaglyph": ANAGLYPH_EXPLANATION,
    "foveated": FOVEATED_EXPLANATION,
    "gaze_foveated": GAZE_FOVEATED_EXPLANATION,
    "validation": VALIDATION_EXPLANATION,
}
