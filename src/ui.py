import random
import imgui
from .explanations import MODE_EXPLANATIONS, MODE_TITLES

MODES = ["monocular", "anaglyph", "foveated", "gaze_foveated", "validation"]
MODE_LABELS = ["Monocular", "Anaglyph Stereo",
               "Fixed Foveated Anaglyph", "Gaze-Driven Foveated Anaglyph",
               "Validation Experiment"]

SIDEBAR_WIDTH = 250
EXPLANATION_HEIGHT = 300


class UIControls:
    def __init__(self):
        self.mode_index = 0
        self.ipd = 0.064
        self.blur_strength = 1.0
        self.show_heatmap = False
        self.grayscale = False

        # validation experiment
        self.stereo_left = random.choice([True, False])
        self.foveated_trial = random.choice([True, False])
        self.trials = 0
        self.correct = 0
        self.trials_fov = 0
        self.correct_fov = 0
        self.trials_sharp = 0
        self.correct_sharp = 0
        self.last_answer = None
        self.trial_state = "show"  # "show" -> user answers -> "reset" -> 2s black -> "show"
        self.flash_elapsed = 0.0

    @property
    def mode(self):
        return MODES[self.mode_index]

    def new_trial(self):
        # randomize which side gets stereo and whether the trial is foveated
        self.stereo_left = random.choice([True, False])
        self.foveated_trial = random.choice([True, False])
        self.last_answer = None
        self.trial_state = "show"  # "show" -> user answers -> "reset" -> 2s black -> "show"
        self.flash_elapsed = 0.0

    def answer(self, guessed_left: bool):
        # check answer, update counters, then immediately set up the next trial
        is_correct = (guessed_left == self.stereo_left)
        # print(f"answer: guessed_left={guessed_left}, stereo_left={self.stereo_left}, correct={is_correct}")

        self.trials += 1
        self.correct += int(is_correct)

        if self.foveated_trial:
            self.trials_fov += 1
            self.correct_fov += int(is_correct)
        else:
            self.trials_sharp += 1
            self.correct_sharp += int(is_correct)

        self.last_answer = "correct" if is_correct else "wrong"
        self.stereo_left = random.choice([True, False])
        self.foveated_trial = random.choice([True, False])
        self.trial_state = "reset"  # triggers black screen countdown in main loop
        self.flash_elapsed = 0.0


def draw_ui(ui_controls, window_width, window_height):
    draw_sidebar(ui_controls)
    draw_explanation(ui_controls, window_width, window_height)


# sidebar auto-resizes to content height — WINDOW_ALWAYS_AUTO_RESIZE handles this
def draw_sidebar(state):
    imgui.set_next_window_position(0, 0)
    imgui.set_next_window_bg_alpha(0.75)
    expanded, _ = imgui.begin("Controls", flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_AUTO_RESIZE)

    # only show sliders and other panel items for modes that actually need them

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

        if state.mode != "monocular":
            changed, new_ipd = imgui.slider_float("IPD (cm)", state.ipd, 0.0, 0.10, "%.3f")
            if changed:
                state.ipd = new_ipd

        is_foveated = state.mode in ("foveated", "gaze_foveated", "validation")

        if is_foveated:
            changed, new_blur = imgui.slider_float("Blur Strength", state.blur_strength, 0.0, 10.0, "%.1fx")
            if changed:
                state.blur_strength = new_blur

        imgui.spacing()
        _, state.grayscale = imgui.checkbox("Grayscale", state.grayscale)

        if state.mode in ("foveated", "gaze_foveated"):
            _, state.show_heatmap = imgui.checkbox("Show Foveation Heatmap", state.show_heatmap)

        imgui.spacing()

        imgui.separator()


        imgui.text("Rotate camera: A / D")

        if state.mode == "gaze_foveated":
            imgui.text("Move gaze point: Click & drag")

        if state.mode == "validation":
            draw_validation_controls(state)

        imgui.pop_item_width()

    imgui.end()


def draw_validation_controls(state):
    imgui.spacing()
    imgui.separator()
    imgui.spacing()

    imgui.spacing()
    imgui.spacing()
    imgui.text_colored("Fix gaze on red dot.", 0.9, 0.75, 0.2, 1.0)
    imgui.text("Which side has depth?")
    imgui.text_colored("Click arrow keys (LEFT, RIGHT) to answer.", 0.6, 0.6, 0.6, 1.0)

    imgui.spacing()

    if state.last_answer == "correct":
        imgui.text_colored("Correct!", 0.2, 0.9, 0.2, 1.0)
    elif state.last_answer == "wrong":
        imgui.text_colored("Wrong!", 0.9, 0.2, 0.2, 1.0)
    else:
        imgui.spacing()

    imgui.spacing()
    if state.trials > 0:
        imgui.text(f"Total:   {state.correct}/{state.trials}  ({100 * state.correct // state.trials}%)")
    else:
        imgui.text("Total: 0/0")
    if state.trials_fov > 0:
        imgui.text(f"Foveated:{state.correct_fov}/{state.trials_fov}  ({100 * state.correct_fov // state.trials_fov}%)")
    else:
        imgui.text("Foveated: 0/0")
    if state.trials_sharp > 0:
        imgui.text(
            f"Sharp:   {state.correct_sharp}/{state.trials_sharp}  ({100 * state.correct_sharp // state.trials_sharp}%)")
    else:
        imgui.text("Sharp: 0/0")


def draw_explanation(state, window_width, window_height):

    imgui.set_next_window_position(0, window_height - EXPLANATION_HEIGHT)
    imgui.set_next_window_size(window_width, EXPLANATION_HEIGHT)
    imgui.set_next_window_bg_alpha(0.75)

    expanded, _ = imgui.begin("Explanation", flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE)

    if expanded:
        imgui.push_text_wrap_pos(window_width - 20)
        imgui.text(MODE_EXPLANATIONS.get(state.mode, ""))
        imgui.pop_text_wrap_pos()
    # paper reference always shown at the bottom regardless of mode or collapse state
    imgui.separator()
    imgui.spacing()
    imgui.text_colored(
        "Paper: Kergassner et al. -- Toward Understanding Depth Perception in Foveated Rendering"
        "  (SIGGRAPH 2025)  |  https://arxiv.org/abs/2501.18635",
        0.5, 0.6, 0.8, 1.0
    )

    imgui.end()
