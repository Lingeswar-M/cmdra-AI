"""
Avatar manager for resolving avatar image paths by action/state.
"""

from __future__ import annotations

import os
from typing import Optional

import config


class AvatarManager:
    """
    Resolves avatar images with this priority:
    1) category/action image
    2) state image
    3) base/default image
    """

    def __init__(self, avatars_root: Optional[str] = None):
        self.avatars_root = avatars_root or os.path.join(config.ASSETS_DIR, "avatars")
        self.base_default = os.path.join(self.avatars_root, "base", "default.png")
        self.action_aliases = {
            "create_folder": "create",
            "create_file": "create",
            "delete_file": "delete",
            "delete_folder": "delete",
            "rename_file": "rename",
            "open_item": "open",
            "open_website": "open",
            "open_github": "open",
            "open_gmail": "open",
            "search_google": "search",
            "search_youtube": "search",
            "increase_volume": "volume_up",
            "decrease_volume": "volume_down",
            "increase_brightness": "brightness",
            "decrease_brightness": "brightness",
        }

    def get_avatar(self, category: str | None = None, action: str | None = None, state: str | None = None) -> str:
        """
        Return best-matching avatar image path.
        """
        if category and action:
            candidate = os.path.join(self.avatars_root, category, f"{action}.png")
            if os.path.isfile(candidate):
                return candidate
            alias = self.action_aliases.get(action)
            if alias:
                candidate = os.path.join(self.avatars_root, category, f"{alias}.png")
                if os.path.isfile(candidate):
                    return candidate

        if state:
            candidate = os.path.join(self.avatars_root, "states", f"{state}.png")
            if os.path.isfile(candidate):
                return candidate

        return self.base_default
