import os


class PermissionManager:

    def __init__(self):
        # Only allow operations inside Desktop
        self.allowed_base = os.path.join(os.path.expanduser("~"), "Desktop")

        # Limit typing length for safety
        self.max_typing_length = 200


    # 🔒 Check if path is inside allowed directory
    def is_path_allowed(self, path):
        abs_path = os.path.abspath(path)
        return abs_path.startswith(os.path.abspath(self.allowed_base))


    # 🔒 General permission check
    def validate_action(self, intent):
        action = intent["action"]
        params = intent["parameters"]

        # Validate typing length
        if action == "type_text":
            if len(params.get("text", "")) > self.max_typing_length:
                return False, "Typing request too long."

        # Validate folder safety
        if "folder_name" in params:
            full_path = os.path.join(self.allowed_base, params["folder_name"])
            if not self.is_path_allowed(full_path):
                return False, "Access denied."

        return True, None
