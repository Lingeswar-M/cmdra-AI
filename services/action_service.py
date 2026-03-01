from actions.file_actions import *
from actions.system_actions import *
from actions.browser_actions import *
from actions.media_actions import *
from utils.fuzzy import best_match

from security.permission_manager import PermissionManager


class ActionService:

    def __init__(self):
        self.permission = PermissionManager()

    def execute(self, intent):

        action = intent["action"]
        params = intent["parameters"]

        # 🔒 Permission check
        allowed, error = self.permission.validate_action(intent)
        if not allowed:
            return error

        try:
            # Dynamically call the correct function
            if action in globals():
                return globals()[action](**params)

            callable_actions = [name for name, fn in globals().items() if callable(fn)]
            fuzzy_action, _ = best_match(action, callable_actions, cutoff=0.75)
            if fuzzy_action:
                return globals()[fuzzy_action](**params)

            return f"Unknown action: {action}"

        except Exception as e:
            return f"Execution error: {e}"
