import re
from typing import List, Dict, Tuple
from collections import defaultdict


from src.utils.content_type import ContentType

# TODO: refactor this


class NotesGenerator:
    def __init__(self, config: ContentType):
        """Initialize the notes generator with configuration settings.

        Args:
            config: ContentType configuration object containing settings
                   for note generation
        """
        self.config = config
        self.min_term_length = 3  # Minimum length for terms to be considered meaningful

        # Weights for sentence importance based on position in text
        self.sentence_weights = {"first": 1.5, "last": 1.3, "middle": 1.0}

    def create_notes(self, text: str, language: str | None = None) -> str:
        """Main method to generate structured notes from input text.

        Process:
        1. Split text into sentences
        2. Weight sentences by importance
        3. Extract key entities
        4. Detect relationships between concepts
        5. Format all components into structured notes

        Args:
            text: Input text to process
            language: Optional language specification (currently not fully utilized)

        Returns:
            Formatted notes as a single string with sections
        """
        sentences = self._universal_sentence_split(text)
        weighted_sentences = self._weight_sentences(sentences)
        entities = self._structural_entity_extraction(text)
        relationships = self._positional_relationship_detection(text)

        return self._build_note_structure(
            sentences=weighted_sentences,
            entities=entities,
            relationships=relationships,
            language=language,
        )

    def _universal_sentence_split(self, text: str) -> List[str]:
        """Split text into sentences using language-agnostic patterns.

        Uses common sentence terminators (.!?) followed by whitespace and uppercase
        to identify sentence boundaries. Handles basic multilingual cases.
        """
        # Split on sentence terminators followed by whitespace and uppercase letter
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-öø-ȳ]|\")", text)
        return [s.strip() for s in sentences if s.strip()]

    def _weight_sentences(self, sentences: List[str]) -> List[Tuple[float, str]]:
        """Assign importance weights to sentences based on structural features.

        Weights are determined by:
        - Position in text (first/last sentences get higher weight)
        - Presence of questions
        - Presence of numbers
        - Sentence length
        """
        weighted = []
        total = len(sentences)

        for i, sentence in enumerate(sentences):
            # Base weight from position
            weight = self.sentence_weights[
                "first" if i == 0 else "last" if i == total - 1 else "middle"
            ]

            # Apply multipliers for important features
            if "?" in sentence:
                weight *= 1.2  # Questions often contain key information

            if any(c.isdigit() for c in sentence):
                weight *= 1.3  # Numbers typically indicate important data

            if len(sentence) < 100:  # Very long sentences may be less important
                weight *= 1.1

            weighted.append((weight, sentence))

        return sorted(weighted, key=lambda x: -x[0])  # Sort by weight descending

    def _structural_entity_extraction(self, text: str) -> Dict[str, float]:
        """Extract key terms and phrases from text using frequency analysis.

        Entities are identified by:
        - Individual words (minimum 3 letters)
        - Repeated word sequences (phrases)
        - Frequency counts determine importance
        """
        # Find words with at least 3 alphabetic characters
        words = re.findall(r"(?<!\S)[^\W\d_]{3,}(?!\S)", text.lower())
        word_counts = defaultdict(int)

        # Count individual word occurrences
        for word in words:
            word_counts[word] += 1

        # Detect common phrases (1-3 word sequences)
        phrases = re.findall(
            r"(?<!\S)(?:[^\W\d_]+\s){1,2}[^\W\d_]+(?!\S)", text.lower()
        )
        for phrase in phrases:
            word_counts[phrase] += 2  # Phrases get extra weight

        return dict(sorted(word_counts.items(), key=lambda x: -x[1]))

    def _positional_relationship_detection(
        self, text: str
    ) -> List[Tuple[str, str, str]]:
        """Detect conceptual relationships using sentence structure patterns.

        Identifies potential subject-verb-object patterns by analyzing:
        - Word positions in sentences
        - Common triple patterns around sentence centers
        """
        relationships = []
        sentences = self._universal_sentence_split(text)

        for sentence in sentences:
            words = [w for w in re.findall(r"[^\W\d_]+", sentence) if w]  # Words only
            if len(words) < 3:
                continue  # Need at least 3 words for a relationship

            # Analyze words around the middle of the sentence
            middle = len(words) // 2
            low = max(1, middle - 1)  # Look around the middle
            high = min(len(words) - 1, middle + 2)

            for i in range(low, high):
                # Extract potential subject-verb-object patterns
                relationships.append(
                    (
                        " ".join(words[max(0, i - 1) : i]),  # Left context (subject)
                        words[i],  # Center word (verb/action)
                        " ".join(
                            words[i + 1 : min(len(words), i + 2)]
                        ),  # Right context (object)
                    )
                )

        return relationships

    def _build_note_structure(
        self,
        sentences: List[Tuple[float, str]],
        entities: Dict[str, float],
        relationships: List[Tuple[str, str, str]],
        language: str,
    ) -> str:
        """Organize all extracted information into structured note format.

        Creates sections for:
        - Key concepts (entities)
        - Key relationships
        - Important facts (weighted sentences)
        """
        notes = [
            "# Key Concepts",
            *self._format_entities(entities, sentences),
            "\n# Key Relationships",
            *self._format_relationships(relationships),
            "\n# Important Facts",
            *self._format_facts(sentences),
        ]
        return "\n".join(notes)

    def _format_entities(
        self, entities: Dict[str, float], sentences: List[Tuple[float, str]]
    ) -> List[str]:
        """Format extracted entities with example sentences.

        For each top entity:
        - Shows the entity (title case)
        - Includes up to 2 example sentences containing the entity
        """
        formatted = []
        for entity, _ in list(entities.items())[:5]:  # Top 5 entities
            formatted.append(f"• {entity.title()}")
            # Find example sentences containing the entity
            matches = [s[1] for s in sentences if entity.lower() in s[1].lower()][:2]
            formatted.extend(f"  - {self._clean_sentence(s)}" for s in matches)

        return formatted

    def _format_relationships(
        self, relationships: List[Tuple[str, str, str]]
    ) -> List[str]:
        """Group and format common relationship patterns.

        Aggregates similar relationships and shows:
        - Subject-verb combinations
        - All associated objects
        """
        rel_counts = defaultdict(list)
        for subj, verb, obj in relationships:
            rel_counts[(subj.lower(), verb.lower())].append(obj.lower())

        return [
            f"• {subj.title()} {verb} {', '.join(objs)}"
            for (subj, verb), objs in sorted(
                rel_counts.items(), key=lambda x: -len(x[1])  # Sort by frequency
            )[
                :3
            ]  # Show top 3 most frequent relationships
        ]

    def _format_facts(self, sentences: List[Tuple[float, str]]) -> List[str]:
        """Format the most important sentences as key facts."""
        return [f"• {self._clean_sentence(s[1])}" for s in sentences[:3]]

    def _clean_sentence(self, sentence: str) -> str:
        """Normalize sentence formatting.

        - Collapses multiple spaces
        - Ensures proper capitalization
        - Removes extra whitespace
        """
        cleaned = re.sub(r"\s+", " ", sentence).strip()
        if len(cleaned) > 0:
            # Capitalize first alphabetic character
            for i, c in enumerate(cleaned):
                if c.isalpha():
                    cleaned = cleaned[:i] + c.upper() + cleaned[i + 1 :]
                    break

        return cleaned
