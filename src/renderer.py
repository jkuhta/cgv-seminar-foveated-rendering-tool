import moderngl
import numpy as np
from pathlib import Path

from src.scene import fullscreen_quad, build_scene

SHADER_DIR = Path(__file__).parent / "shaders"

LIGHT_POS     = (4.0, 6.0, 5.0)
DIVIDER_WIDTH = 45.0   # px — 1deg fovea radius on 27" at 60cm
FOVEA_RADIUS  = 225.0  # px — 5deg eccentricity blackout


def _load_shader(filename):
    return (SHADER_DIR / filename).read_text()


class Renderer:
    def __init__(self, ctx: moderngl.Context, width: int, height: int):
        self.ctx    = ctx
        self.width  = width
        self.height = height
        self._build_programs_and_vaos()
        self._build_framebuffers()

    def _build_programs_and_vaos(self):
        ctx        = self.ctx
        scene_vert = _load_shader("scene_vert.glsl")
        quad_vert  = _load_shader("quad_vert.glsl")

        self.scene_program = ctx.program(
            vertex_shader=scene_vert,
            fragment_shader=_load_shader("scene_frag.glsl"),
        )

        quad_verts, quad_indices = fullscreen_quad()
        quad_vbo = ctx.buffer(quad_verts.tobytes())
        quad_ibo = ctx.buffer(quad_indices.tobytes())

        def make_quad_vao(program):
            return ctx.vertex_array(program, [(quad_vbo, "2f 2f", "in_position", "in_uv")], quad_ibo)

        # one entry per post-processing pass
        post_processing_passes = [
            ("blit",       "blit_frag.glsl"),
            ("anaglyph",   "anaglyph_frag.glsl"),
            ("foveated",   "foveated_frag.glsl"),
            ("reticle",    "reticle_frag.glsl"),
            ("heatmap",    "heatmap_frag.glsl"),
            ("validation", "validation_frag.glsl"),
        ]
        for pass_name, frag_file in post_processing_passes:
            program = ctx.program(vertex_shader=quad_vert, fragment_shader=_load_shader(frag_file))
            setattr(self, f"prog_{pass_name}", program)
            setattr(self, f"vao_{pass_name}",  make_quad_vao(program))

        scene_data = build_scene()
        scene_vbo  = ctx.buffer(scene_data.tobytes())
        self.scene_vao = ctx.vertex_array(
            self.scene_program,
            [(scene_vbo, "3f 3f 3f", "in_position", "in_normal", "in_color")],
        )

    def _build_framebuffers(self):
        w, h = self.width, self.height

        def make_fbo():
            color_texture = self.ctx.texture((w, h), components=3)
            color_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            depth_buffer = self.ctx.depth_renderbuffer((w, h))
            fbo = self.ctx.framebuffer([color_texture], depth_buffer)
            return fbo, color_texture

        self.fbo_left,      self.tex_left      = make_fbo()
        self.fbo_right,     self.tex_right     = make_fbo()
        self.fbo_anaglyph,  self.tex_anaglyph  = make_fbo()
        self.fbo_flat,      self.tex_flat      = make_fbo()
        self.fbo_flat_anag, self.tex_flat_anag = make_fbo()

    def render(self, camera, mode: str, ipd: float,
               blur_strength: float, viewport: tuple,
               gaze: tuple = (0.5, 0.5),
               stereo_left: bool = True,
               foveated_trial: bool = True,
               grayscale: bool = False,
               show_heatmap: bool = False):

        vx, vy, vw, vh = viewport
        aspect_ratio   = vw / vh if vh > 0 else 1.0

        # render scene from each eye into its own FBO
        self.render_scene_to_fbo(self.fbo_left, camera, -ipd / 2, aspect_ratio, vw, vh, grayscale)
        if mode != "monocular":
            self.render_scene_to_fbo(self.fbo_right, camera, +ipd / 2, aspect_ratio, vw, vh, grayscale)
        if mode == "validation":
            self.render_scene_to_fbo(self.fbo_flat, camera, 0.0, aspect_ratio, vw, vh, grayscale)

        self.ctx.screen.use()
        self.ctx.viewport = (vx, vy, vw, vh)

        if mode == "monocular":
            self.blit(self.tex_left)

        elif mode == "anaglyph":
            self.composite_anaglyph(self.tex_left, self.tex_right)

        elif mode == "validation":
            self._render_validation_experiment(blur_strength, vw, vh, stereo_left, foveated_trial)
            self.render_reticle(vw, vh, gaze_uv=(0.5, 0.5))

        elif mode in ("foveated", "gaze_foveated"):
            # composite anaglyph into intermediate FBO first, then blur
            self.fbo_anaglyph.use()
            self.ctx.viewport = (0, 0, vw, vh)
            self.fbo_anaglyph.clear(0.0, 0.0, 0.0)
            self.composite_anaglyph(self.tex_left, self.tex_right)

            self.ctx.screen.use()
            self.ctx.viewport = (vx, vy, vw, vh)
            self.render_foveated_blur(self.tex_anaglyph, blur_strength, vw, vh, gaze)
            self.render_reticle(vw, vh, gaze_uv=gaze)

        if show_heatmap:
            self.ctx.screen.use()
            self.ctx.viewport = (vx, vy, vw, vh)
            heatmap_gaze = (0.5, 0.5) if mode == "foveated" else gaze
            self._render_heatmap(vw, vh, heatmap_gaze)

    def render_scene_to_fbo(self, fbo, camera, lateral_offset, aspect_ratio, vw, vh, grayscale):
        fbo.use()
        self.ctx.viewport = (0, 0, vw, vh)
        fbo.clear(0.05, 0.05, 0.08)
        self.ctx.enable(moderngl.DEPTH_TEST)

        eye_position = camera.eye_world_pos(lateral_offset)
        self.scene_program["u_model"].write(np.eye(4, dtype=np.float32).tobytes())
        self.scene_program["u_view"].write(camera.view_matrix(lateral_offset).tobytes())
        self.scene_program["u_proj"].write(camera.projection_matrix(aspect_ratio).tobytes())
        self.scene_program["u_light_pos"].value = LIGHT_POS
        self.scene_program["u_view_pos"].value  = tuple(eye_position)
        self.scene_program["u_grayscale"].value = 1 if grayscale else 0

        self.scene_vao.render(moderngl.TRIANGLES)
        self.ctx.disable(moderngl.DEPTH_TEST)

    def blit(self, source_texture):
        source_texture.use(location=0)
        self.prog_blit["u_tex"] = 0
        self.vao_blit.render(moderngl.TRIANGLES)

    def composite_anaglyph(self, left_eye_texture, right_eye_texture):
        left_eye_texture.use(location=0)
        right_eye_texture.use(location=1)
        self.prog_anaglyph["u_left"]  = 0
        self.prog_anaglyph["u_right"] = 1
        self.vao_anaglyph.render(moderngl.TRIANGLES)

    def render_foveated_blur(self, source_texture, blur_strength, vw, vh, gaze_uv):
        source_texture.use(location=0)
        self.prog_foveated["u_tex"]           = 0
        self.prog_foveated["u_resolution"]    = (float(vw), float(vh))
        self.prog_foveated["u_blur_strength"] = blur_strength
        self.prog_foveated["u_gaze"]          = (float(gaze_uv[0]), float(gaze_uv[1]))
        self.vao_foveated.render(moderngl.TRIANGLES)

    def render_reticle(self, vw, vh, gaze_uv):
        self.prog_reticle["u_resolution"] = (float(vw), float(vh))
        self.prog_reticle["u_gaze"]       = (float(gaze_uv[0]), float(gaze_uv[1]))
        self.prog_reticle["u_dot_radius"] = 8.0
        self.vao_reticle.render(moderngl.TRIANGLES)

    def _render_validation_experiment(self, blur_strength, vw, vh, stereo_left, foveated_trial):
        # stereo anaglyph side
        self.fbo_anaglyph.use()
        self.ctx.viewport = (0, 0, vw, vh)
        self.fbo_anaglyph.clear(0.0, 0.0, 0.0)
        self.composite_anaglyph(self.tex_left, self.tex_right)

        # flat (no disparity) side — same image for both eyes
        self.fbo_flat_anag.use()
        self.ctx.viewport = (0, 0, vw, vh)
        self.fbo_flat_anag.clear(0.0, 0.0, 0.0)
        self.composite_anaglyph(self.tex_flat, self.tex_flat)

        self.ctx.screen.use()
        self.tex_anaglyph.use(location=0)
        self.tex_flat_anag.use(location=1)
        self.prog_validation["u_stereo"]        = 0
        self.prog_validation["u_flat"]          = 1
        self.prog_validation["u_stereo_left"]   = 1 if stereo_left else 0
        self.prog_validation["u_resolution"]    = (float(vw), float(vh))
        self.prog_validation["u_blur_strength"] = blur_strength if foveated_trial else 0.0
        self.prog_validation["u_divider_width"] = DIVIDER_WIDTH
        self.prog_validation["u_fovea_px"]      = FOVEA_RADIUS
        self.vao_validation.render(moderngl.TRIANGLES)

    def _render_heatmap(self, vw, vh, gaze_uv, opacity=0.6):
        self.prog_heatmap["u_resolution"] = (float(vw), float(vh))
        self.prog_heatmap["u_gaze"]       = (float(gaze_uv[0]), float(gaze_uv[1]))
        self.prog_heatmap["u_opacity"]    = opacity
        self.vao_heatmap.render(moderngl.TRIANGLES)

    def resize(self, new_width, new_height):
        # self.build_programs_and_vaos()
        self.width  = new_width
        self.height = new_height
        for fbo in [self.fbo_left, self.fbo_right, self.fbo_anaglyph, self.fbo_flat, self.fbo_flat_anag]:
            fbo.release()
        for tex in [self.tex_left, self.tex_right, self.tex_anaglyph, self.tex_flat, self.tex_flat_anag]:
            tex.release()
        self._build_framebuffers()