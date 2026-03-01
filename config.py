import os
import sys

# ==========================================
# UI SETTINGS
# ==========================================
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
ALWAYS_ON_TOP = True
WINDOW_OPACITY = 1.0
THEME_MODE = "dark"

BG_COLOR = "#1a1a1a"
ACCENT_COLOR = "#00d4ff"
TEXT_COLOR = "#ffffff"
MIC_BUTTON_COLOR = "#2a2a2a"
MIC_BUTTON_ACTIVE = "#00d4ff"

# ==========================================
# PATHS
# ==========================================
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BASE_DIR

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICON_PATH = os.path.join(BASE_DIR, "cmdra-ai.png")
if not os.path.exists(ICON_PATH):
    ICON_PATH = os.path.join(BASE_DIR, "icon.png")
AVATARS_DIR = os.path.join(ASSETS_DIR, "avatars")
AVATAR_DIR = AVATARS_DIR
AVATAR_IMAGE = os.path.join(AVATARS_DIR, "base", "default.png")
LOGS_DIR = os.path.join(APP_DIR, "logs")

# ==========================================
# SECURITY
# ==========================================
DANGEROUS_ACTIONS = ["delete_folder", "delete_file"]
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
MAX_TYPING_LENGTH = 200

# ==========================================
# LOGGING
# ==========================================
LOG_FILE = os.path.join(LOGS_DIR, "cmdra.log")
LOG_LEVEL = "INFO"
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_SIZE = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 3

# ==========================================
# MINI PANEL / DOCK MODE
# ==========================================
AUTO_DOCK_ENABLED = True
AUTO_DOCK_TIMEOUT_MS = 5000
DOCK_ICON_SIZE = 64
DOCK_MARGIN = 22

# ==========================================
# PERFORMANCE
# ==========================================
ENABLE_GPU = False
NUM_THREADS = 2
ENABLE_WAKEWORD = False

