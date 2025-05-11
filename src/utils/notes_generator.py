import re
from typing import List, Dict, Tuple
from collections import defaultdict
from fpdf import FPDF


from src.utils.content_type import ContentType



class NotesGenerator:
    def __init__(self, config: ContentType):
        self.config = config
        self.min_term_length = 3  # Universal minimum term length
        self.sentence_weights = {"first": 1.5, "last": 1.3, "middle": 1.0}

    def create_notes(self, text: str, language: str = None) -> str:
        """Universal note generation using structural patterns
        Returns:
            str: Formatted notes as a single string
        """
        sentences = self._universal_sentence_split(text)
        weighted_sentences = self._weight_sentences(sentences)
        entities = self._structural_entity_extraction(text)
        relationships = self._positional_relationship_detection(text)
        
        return self._build_note_structure(
            sentences=weighted_sentences,
            entities=entities,
            relationships=relationships,
            language=language
        )

    def _universal_sentence_split(self, text: str) -> List[str]:
        """Language-agnostic sentence splitting"""
        # Split on common sentence terminators followed by whitespace/Uppercase
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-öø-ȳ]|\")', text)
        return [s.strip() for s in sentences if s.strip()]

    def _weight_sentences(self, sentences: List[str]) -> List[Tuple[float, str]]:
        """Rank sentences using universal features"""
        weighted = []
        total = len(sentences)
        
        for i, sentence in enumerate(sentences):
            weight = self.sentence_weights["first" if i == 0 else "last" if i == total-1 else "middle"]
            
            # Universal importance signals
            if '?' in sentence:
                weight *= 1.2  # Questions are generally important
            if any(c.isdigit() for c in sentence):
                weight *= 1.3  # Numbers often indicate important data
            if len(sentence) < 100:  # Short sentences may be impactful
                weight *= 1.1
                
            weighted.append((weight, sentence))
            
        return sorted(weighted, key=lambda x: -x[0])

    def _structural_entity_extraction(self, text: str) -> Dict[str, float]:
        """Entity detection using frequency and structural patterns"""
        # Match words with at least one alphabetic character
        words = re.findall(r'(?<!\S)[^\W\d_]{3,}(?!\S)', text.lower())
        word_counts = defaultdict(int)
        
        # Basic term frequency counting
        for word in words:
            word_counts[word] += 1
            
        # Phrase detection using repeated word sequences
        phrases = re.findall(r'(?<!\S)(?:[^\W\d_]+\s){1,2}[^\W\d_]+(?!\S)', text.lower())
        for phrase in phrases:
            word_counts[phrase] += 2
            
        return dict(sorted(word_counts.items(), key=lambda x: -x[1]))

    def _positional_relationship_detection(self, text: str) -> List[Tuple[str, str, str]]:
        """Universal relationship detection using positional patterns"""
        relationships = []
        sentences = self._universal_sentence_split(text)
        
        for sentence in sentences:
            words = [w for w in re.findall(r'[^\W\d_]+', sentence) if w]  # Words only
            if len(words) < 3:
                continue
                
            # Find potential relationships using positional analysis
            middle = len(words) // 2
            low = max(1, middle - 1)  # Look around the middle
            high = min(len(words) - 1, middle + 2)
            
            for i in range(low, high):
                # Universal pattern: [Context] [Center Word] [Context]
                relationships.append((
                    ' '.join(words[max(0, i-1):i]),  # Left context (subject)
                    words[i],                        # Center word (verb/action)
                    ' '.join(words[i+1:min(len(words), i+2)])  # Right context (object)
                ))
                    
        return relationships

    def _build_note_structure(
        self,
        sentences: List[Tuple[float, str]],
        entities: Dict[str, float],
        relationships: List[Tuple[str, str, str]],
        language: str,
    ) -> str:
        """Universal note structure using ranked content"""
        notes = [
            "# Key Concepts",
            *self._format_entities(entities, sentences),
            "\n# Key Relationships",
            *self._format_relationships(relationships),
            "\n# Important Facts",
            *self._format_facts(sentences)
        ]
        return "\n".join(notes)

    def _format_entities(
        self, 
        entities: Dict[str, float], 
        sentences: List[Tuple[float, str]]
    ) -> List[str]:
        """Format entities for output"""
        formatted = []
        for entity, _ in list(entities.items())[:5]:  # Top 5 entities
            formatted.append(f"• {entity.title()}")
            # Find first two sentences containing the entity
            matches = [s[1] for s in sentences if entity.lower() in s[1].lower()][:2]
            formatted.extend(f"  - {self._clean_sentence(s)}" for s in matches)
            
        return formatted

    def _format_relationships(
        self, 
        relationships: List[Tuple[str, str, str]]
    ) -> List[str]:
        """Format relationships for output"""
        rel_counts = defaultdict(list)
        for subj, verb, obj in relationships:
            rel_counts[(subj.lower(), verb.lower())].append(obj.lower())
        
        return [
            f"• {subj.title()} {verb} {', '.join(objs)}" 
            for (subj, verb), objs in sorted(
                rel_counts.items(),
                key=lambda x: -len(x[1])  # Sort by frequency
            )[:3]  # Top 3 relationships
        ]

    def _format_facts(self, sentences: List[Tuple[float, str]]) -> List[str]:
        """Format important facts for output"""
        return [f"• {self._clean_sentence(s[1])}" for s in sentences[:3]]

    def _clean_sentence(self, sentence: str) -> str:
        """Universal sentence cleaning"""
        cleaned = re.sub(r'\s+', ' ', sentence).strip()
        if len(cleaned) > 0:
            # Capitalize first alphabetic character
            for i, c in enumerate(cleaned):
                if c.isalpha():
                    cleaned = cleaned[:i] + c.upper() + cleaned[i+1:]
                    break
        return cleaned