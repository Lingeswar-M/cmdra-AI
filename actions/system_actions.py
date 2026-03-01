import os
import webbrowser
import shutil
import ctypes
import subprocess
from pathlib import Path


def _launch_app(command, success_message, error_message):
    try:
        subprocess.Popen(command, shell=True)
        return success_message
    except Exception as e:
        return f"{error_message}: {e}"


def _launch_executable(exe_name, common_paths=None, url_fallback=None):
    candidates = []
    which_path = shutil.which(exe_name)
    if which_path:
        candidates.append(which_path)
    for path in (common_paths or []):
        if path and os.path.exists(path):
            candidates.append(path)

    for exe_path in candidates:
        try:
            subprocess.Popen([exe_path], shell=False)
            return True, None
        except Exception:
            continue

    if url_fallback:
        try:
            webbrowser.open(url_fallback)
            return False, f"{exe_name} executable not found. Opened fallback URL."
        except Exception as e:
            return False, str(e)

    return False, f"{exe_name} executable not found."


def open_chrome():
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    program_files = os.environ.get("ProgramFiles", "")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "")
    paths = [
        str(Path(local_appdata) / "Google/Chrome/Application/chrome.exe"),
        str(Path(program_files) / "Google/Chrome/Application/chrome.exe"),
        str(Path(program_files_x86) / "Google/Chrome/Application/chrome.exe"),
    ]
    launched, note = _launch_executable("chrome", paths, url_fallback="https://www.google.com")
    if launched:
        return "Opening Chrome."
    if note and "fallback" in note.lower():
        return "Chrome not found. Opened Google in default browser instead."
    return f"Error opening Chrome: {note}"


def open_vscode():
    return _launch_app("code", "Opening VS Code.", "Error opening VS Code")


def open_notepad():
    return _launch_app("notepad", "Opening Notepad.", "Error opening Notepad")

def open_cmd():
    return _launch_app("start cmd", "Opening Command Prompt.", "Error opening Command Prompt")


def lock_screen():
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Locking screen."
    except Exception as e:
        return f"Error locking screen: {e}"


def open_brave():
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    program_files = os.environ.get("ProgramFiles", "")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "")
    paths = [
        str(Path(local_appdata) / "BraveSoftware/Brave-Browser/Application/brave.exe"),
        str(Path(program_files) / "BraveSoftware/Brave-Browser/Application/brave.exe"),
        str(Path(program_files_x86) / "BraveSoftware/Brave-Browser/Application/brave.exe"),
    ]
    launched, note = _launch_executable("brave", paths, url_fallback="https://www.google.com")
    if launched:
        return "Opening Brave browser."
    if note and "fallback" in note.lower():
        return "Brave not found. Opened default browser instead."
    return f"Error opening Brave: {note}"


def open_settings():
    return _launch_app("start ms-settings:", "Opening Settings.", "Error opening Settings")


def open_task_manager():
    return _launch_app("taskmgr", "Opening Task Manager.", "Error opening Task Manager")


def open_word():
    return _launch_app("start winword", "Opening Microsoft Word.", "Error opening Microsoft Word")


def open_excel():
    return _launch_app("start excel", "Opening Microsoft Excel.", "Error opening Microsoft Excel")


def open_powerpoint():
    return _launch_app("start powerpnt", "Opening Microsoft PowerPoint.", "Error opening Microsoft PowerPoint")


def show_disk_usage():
    try:
        total, used, free = shutil.disk_usage("C:\\")

        total_gb = total // (2**30)
        used_gb = used // (2**30)
        free_gb = free // (2**30)

        return (
            f"Disk Usage (C Drive):\\n"
            f"Total: {total_gb} GB\\n"
            f"Used: {used_gb} GB\\n"
            f"Free: {free_gb} GB"
        )

    except Exception as e:
        return f"Error checking disk usage: {e}"


def exit_app():
    """Signal the UI to close the running assistant app."""
    return "__EXIT_APP__"
