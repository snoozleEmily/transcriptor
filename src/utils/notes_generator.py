import re
from typing import List, Dict, Tuple
from textblob import TextBlob
from collections import defaultdict
from fpdf import FPDF


from src.utils.content_type import ContentType



class NotesGenerator:
    def __init__(self, config: ContentType):
        self.config = config
        self.min_term_length = 3  # Minimum characters for important terms
        self.sentence_weights = {"first": 1.5, "last": 1.3, "middle": 1.0}

    def create_notes(self, text: str) -> str:
        """Language/topic-agnostic note generation"""
        # Language detection (TextBlob built-in)
        blob = TextBlob(text)
        language = blob.detect_language()

        # Extract core components
        sentences = self._weight_sentences(blob.sentences)
        entities = self._extract_entities(blob)
        relationships = self._find_relationships(blob)

        return self._build_note_structure(
            sentences=sentences,
            entities=entities,
            relationships=relationships,
            language=language,
        )

    def _weight_sentences(self, sentences: List) -> List[Tuple]:
        """Rank sentences by position and content"""
        weighted = []
        total = len(sentences)

        for i, sentence in enumerate(sentences):
            position = "first" if i == 0 else "last" if i == total - 1 else "middle"
            weight = self.sentence_weights[position]

            # Boost weight for questions and lists
            text = str(sentence).strip()
            if text.endswith("?"):
                weight *= 1.2

            if re.search(r"\d+\.\s|\- ", text):
                weight *= 1.4

            weighted.append((weight, text))
            
        return sorted(weighted, key=lambda x: -x[0])

    def _extract_entities(self, blob: TextBlob) -> Dict[str, float]:
        """Find important terms using TF-IDF-like scoring"""
        noun_phrases = [np.lower() for np in blob.noun_phrases]
        word_counts = defaultdict(int)

        # Count meaningful words
        for word, tag in blob.tags:
            if len(word) >= self.min_term_length and tag.startswith(("N", "V", "J")):
                word_counts[word.lower()] += 1

        # Combine noun phrases and single words
        entity_scores = defaultdict(float)
        for np in noun_phrases:
            entity_scores[np] += 2.0  # Higher weight for phrases

        for word, count in word_counts.items():
            entity_scores[word] += count * 0.5

        return dict(sorted(entity_scores.items(), key=lambda x: -x[1]))

    def _find_relationships(self, blob: TextBlob) -> List[Tuple]:
        """Universal relationship extraction using POS patterns"""
        relationships = []
        for sentence in blob.sentences:
            tags = sentence.tags
            for i in range(len(tags) - 2):
                # Look for: Noun -> Verb -> Noun patterns
                if (
                    tags[i][1].startswith("N")
                    and tags[i + 1][1].startswith("V")
                    and tags[i + 2][1].startswith("N")
                ):
                    relationships.append(
                        (
                            tags[i][0],  # Subject
                            tags[i + 1][0],  # Verb
                            tags[i + 2][0],  # Object
                        )
                    )
        return relationships

    def _build_note_structure(
        self,
        sentences: List[Tuple],
        entities: Dict[str, float],
        relationships: List[Tuple],
        language: str,
    ) -> str:
        """Generate hierarchical notes based on content analysis"""
        notes = []

        # 1. Key Entities Section
        notes.append("# Key Concepts")
        for entity, score in list(entities.items())[:5]:  # Top 5 entities
            notes.append(f"• {entity.capitalize()}")
            # Find supporting sentences
            support = [s[1] for s in sentences if entity.lower() in s[1].lower()]

            for sent in support[:2]:  # Top 2 supporting sentences
                notes.append(f"  - {self._clean_sentence(sent)}")

        # 2. Important Relationships
        notes.append("\n# Key Relationships")
        unique_rels = defaultdict(list)
        for subj, verb, obj in relationships:
            unique_rels[(subj.lower(), verb.lower())].append(obj.lower())

        for (subj, verb), objs in list(unique_rels.items())[:3]:  # Top 3
            notes.append(f"• {subj.capitalize()} {verb} {', '.join(objs)}")

        # 3. Key Facts
        notes.append("\n# Important Facts")
        for weight, sent in sentences[:3]:  # Top 3 sentences
            notes.append(f"• {self._clean_sentence(sent)}")

        return "\n".join(notes)

    def _clean_sentence(self, sentence: str) -> str:
        """Normalize sentence formatting"""
        cleaned = re.sub(r"\s+", " ", sentence)  # Remove extra spaces
        return cleaned[0].upper() + cleaned[1:]  # Ensure capitalization


class UniversalPDFExporter:
    def export_notes(self, notes: str, filename: str):
        """Language-agnostic PDF formatting"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)

        # UTF-8 support
        pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVu", "", 12)

        for line in notes.split("\n"):
            if line.startswith("# "):
                pdf.set_font(size=14, style="B")
                pdf.cell(0, 10, txt=line[2:], ln=1)
                pdf.set_font(size=12, style="")

            elif line.startswith("• "):
                pdf.cell(10)
                pdf.cell(0, 10, txt=line[2:], ln=1)

            elif line.startswith("  - "):
                pdf.cell(20)
                pdf.cell(0, 10, txt=line[4:], ln=1)

            else:
                pdf.ln(5)

        pdf.output(filename)
