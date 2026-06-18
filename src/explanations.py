# Educational explanation text for each rendering mode.

MONOCULAR_EXPLANATION = """MONOCULAR MODE

You are seeing the scene through a single virtual eye.

With only one eye, depth cues come from:
- Object size (near objects appear larger)
- Occlusion (near objects block far ones)
- Perspective (parallel lines converge)

Notice that while you can estimate depth from context,
there is no BINOCULAR DISPARITY -- the geometric difference
between left and right eye views that gives us strong,
reliable depth perception.

Press A/D to orbit the camera and explore the scene.
"""

ANAGLYPH_EXPLANATION = """ANAGLYPH STEREO MODE

Both eye views are combined into a single image:
- LEFT eye image  -> RED channel
- RIGHT eye image -> CYAN (Green + Blue) channels

If you have red-cyan anaglyph glasses, put them on now.
Your left eye (red lens) sees only the red channel,
your right eye (cyan lens) sees only the cyan channel.

Your brain receives two slightly different images and
fuses them into a single perception of depth.

Without glasses, you can still see the colour fringing
around objects. Objects with the most fringing have the
most disparity = closest depth.
"""

FOVEATED_EXPLANATION = """FIXED FOVEATED ANAGLYPH MODE

The centre of your screen (fovea region) stays sharp.
The periphery is progressively blurred.

Why this works:
Your retina has a small high-resolution region called
the FOVEA (about 2 degrees of visual angle). Outside
it, your vision drops off sharply.

The paper's key finding: even with peripheral blur,
STEREOSCOPIC DEPTH PERCEPTION is largely preserved.

Adjust Blur Strength to explore how much blur you can
add before depth perception breaks down.
"""

GAZE_FOVEATED_EXPLANATION = """GAZE-DRIVEN FOVEATED ANAGLYPH MODE

Same as Fixed Foveated, but the sharp fovea region
follows your mouse cursor -- simulating a real eye-tracked
VR headset (Quest Pro, PSVR2, Apple Vision Pro).

Click and drag to move the gaze point. Notice:
- The reticle (red dot + corner brackets) marks the fovea
- Everything outside blurs progressively
- Stereoscopic depth cues remain perceptible even
  in the blurred periphery -- the paper's core finding.

This is why foveated rendering can cut GPU cost by
50-70% with minimal perceptual quality loss.
"""

VALIDATION_EXPLANATION = """VALIDATION EXPERIMENT MODE

Replicates the 2AFC forced-choice validation from
Kergassner et al. (SIGGRAPH 2025).

The screen is split in two. One half shows a STEREO
anaglyph (real IPD), the other shows a FLAT image
(IPD = 0, no disparity). The assignment is randomised.

The fovea is blacked out -- you must judge depth using
PERIPHERAL VISION only, exactly as in foveated rendering.

Fix your gaze on the red dot. Press LEFT or RIGHT (or
use the arrow keys) to indicate which half has depth.

The paper found observers reliably identified the stereo
side even with significant peripheral blur, validating
that stereopsis survives foveated rendering.
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
