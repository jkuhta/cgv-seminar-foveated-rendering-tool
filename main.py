import time
import glfw
import moderngl
import imgui
from imgui.integrations.glfw import GlfwRenderer

from src.camera import Camera
from src.renderer import Renderer
from src.ui import UIControls, draw_ui

ROTATE_SPEED = 60.0
FLASH_DURATION = 2.0


def create_window():
    if not glfw.init():
        raise RuntimeError("GLFW failed to init")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    glfw.window_hint(glfw.MAXIMIZED, True)

    window = glfw.create_window(
        2560, 1440,
        "Towards Understanding Depth Perception in Foveated Rendering - Educational Tool",
        None, None,
    )
    if not window:
        glfw.terminate()
        raise RuntimeError("Window creation failed")

    glfw.make_context_current(window)
    glfw.swap_interval(1)  # vsync
    return window


def handle_keyboard(window, camera, ui_controls, dt, key_state):
    if imgui.get_io().want_capture_keyboard:
        return

    # rotations (A, D)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.rotate(-ROTATE_SPEED * dt)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.rotate(+ROTATE_SPEED * dt)

    # validation answers (LEFT, RIGHT)
    if ui_controls.mode == "validation" and ui_controls.trial_state == "show":

        left_pressed = glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS
        right_pressed = glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS

        if left_pressed and not key_state["left"]:
            ui_controls.answer(guessed_left=True)
        elif right_pressed and not key_state["right"]:
            ui_controls.answer(guessed_left=False)
        key_state["left"] = left_pressed
        key_state["right"] = right_pressed


def update_validation_timer(ui_controls, dt):
    # show black screen between trials
    if ui_controls.mode == "validation" and ui_controls.trial_state == "reset":
        ui_controls.flash_elapsed += dt
        if ui_controls.flash_elapsed >= FLASH_DURATION:
            ui_controls.new_trial()


def update_gaze_from_mouse(ui_controls, mouse_pos, drag_active, gaze_uv):
    # update gaze position from mousse position
    if (ui_controls.mode == "gaze_foveated"
            and drag_active[0]
            and not imgui.get_io().want_capture_mouse):
        gaze_uv[0] = mouse_pos[0]
        gaze_uv[1] = mouse_pos[1]


def draw_frame(ctx, renderer, camera, ui_controls, framebuffer_width, framebuffer_height, gaze_uv, imgui_impl):
    gaze_position = (0.5, 0.5) if ui_controls.mode == "foveated" else tuple(gaze_uv)

    ctx.viewport = (0, 0, framebuffer_width, framebuffer_height)

    # show black screen between trials so the previous image does not bleed into the next
    if ui_controls.mode == "validation" and ui_controls.trial_state == "reset":
        ctx.clear(0.0, 0.0, 0.0)
        ctx.screen.use()
        renderer.render_reticle(framebuffer_width, framebuffer_height, gaze_uv=(0.5, 0.5))
    # render normal scene
    else:
        renderer.render(
            camera=camera,
            mode=ui_controls.mode,
            ipd=ui_controls.ipd,
            blur_strength=ui_controls.blur_strength,
            viewport=(0, 0, framebuffer_width, framebuffer_height),
            gaze=gaze_position,
            stereo_left=ui_controls.stereo_left,
            foveated_trial=ui_controls.foveated_trial,
            grayscale=ui_controls.grayscale,
            show_heatmap=ui_controls.show_heatmap,
        )

    ctx.viewport = (0, 0, framebuffer_width, framebuffer_height)
    imgui.render()
    imgui_impl.render(imgui.get_draw_data())


def main():
    window = create_window()
    ctx = moderngl.create_context()
    ctx.enable(moderngl.BLEND)  # needed for reticle and heatmap alpha blending
    ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

    imgui.create_context()
    io = imgui.get_io()
    io.font_global_scale = 1.5
    imgui_impl = GlfwRenderer(window)  # imgui backend that hooks into GLFW events

    camera = Camera()
    ui_controls = UIControls()
    # renderer needs framebuffer size upfront to allocate FBOs at the right resolution
    renderer = Renderer(ctx, *glfw.get_framebuffer_size(window))

    framebuffer_width, framebuffer_height = glfw.get_framebuffer_size(window)
    window_width, window_height = glfw.get_window_size(window)

    gaze_uv = [0.5, 0.5]  # normalised UV, starts at screen centre
    mouse_pos = [0.5, 0.5]  # raw mouse position, always tracked
    mouse_down = [False]  # is left button held?
    drag_active = [False]  # did the mouse move while held? (distinguishes click from drag)
    key_state = {"left": False, "right": False}

    def on_resize(win, w, h):
        nonlocal framebuffer_width, framebuffer_height, window_width, window_height
        framebuffer_width, framebuffer_height = glfw.get_framebuffer_size(win)
        window_width, window_height = glfw.get_window_size(win)
        renderer.resize(framebuffer_width, framebuffer_height)

    def on_cursor_moved(win, xpos, ypos):
        w, h = glfw.get_window_size(win)
        mouse_pos[0] = xpos / w
        mouse_pos[1] = 1.0 - ypos / h  # flip Y: GLFW origin is top-left, UV origin is bottom-left
        if mouse_down[0]:
            drag_active[0] = True

    def on_mouse_button(win, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                mouse_down[0] = True
                drag_active[0] = False
            else:
                mouse_down[0] = False
                drag_active[0] = False

        if (action == glfw.PRESS
                and ui_controls.mode == "validation"
                and ui_controls.trial_state == "show"
                and not imgui.get_io().want_capture_mouse):
            if button == glfw.MOUSE_BUTTON_LEFT:
                ui_controls.answer(guessed_left=True)
            elif button == glfw.MOUSE_BUTTON_RIGHT:
                ui_controls.answer(guessed_left=False)

    glfw.set_framebuffer_size_callback(window, on_resize)
    glfw.set_cursor_pos_callback(window, on_cursor_moved)
    glfw.set_mouse_button_callback(window, on_mouse_button)

    last_time = time.time()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        imgui_impl.process_inputs()

        now = time.time()
        dt = now - last_time
        last_time = now

        handle_keyboard(window, camera, ui_controls, dt, key_state)
        update_validation_timer(ui_controls, dt)

        imgui.new_frame()
        draw_ui(ui_controls, window_width, window_height)

        update_gaze_from_mouse(ui_controls, mouse_pos, drag_active, gaze_uv)
        # print(f"gaze: {gaze_uv}, mode: {ui_controls.mode}")
        draw_frame(ctx, renderer, camera, ui_controls,
                   framebuffer_width, framebuffer_height, gaze_uv, imgui_impl)

        glfw.swap_buffers(window)

    imgui_impl.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    main()
