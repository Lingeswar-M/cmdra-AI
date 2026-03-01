import re
from difflib import get_close_matches

from utils.fuzzy import best_match


class IntentClassifier:
    COMMAND_VOCAB = {
        "create", "make", "folder", "called", "named", "confirm", "delete", "file", "rename", "to", "as",
        "move", "open", "read", "write", "in", "organize", "downloads", "website", "search", "google",
        "youtube", "gmail", "mail", "brave", "chrome", "vscode", "notepad", "cmd", "command", "prompt",
        "settings", "task", "manager", "word", "excel", "powerpoint", "power", "point", "lock", "screen",
        "disk", "usage", "exit", "quit", "close", "stop", "assistant", "shutdown", "brightness", "increase", "decrease",
        "up", "down", "lower", "raise", "brighter", "dim", "play", "pause", "music", "volume", "microsoft",
    }

    def _contains_fuzzy(self, text, keyword, cutoff=0.75):
        words = text.split()
        return bool(get_close_matches(keyword, words, n=1, cutoff=cutoff))

    def _normalize_command_text(self, text):
        words = text.lower().strip().split()
        head = min(6, len(words))
        for i in range(head):
            cutoff = 0.72 if i == 0 else 0.84
            match, score = best_match(words[i], list(self.COMMAND_VOCAB), cutoff=cutoff)
            if match:
                if i == 1 and words[0] == "open" and match in {"file", "folder", "website"} and score < 0.9:
                    continue
                words[i] = match
        return " ".join(words)

    def classify(self, text: str):
        text = self._normalize_command_text(text)

        # -------------------------
        # FILE MANAGEMENT
        # -------------------------
        match = re.search(r"(create|make)\s+(a\s+)?folder\s+(called|named)?\s*(.+)", text)
        if match:
            return {
                "category": "file",
                "action": "create_folder",
                "parameters": {"folder_name": match.group(4).strip()},
            }

        match = re.search(r"(confirm\s+)?delete\s+(the\s+)?file\s+(called\s+)?(.+)", text)
        if match:
            confirm = bool(match.group(1))
            return {
                "category": "file",
                "action": "delete_file",
                "parameters": {"file_name": match.group(4).strip(), "confirm": confirm},
            }

        match = re.search(r"(confirm\s+)?delete\s+(the\s+)?folder\s+(called|named)?\s*(.+)", text)
        if match:
            confirm = bool(match.group(1))
            return {
                "category": "file",
                "action": "delete_folder",
                "parameters": {"folder_name": match.group(4).strip(), "confirm": confirm},
            }

        # rename file dummy as sample
        match = re.search(r"rename\s+(file\s+)?(.+?)\s+(to|as)\s+(.+)", text)
        if match:
            return {
                "category": "file",
                "action": "rename_file",
                "parameters": {
                    "old_name": match.group(2).strip(),
                    "new_name": match.group(4).strip(),
                },
            }

        match = re.search(r"(create|make)\s+(a\s+)?(text|txt|doc|docx|pdf|json|csv|python|py)\s+file\s+(called|named)?\s*(.+?)(\s+in\s+(.+))?$", text)
        if match:
            file_type = match.group(3).strip()
            file_name = match.group(5).strip()
            folder_name = match.group(7).strip() if match.group(7) else "Desktop"
            return {
                "category": "file",
                "action": "create_file",
                "parameters": {
                    "file_name": file_name,
                    "folder_name": folder_name,
                    "content": "",
                    "file_type": file_type,
                },
            }

        match = re.search(r"(create|make)\s+(a\s+)?file\s+(called|named)?\s*(.+?)(\s+in\s+(.+))?$", text)
        if match:
            file_name = match.group(4).strip()
            folder_name = match.group(6).strip() if match.group(6) else "Desktop"
            return {
                "category": "file",
                "action": "create_file",
                "parameters": {"file_name": file_name, "folder_name": folder_name, "content": ""},
            }

        match = re.search(r"move\s+folder\s+(.+?)\s+to\s+(.+)", text)
        if match:
            return {
                "category": "file",
                "action": "move_folder",
                "parameters": {"folder_name": match.group(1).strip(), "destination_folder": match.group(2).strip()},
            }

        match = re.search(r"move\s+(.+)\s+to\s+(.+)", text)
        if match:
            return {
                "category": "file",
                "action": "move_file",
                "parameters": {"file_name": match.group(1).strip(), "destination_folder": match.group(2).strip()},
            }

        if "list files" in text:
            return {"category": "file", "action": "list_files", "parameters": {}}

        match = re.search(r"open\s+file\s+(.+?)(?:\s+(?:in|from)\s+(.+))?$", text)
        if match:
            return {
                "category": "file",
                "action": "open_item",
                "parameters": {
                    "name": match.group(1).strip(),
                    "destination_folder": match.group(2).strip() if match.group(2) else None,
                },
            }

        match = re.search(r"open\s+folder\s+(.+?)(?:\s+(?:in|from)\s+(.+))?$", text)
        if match:
            return {
                "category": "file",
                "action": "open_item",
                "parameters": {
                    "name": match.group(1).strip(),
                    "destination_folder": match.group(2).strip() if match.group(2) else None,
                },
            }

        match = re.search(r"read\s+file\s+(.+)", text)
        if match:
            return {"category": "file", "action": "read_file", "parameters": {"file_name": match.group(1).strip()}}

        match = re.search(r"write\s+(.+)\s+to\s+file\s+(.+)", text)
        if match:
            return {
                "category": "file",
                "action": "write_file",
                "parameters": {"content": match.group(1).strip(), "file_name": match.group(2).strip()},
            }

        if "organize downloads" in text:
            return {"category": "file", "action": "organize_downloads", "parameters": {}}

        # -------------------------
        # QUICK WEBSITE SHORTCUTS
        # -------------------------
        quick_sites = {
            "youtube": "https://youtube.com",
            "colab": "https://colab.research.google.com",
            "chatgpt": "https://chatgpt.com",
            "canva": "https://www.canva.com",
            "github": "https://github.com",
            "whatsapp": "https://web.whatsapp.com",
            "web whatsapp": "https://web.whatsapp.com",
            "drive": "https://drive.google.com",
            "google drive": "https://drive.google.com",
        }
        for key, url in quick_sites.items():
            if key in text and ("open" in text or text == key):
                return {"category": "browser", "action": "open_website", "parameters": {"url": url}}

        # -------------------------
        # SYSTEM CONTROL
        # -------------------------
        if "open brave" in text or ("brave" in text and "open" in text):
            return {"category": "system", "action": "open_brave", "parameters": {}}
        if "open chrome" in text:
            return {"category": "system", "action": "open_chrome", "parameters": {}}
        if "open vscode" in text or "open vs code" in text:
            return {"category": "system", "action": "open_vscode", "parameters": {}}
        if "open notepad" in text:
            return {"category": "system", "action": "open_notepad", "parameters": {}}
        if "open cmd" in text or "open command prompt" in text:
            return {"category": "system", "action": "open_cmd", "parameters": {}}
        if "open settings" in text:
            return {"category": "system", "action": "open_settings", "parameters": {}}
        if "open task manager" in text:
            return {"category": "system", "action": "open_task_manager", "parameters": {}}
        if "open word" in text or "open microsoft word" in text:
            return {"category": "system", "action": "open_word", "parameters": {}}
        if "open excel" in text or "open microsoft excel" in text:
            return {"category": "system", "action": "open_excel", "parameters": {}}
        if "open powerpoint" in text or "open power point" in text or "open microsoft powerpoint" in text:
            return {"category": "system", "action": "open_powerpoint", "parameters": {}}

        if text in {"exit", "quit", "close", "shutdown", "shut down"} or any(
            x in text for x in ["close app", "exit app", "quit app", "stop assistant", "shutdown app", "shut down app"]
        ):
            return {"category": "system", "action": "exit_app", "parameters": {}}

        if "lock screen" in text:
            return {"category": "system", "action": "lock_screen", "parameters": {}}
        if "disk usage" in text:
            return {"category": "system", "action": "show_disk_usage", "parameters": {}}

        # -------------------------
        # BROWSER AUTOMATION
        # -------------------------
        match = re.search(r"open website\s+(.+)", text)
        if match:
            return {"category": "browser", "action": "open_website", "parameters": {"url": match.group(1).strip()}}

        match = re.search(r"search google\s+(.+)", text)
        if match:
            return {"category": "browser", "action": "search_google", "parameters": {"query": match.group(1).strip()}}

        match = re.search(r"search youtube\s+(.+)", text)
        if match:
            return {"category": "browser", "action": "search_youtube", "parameters": {"query": match.group(1).strip()}}

        if "open gmail" in text or "open mail" in text:
            return {"category": "browser", "action": "open_gmail", "parameters": {}}

        # Generic open for local file/folder names
        match = re.search(r"open\s+(.+?)(?:\s+(?:in|from)\s+(.+))?$", text)
        if match:
            return {
                "category": "file",
                "action": "open_item",
                "parameters": {
                    "name": match.group(1).strip(),
                    "destination_folder": match.group(2).strip() if match.group(2) else None,
                },
            }

        # -------------------------
        # MEDIA CONTROL
        # -------------------------
        if "brightness" in text or self._contains_fuzzy(text, "brightness"):
            if any(word in text for word in ["decrease", "down", "lower", "dim"]):
                return {"category": "media", "action": "decrease_brightness", "parameters": {}}
            if any(word in text for word in ["increase", "up", "raise", "brighter"]):
                return {"category": "media", "action": "increase_brightness", "parameters": {}}

        if "play music" in text:
            return {"category": "media", "action": "play_music", "parameters": {}}
        if "pause music" in text:
            return {"category": "media", "action": "pause_music", "parameters": {}}

        if "volume" in text:
            if any(word in text for word in ["increase", "up", "raise"]):
                return {"category": "media", "action": "increase_volume", "parameters": {}}
            if any(word in text for word in ["decrease", "down", "lower"]):
                return {"category": "media", "action": "decrease_volume", "parameters": {}}

        return {"category": "chat", "action": None, "parameters": {}}
