# Foveated Rendering Demo

An interactive educational tool built for the paper:

> **Towards Understanding Depth Perception in Foveated Rendering**  
> Kergaßner, Tariq, Didyk — SIGGRAPH 2025

The demo renders a simple 3D scene in stereo, applies foveated blur driven
by the mouse position (simulating gaze-tracked rendering), and lets you
interactively explore how strongly you can blur the periphery before depth
perception breaks down. Spoiler: it takes a lot more blur than you'd expect.

---

## What it shows

Move your mouse around the scene. Blur radiates outward from wherever you're
looking — sharp at the centre, increasingly blurry toward the edges. This is
exactly what a VR headset does using eye tracking to save GPU time.

The key finding from the paper: even at **2× the blur level** that current
foveated rendering systems use, stereoscopic depth perception remains
completely intact. The scene is rendered in wiggle-stereo (left/right eye
images alternating at 3 Hz) so depth is visible without any special glasses.

---

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Requires Python 3.10+ and a GPU that supports OpenGL 3.3.

---

## Controls

| Input | Action |
|---|---|
| Mouse move | Set gaze point — blur follows |
| `0` | No blur |
| `1` | Paper model (safe threshold) |
| `2` | 2× model — still fine per the paper |
| `3` | 3× model — now you start to notice |
| Drag the bottom bar | Continuously adjust blur multiplier |
| `H` | Toggle HUD |
| `Q` / `Esc` | Quit |

---

## Project structure

```
fov/
├── app.py              Entry point. Window, input, main loop.
├── config.py           All constants — window size, FOV, IPD, wiggle speed.
├── requirements.txt
│
├── core/
│   ├── renderer.py     Owns all OpenGL objects. Executes the render pipeline.
│   └── scene.py        3D geometry: floor plane, boxes at various depths.
│
└── shaders/
    ├── scene.vert      3D geometry vertex shader.
    ├── scene.frag      Diffuse lighting + checkerboard floor.
    ├── post.vert       Shared fullscreen triangle (used by blur + composite).
    ├── blur.frag       Foveated Gaussian blur — sigma grows with eccentricity.
    └── composite.frag  Wiggle stereo output + gaze marker + HUD slider.
```

---

## Render pipeline

Each frame runs five passes:

```
1. Scene → FBO (left eye,  camera offset -IPD/2)
2. Scene → FBO (right eye, camera offset +IPD/2)
3. H-blur → FBO  (left)     ┐  separable Gaussian,
4. V-blur → FBO  (left)     │  sigma per pixel from
   H-blur → FBO  (right)    │  paper Equation 6
   V-blur → FBO  (right)    ┘
5. Composite → screen  (wiggle + gaze dot + HUD)
```

Stereo comes naturally from rendering with two cameras separated by the IPD
(~65 mm). No pixel-shifting tricks needed for a real 3D scene.

---

## The blur model

The blur amount at each pixel follows the paper's perceptual model
(Equation 6, p₂ term):

```
sigma(theta) = max(0,  8.85 * exp(0.04 * theta) - 7.5)  [arc-minutes]
```

where `theta` is the eccentricity in degrees — how far the pixel is from the
gaze point. This gives the blur level at which stereoacuity is *best*, i.e.
the maximum safe blur that doesn't degrade depth perception. The slider
multiplies this value (0× = off, 1× = model, 2× = double, 3× = triple).

---

## Extending the demo

A few natural next steps, roughly in order of effort:

- **Anaglyph mode** — one extra branch in `composite.frag`, one key binding
  in `app.py`. Works well for grayscale content and lets an audience experience
  stereo with cheap red-cyan glasses.

- **Spatial vs stereo comparison** — split the screen: left half shows a
  sharpness test (fine grating) degrading with blur, right half shows depth
  remaining intact. Same blur slider drives both.

- **Interactive model surface** — run `python model_explorer.py` (to be added)
  to show the full M(θ, σ) threshold surface from the paper as a 3D Plotly
  plot, with existing foveation methods overlaid.

- **Webcam eye tracking** — replace mouse position with gaze estimated from
  a webcam using MediaPipe Face Mesh. Swap one function in `app.py`.

---

## Dependencies

| Package | Purpose |
|---|---|
| `moderngl` | Python OpenGL wrapper |
| `moderngl-window` | Window creation and input |
| `numpy` | Matrix and vertex data |
| `pyrr` | Camera matrices (perspective, look-at) |
