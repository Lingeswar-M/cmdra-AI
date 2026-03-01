class PromptBuilder:

    def __init__(self):
        self.system_prompt = """
You are cmdraAI, a  playful, lovable and secure and intelligent desktop assistant.

Rules:
- Keep responses short and clear.
- Do not execute system commands directly.
- Never suggest dangerous file operations.
- Be precise and helpful.
"""

    def build_prompt(self, user_input, memory_context=None):
        prompt = self.system_prompt.strip() + "\n\n"

        if memory_context:
            prompt += f"Conversation Memory:\n{memory_context}\n\n"

        prompt += f"User: {user_input}\nAssistant:"

        return prompt


