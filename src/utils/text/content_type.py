from typing import List, Dict, Optional



class ContentType:
    """Configuration for content type characteristics and processing rules."""
    def __init__(
        self,
        *,
        types: Optional[List[str]] = None, # List of content types (e.g., ['database', 'radiology'])
        words: Optional[Dict[str, List[str]]]  = None, # List of specific words/terms (names, acronyms, etc.)
        has_code: bool = False,            # Whether content contains code snippets/commands
        has_odd_names: bool = False,       # Whether content contains unusual names/identifiers
        is_multilingual: bool = False,     # Whether content contains multiple languages
        note_style: str = "general"
    ):
        """
        Initialize content type configuration with processing flags.
        
        Args:
            types: List of content types (e.g., ['database', 'radiology'])
            words: List of specific words/terms (names, acronyms, etc.)
            has_code: Whether content contains code snippets/commands
            has_odd_names: Whether content contains unusual names/identifiers
            is_multilingual: Whether content contains multiple languages
        """
        # Core content characteristics
        self.types = types or []          # List of content types
        self.words = words or []          # List of specific terms
        self.has_code = has_code          # Code content flag
        self.has_odd_names = has_odd_names or bool(words)  # Unusual names flag
        self.is_multilingual = is_multilingual  # Multilingual content flag
        self.note_style = note_style,  # 'technical', 'lecture', 'meeting'
        self.sections = {  # Template control
            "technical": ["Key Terms", "Definitions", "Procedures"],
            "lecture": ["Main Ideas", "Examples", "Questions"]
        }

    # --------------------- Organizational Storage  ---------------------
    def get_active_categories(self) -> List[str]:
        """Return all active processing categories as a flat list."""
        active = []

        if self.types:
            active.extend([f"type:{t}" for t in self.types])

        if self.words:
            active.extend([f"word:{w}" for w in self.words])

        if self.has_code:
            active.append('has_code')

        if self.has_odd_names:
            active.append('has_odd_names')
        
        if self.is_multilingual:
            active.append('is_multilingual')

        return active

    def is_special(self) -> bool:
        """Check if any special processing flags are enabled."""
        return any([
            self.types,
            self.words,
            self.has_code,
            self.has_odd_names,
            self.is_multilingual
        ])
    
    def is_peculiar(self) -> bool:
        """Check if any specific processing flags are enabled."""
        return any([
            self.has_code,
            self.has_odd_names,
            self.is_multilingual
        ])