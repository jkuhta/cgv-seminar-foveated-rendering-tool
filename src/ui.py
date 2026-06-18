import random
import imgui
from src.explanations import MODE_EXPLANATIONS, MODE_TITLES

MODES       = ["monocular", "anaglyph", "foveated", "gaze_foveated", "validation"]
MODE_LABELS = ["Monocular", "Anaglyph Stereo",
               "Fixed Foveated Anaglyph", "Gaze-Driven Foveated Anaglyph",
               "Validation Experiment"]

SIDEBAR_WIDTH      = 270
EXPLANATION_HEIGHT = 200


class UIState:
    def __init__(self):
        self.mode_index    = 0
        self.ipd           = 0.064
        self.blur_strength = 45.0
        self.show_heatmap  = False
        self.grayscale     = False

        # validation experiment
        self.stereo_left    = random.choice([True, False])
        self.foveated_trial = random.choice([True, False])
        self.trials         = 0
        self.correct        = 0
        self.trials_fov     = 0
        self.correct_fov    = 0
        self.trials_sharp   = 0
        self.correct_sharp  = 0
        self.last_answer    = None
        self.trial_state    = "showing"
        self.flash_elapsed  = 0.0

    @property
    def mode(self):
        return MODES[self.mode_index]

    def new_trial(self):
        self.stereo_left    = random.choice([True, False])
        self.foveated_trial = random.choice([True, False])
        self.last_answer    = None
        self.trial_state    = "showing"
        self.flash_elapsed  = 0.0

    def answer(self, guessed_left: bool):
        is_correct = (guessed_left == self.stereo_left)
        # print(f"answer: guessed_left={guessed_left}, stereo_left={self.stereo_left}, correct={is_correct}")

        self.trials  += 1
        self.correct += int(is_correct)

        if self.foveated_trial:
            self.trials_fov  += 1
            self.correct_fov += int(is_correct)
        else:
            self.trials_sharp  += 1
            self.correct_sharp += int(is_correct)

        self.last_answer    = "correct" if is_correct else "wrong"
        self.stereo_left    = random.choice([True, False])
        self.foveated_trial = random.choice([True, False])
        self.trial_state    = "flashing"
        self.flash_elapsed  = 0.0


def draw(ui_state, window_width, window_height):
    _draw_sidebar(ui_state, window_height)
    _draw_explanation(ui_state, window_width, window_height)


def _draw_sidebar(state, window_height):
    imgui.set_next_window_position(0, 0)
    imgui.set_next_window_bg_alpha(0.75)
    expanded, _ = imgui.begin("Controls", flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_AUTO_RESIZE)

    if expanded:
        imgui.push_item_width(SIDEBAR_WIDTH - 20)

        imgui.text("Rendering Mode")
        imgui.separator()
        for i, label in enumerate(MODE_LABELS):
            if imgui.radio_button(label, state.mode_index == i):
                state.mode_index = i
        imgui.spacing()

        imgui.text("Parameters")
        imgui.separator()

        changed, new_ipd = imgui.slider_float("IPD (m)", state.ipd, 0.0, 0.10, "%.3f")
        if changed:
            state.ipd = new_ipd

        is_foveated = state.mode in ("foveated", "gaze_foveated", "validation")
        if not is_foveated:
            imgui.push_style_var(imgui.STYLE_ALPHA, 0.4)
        changed, new_blur = imgui.slider_float("Blur Strength", state.blur_strength, 0.0, 60.0, "%.1f px")
        if changed and is_foveated:
            state.blur_strength = new_blur
        if not is_foveated:
            imgui.pop_style_var()

        imgui.spacing()
        _, state.grayscale   = imgui.checkbox("Grayscale", state.grayscale)
        _, state.show_heatmap = imgui.checkbox("Show Foveation Heatmap", state.show_heatmap)
        if state.show_heatmap:
            imgui.text_colored("Blue=sharp  Green=mid  Red=blurred", 0.6, 0.8, 0.6, 1.0)

        imgui.spacing()
        imgui.text_colored("A / D — orbit camera", 0.5, 0.8, 0.5, 1.0)
        if state.mode == "gaze_foveated":
            imgui.text_colored("Click+drag — move gaze point", 0.9, 0.75, 0.2, 1.0)

        if state.mode == "validation":
            _draw_validation_controls(state)

        imgui.pop_item_width()

    imgui.end()


def _draw_validation_controls(state):
    imgui.spacing()
    imgui.separator()
    imgui.spacing()

    if state.foveated_trial:
        imgui.text_colored("Trial: FOVEATED", 0.9, 0.6, 0.1, 1.0)
    else:
        imgui.text_colored("Trial: SHARP", 0.4, 0.9, 0.4, 1.0)

    imgui.spacing()
    imgui.text("Which side has depth?")
    imgui.spacing()

    button_width = (SIDEBAR_WIDTH - 20) // 2 - 2
    if imgui.button("LEFT  (<)", width=button_width):
        state.answer(guessed_left=True)
    imgui.same_line()
    if imgui.button("RIGHT (>)", width=button_width):
        state.answer(guessed_left=False)

    imgui.spacing()
    if state.last_answer == "correct":
        imgui.text_colored("Correct!", 0.2, 0.9, 0.2, 1.0)
    elif state.last_answer == "wrong":
        imgui.text_colored("Wrong!", 0.9, 0.2, 0.2, 1.0)

    imgui.spacing()
    if state.trials > 0:
        imgui.text(f"Total:   {state.correct}/{state.trials}  ({100*state.correct//state.trials}%)")
    if state.trials_fov > 0:
        imgui.text(f"Foveated:{state.correct_fov}/{state.trials_fov}  ({100*state.correct_fov//state.trials_fov}%)")
    if state.trials_sharp > 0:
        imgui.text(f"Sharp:   {state.correct_sharp}/{state.trials_sharp}  ({100*state.correct_sharp//state.trials_sharp}%)")

    imgui.spacing()
    if imgui.button("New Trial", width=SIDEBAR_WIDTH - 20):
        state.new_trial()

    imgui.spacing()
    imgui.text_colored("Fix gaze on red dot.", 0.9, 0.75, 0.2, 1.0)
    imgui.text_colored("Click or arrow keys to answer.", 0.6, 0.6, 0.6, 1.0)

    imgui.spacing()
    if state.trial_state == "flashing":
        imgui.text_colored("Resetting...", 0.9, 0.9, 0.9, 1.0)
    else:
        imgui.text_colored("Scene visible -- click to answer.", 0.5, 0.8, 1.0, 1.0)


def _draw_explanation(state, window_width, window_height):
    imgui.set_next_window_position(0, window_height - EXPLANATION_HEIGHT)
    imgui.set_next_window_size(window_width, EXPLANATION_HEIGHT)
    imgui.set_next_window_bg_alpha(0.75)
    expanded, _ = imgui.begin("Explanation", flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE)

    if expanded:
        title = MODE_TITLES.get(state.mode, state.mode)
        imgui.text_colored(f"[ {title} ]", 0.9, 0.75, 0.2, 1.0)
        imgui.separator()
        imgui.push_text_wrap_pos(window_width - 20)
        imgui.text(MODE_EXPLANATIONS.get(state.mode, ""))
        imgui.pop_text_wrap_pos()

    imgui.end()