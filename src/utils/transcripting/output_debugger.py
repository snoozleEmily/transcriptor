from typing import Optional


from src.utils.content_type import ContentType



class OutputDebugger:
    """Handles content-specific debugging and prompt generation"""
    DEBUG_PREFIX = "[DEBUG]"
    PROMPT_DOMAIN_PREFIX = "Domains:"

    def generate_content_prompt(self, content_config: ContentType) -> str:
        """
        Generate context prompt and debug output based on content configuration

        Args:
            content_config: ContentType object with configuration

        Returns:
            Formatted prompt string for the model
        """
        prompt_parts = []

        self._debug_content_features(content_config)

        if content_config.words:
            prompt_parts.append(
                f"{self.PROMPT_DOMAIN_PREFIX} {', '.join(content_config.words)}"
            )

        return " ".join(prompt_parts) if prompt_parts else ""

    def _debug_content_features(self, content_config: ContentType):
        """Log debug information about content features"""
        if content_config.words:
            self._log_debug_message("Custom vocabulary detected", content_config.words)

        if content_config.has_code:
            self._log_debug_message(
                "Code content detected", str(content_config.has_code)
            )

        if content_config.has_odd_names:
            self._log_debug_message(
                "Unusual names detected", str(content_config.has_odd_names)
            )

    def _log_debug_message(self, title: str, details: Optional[str] = None):
        """
        Standardized debug message formatting

        Args:
            title: Main debug message
            details: Additional details to display
        """
        print(f"\n{self.DEBUG_PREFIX} {title}")
        if details:
            print(f"{' ' * (len(self.DEBUG_PREFIX) + 1)}{details}")
