
# Educational Tool: Towards Understanding Depth Perception in Foveated Rendering

**Student:** Jan Kuhta (6539653)

## 1. What Was Done

An interactive educational tool was built in Python using ModernGL (OpenGL 3.3) and Dear ImGui. It renders a coloured 3D island scene and lets the user interactively switch between five rendering modes:

- **Monocular** — single eye, no stereo depth
- **Anaglyph Stereo** — red/cyan stereoscopic image viewed with anaglyph glasses
- **Fixed Foveated Anaglyph** — anaglyph with peripheral blur centred on the screen
- **Gaze-Driven Foveated Anaglyph** — same, but the sharp fovea region follows the mouse
- **Validation Experiment** — a 2AFC split-screen experiment replicating the paper's methodology

The tool runs fullscreen on a 27" 2560x1440 monitor at 60 cm viewing distance, with all perceptual parameters (fovea radius, blur falloff) derived from the literature for that physical setup.

## 2. Connection to the Paper

The paper investigates whether stereoscopic depth perception is preserved when peripheral image quality is degraded, as happens in foveated rendering. Its key finding is that observers can reliably judge binocular disparity from peripheral, heavily blurred imagery — meaning foveated rendering does not significantly impair depth perception.

The tool directly implements the paper's concepts:

- **Binocular disparity** is demonstrated via the anaglyph modes. The IPD slider lets users feel how separation between the two eye renders creates the sensation of depth.
- **Foveal masking** uses the paper's 2-degree visual angle fovea definition, translated to pixels for the target display (tan(1°) × 60 cm × 42.8 px/cm = 45 px radius, normalised to 0.0305 of the screen half-diagonal).
- **The validation experiment** replicates the 2AFC (two-alternative forced choice) paradigm from Section 4 of the paper. The screen is split into a stereo half and a flat (IPD = 0) half, randomly assigned each trial. A central region is blacked out (5° eccentricity, 225 px) to force peripheral-only judgment. The trial is either foveated or sharp, randomised, with separate score tracking for each condition.



## 3. How It Functions as an Educational Tool

The tool is designed to be used live during a presentation with the audience:

**Step 1 — Establish the baseline.** Start in Monocular mode. The scene is visible but flat. Ask the audience: *can you tell which objects are closer?* They can, but only from monocular cues (size, occlusion, perspective).

**Step 2 — Introduce disparity.** Switch to Anaglyph mode and hand out red-cyan glasses. The scene immediately pops into 3D. Moving the IPD slider from 0 upward makes the effect dramatic — showing directly how eye separation produces disparity and depth.

**Step 3 — Introduce foveation.** Switch to Fixed or Gaze-Driven Foveated mode. Enable the foveation heatmap overlay (blue = sharp, red = blurred). The audience sees exactly what quality is being rendered where, and can observe that the 3D depth sensation is largely preserved even as the periphery blurs heavily. This is the paper's core claim made visible.

**Step 4 — Run the experiment.** Switch to Validation mode. Invite a volunteer to look at the red fixation dot and judge which half has depth. Running 10–15 trials live produces a score split by foveated vs sharp trials — typically showing higher accuracy on sharp trials, but still above chance on foveated ones, matching the paper's results.

The tool makes an abstract perceptual result concrete and personally experienced, which is considerably more persuasive than a bar chart.



## Figures

**Figure 1** — *Anaglyph mode with red/cyan separation visible on the island geometry. Objects closer to the camera show wider colour fringing, demonstrating disparity directly.*

**Figure 2** — *Foveated anaglyph with heatmap overlay. Blue centre = full quality; red periphery = maximum blur. The 3D depth percept remains intact despite heavy peripheral degradation.*

**Figure 3** — *Validation experiment (2AFC). Left half shows the stereo anaglyph, right half shows a flat image with no disparity. Central region is blacked out to 5° eccentricity, forcing peripheral depth judgment.*



## External Sources and Declarations

**3D Scene Asset**  
Low-poly desert island kit — CGTrader  
URL: https://www.cgtrader.com/free-3d-models/exterior/landscape/low-poly-desert-island-kit  
Licence: Royalty-free  
Adaptation: The island model was duplicated five times to populate the scene more densely. 

**AI Assistance Declaration**  
AI tools (ChatGPT) were used for assisting with initial project structure design, debugging, and report polishing. All design decisions were developed by the author.
*
*Paper Reference**  
Kergaßner et al. (2025). *Toward Understanding Depth Perception in Foveated Rendering.* ACM SIGGRAPH 2025.