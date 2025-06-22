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
        """Generate human-friendly notes from Whisper transcription output."""
        self.language.process_whisper_output(transcription_result)

        text = transcription_result.get("text", "")
        segments = transcription_result.get("segments", [])

        notes_content = {
            "Summary": self._generate_summary(text),
            "Key Terms": self._extract_key_terms(segments),
            "Definitions": self._extract_definitions(segments),
            "Questions": self._extract_questions(segments),
            "Timestamps": self._generate_timestamps(segments),
        }

        # Format as human-style notes
        return self._format_as_human_notes(notes_content)

    def _format_as_human_notes(self, notes_content: Dict[str, Any]) -> str:
        output = []
        # Summary
        summary = notes_content.get("Summary")
        if summary and not summary.startswith("No "):
            output.append(f"# Summary\n\n{summary}\n")

        # Key Knowledge (terms + definitions)
        knowledge = []
        for term in notes_content.get("Key Terms", []):
            knowledge.append(
                f"\u2022 **{term['term']}** ({term['timestamp']}): {self._clean_text(term['context'])}"
            )
        for definition in notes_content.get("Definitions", []):
            knowledge.append(
                f"\u2022 **{definition['term']}** → {definition['definition']} ({definition['timestamp']})"
            )
        if knowledge:
            output.append("# Key Knowledge\n\n" + "\n".join(knowledge) + "\n")

        # Questions & Answers
        questions = notes_content.get("Questions", [])
        if questions:
            qna = ["# Questions & Answers"]
            for q in questions:
                full_q = self._complete_sentence(q["question"])
                context = self._clean_text(q.get("answer_context", ""))
                qna.append(
                    f"\n**Q:** {full_q}\n**Context:** {context} ({q['timestamp']})"
                )
            output.append("\n".join(qna) + "\n")

        return "\n".join(output)

    def _clean_text(self, text: str) -> str:
        """Clean and format text snippets: single line, end punctuation."""
        txt = text.replace("\n", " ").strip()
        if not txt:
            return ""
        
        if not txt.endswith((".", "!", "?")):
            txt = txt.rstrip(",") + "..."

        return txt

    def _complete_sentence(self, fragment: str) -> str:
        """Ensure question fragments form a complete readable sentence."""
        frag = fragment.strip()
        if frag.endswith((".", "!", "?")):
            return frag
        
        frag = frag.rstrip(",")
        return frag[0].upper() + frag[1:] + "..."

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
            return text[:300] + "..."

    def _get_sumy_tokenizer(self, language: str) -> str:
        """Get appropriate tokenizer language for Sumy."""
        return "english" if language.startswith("en") else "czech"

    def _extract_key_terms(
        self, segments: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Extract important terms with their timestamps."""
        key_terms = []
        seen_terms = set()
        language = self.language.get_language()

        for segment in segments:
            text = segment["text"]
            timestamp = self._format_time(segment["start"])

            if language.startswith("en"):
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
                                "context": text[:150] + "...",
                            }
                        )
            else:
                for word in re.findall(r"\w{4,}", text):
                    if word.lower() not in seen_terms:
                        seen_terms.add(word.lower())
                        key_terms.append(
                            {
                                "term": word,
                                "timestamp": timestamp,
                                "context": text[:100] + "...",
                            }
                        )

        return key_terms[:15]

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

            lower_tokens = text.lower().split()
            if text.endswith("?") or any(q in lower_tokens[:3] for q in question_words):
                answer_context = " ".join(
                    s["text"] for s in segments[i : i + 3] if s != segment
                )[:200]
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
                "text": segment["text"][:150] + "...",
                "timestamp": self._format_time(segment["start"]),
            }
            for segment in segments
            if len(segment["text"].split()) > 8
        ][:20]
