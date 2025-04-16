from typing import Dict, List, Optional

class ContentTypeConfig:
    """Configuration for content type characteristics and processing rules."""
    
    def __init__(
        self,
        *,
        is_technical: bool = False,
        is_multilingual: bool = False,
        has_code: bool = False,
        has_odd_names: bool = False,
        tech_categories: Optional[List[str]] = None,
        custom_processing_rules: Optional[Dict[str, bool]] = None
    ):
        """
        Initialize content type configuration with processing flags.
        
        Args:
            is_technical: Whether content contains technical terminology
            is_multilingual: Whether content contains multiple languages
            has_code: Whether content contains code snippets/commands
            has_odd_names: Whether content contains unusual names/identifiers
            tech_categories: Specific technical domains (e.g., ['backend', 'databases'])
            custom_processing_rules: Additional processing flags (key: flag_name, value: enabled)
        """
        # Core content characteristics
        self.is_technical = is_technical
        self.is_multilingual = is_multilingual
        self.has_code = has_code
        self.has_odd_names = has_odd_names
        
        # Technical domain categorization
        self.tech_categories = tech_categories or []
        
        # Extended processing rules
        self.custom_rules = custom_processing_rules or {}
        
        # Validation
        if not isinstance(self.tech_categories, list):
            # TODO: Create custom exception for this
            raise ValueError("tech_categories must be a list of strings")
            
        if self.has_code and not self.is_technical:
            self.is_technical = True  # Auto-enable technical if code exists

    # TODO: Check possibility to refactor these ifs, looks ichy
    def get_active_categories(self) -> List[str]:
        """Return all active processing categories."""
        active = []
        if self.is_technical:
            active.append('technical')
            active.extend(self.tech_categories)

        if self.is_multilingual:
            active.append('multilingual')

        if self.has_code:
            active.append('code')

        if self.has_odd_names:
            active.append('odd_names')

        active.extend(k for k, v in self.custom_rules.items() if v)
        return active

    def is_special(self) -> bool:
        """Check if any special processing flags are enabled."""
        return any([
            self.is_technical,
            self.is_multilingual,
            self.has_code,
            self.has_odd_names,
            bool(self.custom_rules)
        ])