from typing import Optional


from src.utils.text.content_type import ContentType
from src.errors.debug import debug



class SanitizePrompt:
    """
    Converts a ContentType configuration into a prompt string for AI models.

    Summary:
        SanitizePrompt acts as a bridge between the custom vocabulary/settings
        and the AI model. It ensures that the transcription respects the content
        configuration without altering audio or output text.
    """

    PREFIX = "[INFO]"
    PROMPT_DOMAIN_PREFIX = "Domains:"

    def generate_content_prompt(self, content_config: ContentType) -> str:
        """
        Generate a prompt string summarizing content keywords and features.

        Notes:
            - Debug info is logged via debug.dprint.

        Returns:
            A string containing the prompt fragment or an empty string if no keywords exist.
        """
        # Compute display string once to avoid repeated work
        display_words = self._debug_content_features(content_config)

        if display_words:
            return f"{self.PROMPT_DOMAIN_PREFIX} {display_words}"
        
        return ""

    def _debug_content_features(self, content_config: ContentType) -> Optional[str]:
        """
        Log content features and return a comma-separated string of keywords.s

        TODOs / Future improvements:
            - Add prompt fragments for special content types:
                * has_code: "[INSTRUCTION] Preserve code blocks and formatting"
                * has_odd_names: "[INSTRUCTION] Preserve unusual names verbatim"
                * is_multilingual: "[INSTRUCTION] Expect multiple languages; do not auto-translate"
            - Optionally return a structured fragment (list/dict) for fine-grained prompt composition

        Returns:
            A comma-separated string of custom vocabulary terms, or None if empty.
        """
        display = None
        if content_config.words:
            display = ", ".join(str(k) for k in content_config.words.keys())
            debug.dprint(
                f"{self.PREFIX} Custom vocabulary ({len(content_config.words)} terms): {display}"
            )

        if getattr(content_config, "has_code", False):
            debug.dprint(f"{self.PREFIX} Contains code")
            # TODO: Could add prompt fragment: "Preserve code formatting and inline code tokens."

        if getattr(content_config, "has_odd_names", False):
            debug.dprint(f"{self.PREFIX} Contains unusual names")
            # TODO: Could add prompt fragment: "Preserve unusual names verbatim; avoid normalization."

        if getattr(content_config, "is_multilingual", False):
            debug.dprint(f"{self.PREFIX} Multilingual content")
            # TODO: Could add prompt fragment: "Expect language switches; do not auto-translate."

        return display
