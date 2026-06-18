# Educational Tool: Towards Understanding Depth Perception in Foveated Rendering

**Jan Kuhta (6539653) | CGV Seminar 2026**

Interactive tool for exploring stereoscopic depth perception and foveated rendering, based on Kergaßner et al. (2025).

Optimised for a **27" 2560×1440 16:9 monitor at 60 cm viewing distance**. You'll need red-cyan anaglyph glasses for the
stereo modes.

## Setup

**Python 3.12** is required (3.13 has imgui compatibility issues).

Create a virtual environment and install dependencies:

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## External Resources

**3D Scene Asset**

- *Low-poly desert island kit* by CGTrader
- https://www.cgtrader.com/free-3d-models/exterior/landscape/low-poly-desert-island-kit
- Licence: Royalty-free
- Used as the 3D scene rendered in all modes. The island model was duplicated five times to populate the scene more
  densely.
- The 3D scene asset (`island.obj` + `island10.mtl`) is placed in:

```
external_code/assets/island.obj
external_code/assets/island10.mtl
```

**Python Libraries** (all installed via `requirements.txt`)

- `moderngl` — OpenGL context and rendering
- `glfw` — window creation and input handling
- `imgui[glfw]` — immediate-mode GUI (sidebar controls and explanation panels)
- `numpy` — vertex data and matrix math
- `trimesh` — OBJ/MTL loading
- `pyrr` — camera view and projection matrices

**Paper**

- Kergaßner et al. (2025). *Toward Understanding Depth Perception in Foveated Rendering.* ACM SIGGRAPH 2025.