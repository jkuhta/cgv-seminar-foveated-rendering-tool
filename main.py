import time
import glfw
import moderngl
import imgui
from imgui.integrations.glfw import GlfwRenderer

from src.camera import Camera
from src.renderer import Renderer
from src.ui import UIState, draw as draw_ui

ROTATE_SPEED   = 60.0
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
    glfw.swap_interval(1)
    return window


def setup_opengl(window):
    ctx = moderngl.create_context()
    ctx.enable(moderngl.BLEND)
    ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
    return ctx


def handle_keyboard(window, camera, ui_state, dt, key_state):
    if imgui.get_io().want_capture_keyboard:
        return

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.rotate(-ROTATE_SPEED * dt)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.rotate(+ROTATE_SPEED * dt)

    # arrow keys for validation — detect single press, not hold
    if ui_state.mode == "validation" and ui_state.trial_state == "showing":
        left_pressed  = glfw.get_key(window, glfw.KEY_LEFT)  == glfw.PRESS
        right_pressed = glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS
        if left_pressed and not key_state["left"]:
            ui_state.answer(guessed_left=True)
        elif right_pressed and not key_state["right"]:
            ui_state.answer(guessed_left=False)
        key_state["left"]  = left_pressed
        key_state["right"] = right_pressed


def update_validation_timer(ui_state, dt):
    if ui_state.mode == "validation" and ui_state.trial_state == "flashing":
        ui_state.flash_elapsed += dt
        if ui_state.flash_elapsed >= FLASH_DURATION:
            ui_state.new_trial()


# TODO: could also support scroll wheel for zoom
def update_gaze_from_mouse(ui_state, mouse_pos, drag_active, gaze_uv):
    if (ui_state.mode == "gaze_foveated"
            and drag_active[0]
            and not imgui.get_io().want_capture_mouse):
        gaze_uv[0] = mouse_pos[0]
        gaze_uv[1] = mouse_pos[1]


def draw_frame(ctx, renderer, camera, ui_state, framebuffer_width, framebuffer_height, gaze_uv, imgui_impl):
    gaze_position = (0.5, 0.5) if ui_state.mode == "foveated" else tuple(gaze_uv)

    ctx.viewport = (0, 0, framebuffer_width, framebuffer_height)

    # black screen between validation trials
    if ui_state.mode == "validation" and ui_state.trial_state == "flashing":
        ctx.clear(0.0, 0.0, 0.0)
        ctx.screen.use()
        renderer.render_reticle(framebuffer_width, framebuffer_height, gaze_uv=(0.5, 0.5))
    else:
        ctx.clear(0.08, 0.08, 0.10)
        renderer.render(
            camera=camera,
            mode=ui_state.mode,
            ipd=ui_state.ipd,
            blur_strength=ui_state.blur_strength,
            viewport=(0, 0, framebuffer_width, framebuffer_height),
            gaze=gaze_position,
            stereo_left=ui_state.stereo_left,
            foveated_trial=ui_state.foveated_trial,
            grayscale=ui_state.grayscale,
            show_heatmap=ui_state.show_heatmap,
        )

    ctx.viewport = (0, 0, framebuffer_width, framebuffer_height)
    imgui.render()
    imgui_impl.render(imgui.get_draw_data())


def main():
    window = create_window()
    ctx    = setup_opengl(window)

    imgui.create_context()
    imgui_impl = GlfwRenderer(window)

    camera   = Camera()
    ui_state = UIState()
    renderer = Renderer(ctx, *glfw.get_framebuffer_size(window))

    framebuffer_width, framebuffer_height = glfw.get_framebuffer_size(window)
    window_width, window_height           = glfw.get_window_size(window)

    gaze_uv     = [0.5, 0.5]
    mouse_pos   = [0.5, 0.5]
    mouse_down  = [False]
    drag_active = [False]
    key_state   = {"left": False, "right": False}

    def on_resize(win, w, h):
        nonlocal framebuffer_width, framebuffer_height, window_width, window_height
        framebuffer_width, framebuffer_height = glfw.get_framebuffer_size(win)
        window_width, window_height           = glfw.get_window_size(win)
        renderer.resize(framebuffer_width, framebuffer_height)

    def on_cursor_moved(win, xpos, ypos):
        w, h = glfw.get_window_size(win)
        mouse_pos[0] = xpos / w
        mouse_pos[1] = 1.0 - ypos / h
        if mouse_down[0]:
            drag_active[0] = True

    def on_mouse_button(win, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                mouse_down[0]  = True
                drag_active[0] = False
            else:
                mouse_down[0]  = False
                drag_active[0] = False

        if (action == glfw.PRESS
                and ui_state.mode == "validation"
                and ui_state.trial_state == "showing"
                and not imgui.get_io().want_capture_mouse):
            if button == glfw.MOUSE_BUTTON_LEFT:
                ui_state.answer(guessed_left=True)
            elif button == glfw.MOUSE_BUTTON_RIGHT:
                ui_state.answer(guessed_left=False)

    glfw.set_framebuffer_size_callback(window, on_resize)
    glfw.set_cursor_pos_callback(window, on_cursor_moved)
    glfw.set_mouse_button_callback(window, on_mouse_button)

    last_time = time.time()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        imgui_impl.process_inputs()

        now       = time.time()
        dt        = now - last_time
        last_time = now

        handle_keyboard(window, camera, ui_state, dt, key_state)
        update_validation_timer(ui_state, dt)

        imgui.new_frame()
        draw_ui(ui_state, window_width, window_height)

        update_gaze_from_mouse(ui_state, mouse_pos, drag_active, gaze_uv)
        # print(f"gaze: {gaze_uv}, mode: {ui_state.mode}")
        draw_frame(ctx, renderer, camera, ui_state,
                   framebuffer_width, framebuffer_height, gaze_uv, imgui_impl)

        glfw.swap_buffers(window)

    imgui_impl.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    main()