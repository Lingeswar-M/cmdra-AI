"""
LLM Service - Offline Mode
Since cmdra AI is fully offline, conversational queries are not supported.
This service returns a static response for chat intents.
"""
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """
    Offline LLM Service - Returns static responses for chat intents.
    No actual LLM is used to maintain offline operation.
    """

    def __init__(self):
        logger.info("LLMService initialized in offline mode")

    def ask(self, user_input, memory_context=None):
        """
        Return static response for chat queries.
        
        Args:
            user_input: User's chat query
            memory_context: Not used in offline mode
            
        Returns:
            Static response message
        """
        logger.info(f"Chat query received (offline mode): {user_input}")
        return "I can only help with actions like file management, system control, browser automation, and media control. I cannot have conversations in offline mode."


