# Deprecated


from typing import Dict
from dataclasses import dataclass

# TODO: Refactor this?

@dataclass
class LanguageRule:
    quotation_pairs: Dict[str, str]
    special_cases: Dict[str, str] 

rule = LanguageRule()

LANGUAGE_RULES = {  # Default language rules (could be moved to config/json)
        'fr': rule(
            quotation_pairs={'« ': ' »'},
            special_cases={}
        ),
        'de': rule(
            quotation_pairs={'„': '“'},
            special_cases={}
        ),
        # Add more languages?
    }
