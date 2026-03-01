import pyautogui
import screen_brightness_control as sbc


# 1️⃣ Play / Pause
def play_music():
    pyautogui.press("playpause")
    return "Toggled play/pause."


def pause_music():
    pyautogui.press("playpause")
    return "Toggled play/pause."


# 2️⃣ Increase Volume
def increase_volume():
    for _ in range(5):
        pyautogui.press("volumeup")
    return "Volume increased."


# 3️⃣ Decrease Volume
def decrease_volume():
    for _ in range(5):
        pyautogui.press("volumedown")
    return "Volume decreased."


# 4️⃣ Increase Brightness
def increase_brightness(step=10):
    try:
        current = sbc.get_brightness()[0]
        sbc.set_brightness(min(current + step, 100))
        return "Brightness increased."
    except Exception as e:
        return f"Brightness error: {e}"


# 5️⃣ Decrease Brightness
def decrease_brightness(step=10):
    try:
        current = sbc.get_brightness()[0]
        sbc.set_brightness(max(current - step, 0))
        return "Brightness decreased."
    except Exception as e:
        return f"Brightness error: {e}"


# 6️⃣ Virtual Typing
def type_text(text):
    try:
        pyautogui.write(text, interval=0.05)
        return "Typed the requested text."
    except Exception as e:
        return f"Typing error: {e}"
