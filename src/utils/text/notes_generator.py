import re
import nltk
from typing import List, Dict, Any
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer


from .language import Language
from .content_type import ContentType
from src.utils.text.word_snippets import QUESTION_WRD, DEFINITION_PAT


class NotesGenerator:
    def __init__(self, language: Language, config: ContentType):
        self.config = config
        self.language = language
        self._validate_nltk_resources()

    def create_notes(self, transcription_result: Dict[str, Any]) -> str:
        """Generate structured notes from Whisper transcription output and return formatted string"""
        self.language.process_whisper_output(transcription_result)

        text = transcription_result.get("text", "")
        segments = transcription_result.get("segments", [])

        notes_content = {  # Generate all note sections
            "Summary": self._generate_summary(text),
            "Key Terms": self._extract_key_terms(segments),
            "Definitions": self._extract_definitions(segments),
            "Questions": self._extract_questions(segments),
            "Timestamps": self._generate_timestamps(segments),
        }

        # Format the content as markdown-style text
        formatted_notes = ""
        for section, content in notes_content.items():
            # Skip empty sections if configured
            if (isinstance(content, list) and not content) or (
                isinstance(content, str) and content.startswith("No ")):
                continue

            formatted_notes += f"# {section}\n\n"  # Section heading

            if isinstance(content, list):
                if not content:  # Empty list
                    formatted_notes += "No items found\n\n"
                    continue

                if isinstance(content[0], dict):
                    # Format list of dictionaries
                    for item in content:
                        formatted_notes += (
                            "• "
                            + "\n  ".join(f"{k}: {v}" for k, v in item.items())
                            + "\n"
                        )
                else:
                    for item in content:  # Format simple list
                        formatted_notes += f"• {item}\n"

                formatted_notes += "\n"

            elif isinstance(content, str):
                formatted_notes += f"{content}\n\n"

            else:
                formatted_notes += f"{str(content)}\n\n"

        return formatted_notes

    def _validate_nltk_resources(self) -> None:
        """Ensure required NLTK resources are available."""
        try:
            nltk.data.find("tokenizers/punkt")
            nltk.data.find("taggers/averaged_perceptron_tagger")

        except LookupError:
            nltk.download("punkt")
            nltk.download("averaged_perceptron_tagger")

    def _generate_summary(self, text: str) -> str:
        """Generate a concise summary of the text."""
        if not text.strip():
            return "No summary available."

        try:
            language = self.language.get_language()
            parser = PlaintextParser.from_string(
                text, self._get_sumy_tokenizer(language)
            )
            summarizer = TextRankSummarizer()
            summary_sentences = summarizer(parser.document, sentences_count=3)
            return " ".join(str(s) for s in summary_sentences)

        except Exception:
            return text[:300] + "..."  # Fallback to first 300 chars

    def _get_sumy_tokenizer(self, language: str) -> str:
        """Get appropriate tokenizer language for Sumy."""
        return (
            "english" if language.startswith("en") else "czech"
        )  # Sumy's default fallback

    def _extract_key_terms(
        self, segments: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Extract important terms with their timestamps."""
        key_terms = []
        seen_terms = set()
        language = self.language.get_language()

        # it should consider words: Optional[Dict[str, List[str]]] from ContentType

        for segment in segments:
            text = segment["text"]
            timestamp = self._format_time(segment["start"])

            if language.startswith("en"):
                # English-specific POS tagging
                tokens = nltk.word_tokenize(text)
                for word, pos in nltk.pos_tag(tokens):
                    if (
                        pos.startswith("NN")
                        and len(word) > 3
                        and word.lower() not in seen_terms
                    ):
                        seen_terms.add(word.lower())
                        key_terms.append(
                            {
                                "term": word,
                                "timestamp": timestamp,
                                "context": text[:150]
                                + "...",  # First 150 chars as context
                            }
                        )
            else:
                # Non-English fallback
                for word in re.findall(r"\w{4,}", text):  # Words with 4+ chars
                    if word.lower() not in seen_terms:
                        seen_terms.add(word.lower())
                        key_terms.append(
                            {
                                "term": word,
                                "timestamp": timestamp,
                                "context": text[:100] + "...",
                            }
                        )

        return key_terms[:15]  # Return top 15 terms

    def _extract_definitions(
        self, segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract definitions from text using language-specific patterns."""
        definitions = []
        patterns = self.language.get_definition_patterns(DEFINITION_PAT)

        if not patterns:
            return []

        for segment in segments:
            text = segment["text"]
            timestamp = self._format_time(segment["start"])
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    definitions.append(
                        {
                            "term": match.group(1),
                            "definition": match.group(2),
                            "timestamp": timestamp,
                        }
                    )

        return definitions

    def _extract_questions(
        self, segments: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Extract questions with their answer contexts."""
        questions = []
        question_words = self.language.get_question_words(QUESTION_WRD)

        for i, segment in enumerate(segments):
            text = segment["text"].strip()
            timestamp = self._format_time(segment["start"])

            # Check for question marks or question words in the first three tokens
            lower_tokens = text.lower().split()
            if text.endswith("?") or any(q in lower_tokens[:3] for q in question_words):

                # Get next 2 segments as potential answers
                answer_context = " ".join(
                    s["text"] for s in segments[i : i + 3] if s != segment
                )[
                    :200
                ]  # Limit to 200 chars

                questions.append(
                    {
                        "question": text,
                        "timestamp": timestamp,
                        "answer_context": (
                            answer_context + "..." if answer_context else ""
                        ),
                    }
                )

        return questions

    def _format_time(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format."""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02}"

    def _generate_timestamps(
        self, segments: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate important timestamps for key content."""
        return [
            {
                "text": segment["text"][:150] + "...",  # Truncate long text
                "timestamp": self._format_time(segment["start"]),
            }
            for segment in segments
            if len(segment["text"].split()) > 8  # Only segments with 8+ words
        ][
            :20
        ]  # Limit to 20 key timestamps
