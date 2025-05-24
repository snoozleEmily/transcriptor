import re
import nltk
from typing import List, Dict, Any
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer

from src.utils.content_type import ContentType
from src.utils.notes.word_snippets import QUESTION_WORDS, DEFINITION_PATTERNS 

# NOTE: Wrap in conditional check for enhanced mode
# try:
#     from llama_cpp import Llama
# except ImportError:
#     pass  ?

class NotesGenerator:
    def __init__(self, config: ContentType):
        """Initialize the notes generator with configuration settings.

        Args:
            config: ContentType configuration object containing settings
                   for note generation including language and formatting options
        """
        self.config = config
        self._validate_nltk_resources()

    def create_notes(self, transcription_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured notes from Whisper transcription output.

        Args:
            transcription_result: Dictionary containing Whisper output with:
                - 'text': Full transcribed text
                - 'segments': List of dicts with 'text' and 'start' timestamp
                - 'language': Detected language code

        Returns:
            Dict[str, Any]: Structured notes with key sections and timestamps
        """
        language = transcription_result.get('language', 'en')  # Default to English
        segments = transcription_result.get('segments', [])

        # Process content sections
        sections = {
            "Summary": self._generate_summary(transcription_result.get('text', ''), language),
            "Key Terms": self._extract_key_terms(segments, language),
            "Definitions": self._extract_definitions(segments, language),
            "Questions": self._extract_questions(segments, language),
            "Timestamps": self._generate_timestamps(segments)
        }

        # TINYLLAMA INTEGRATION POINT
        # if self.config.note_style == "enhanced":
        #     return self._llm_polish_notes(sections)

        return sections
    
    def _validate_nltk_resources(self) -> None:
        """Ensure required NLTK resources are available."""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')

    def _generate_summary(self, text: str, language: str) -> str:
        """Generate a concise summary of the text."""
        if not text.strip():
            return "No summary available."

        try:
            parser = PlaintextParser.from_string(text, self._get_sumy_tokenizer(language))
            summarizer = TextRankSummarizer()
            summary_sentences = summarizer(parser.document, sentences_count=3)
            return " ".join(str(s) for s in summary_sentences)
        
        except Exception:
            return text[:300] + "..."  # Fallback to first 300 chars

    def _get_sumy_tokenizer(self, language: str) -> str:
        """Get appropriate tokenizer language for Sumy."""
        return "english" if language.startswith('en') else "czech"  # Sumy's default fallback

    def _extract_key_terms(self, segments: List[Dict[str, Any]], language: str) -> List[Dict[str, str]]:
        """Extract important terms with their timestamps."""
        key_terms = []
        seen_terms = set()

        for segment in segments:
            text = segment['text']
            timestamp = self._format_time(segment['start'])
            
            if language.startswith('en'):
                # English-specific POS tagging
                tokens = nltk.word_tokenize(text)
                for word, pos in nltk.pos_tag(tokens):
                    if (pos.startswith('NN') and len(word) > 3 and 
                        word.lower() not in seen_terms):
                        seen_terms.add(word.lower())
                        key_terms.append({
                            'term': word,
                            'timestamp': timestamp,
                            'context': text[:100] + "..."  # First 100 chars as context
                        })
            else:
                # Non-English fallback
                for word in re.findall(r'\w{4,}', text):  # Words with 4+ chars
                    if word.lower() not in seen_terms:
                        seen_terms.add(word.lower())
                        key_terms.append({
                            'term': word,
                            'timestamp': timestamp,
                            'context': text[:100] + "..."
                        })

        return key_terms[:15]  # Return top 15 terms

    def _extract_definitions(self, segments, language):
        definitions = []
        lang_code = language[:2].lower()  # ex: "en", "pt", "es", "it"
        patterns = DEFINITION_PATTERNS.get(lang_code, DEFINITION_PATTERNS["default"])

        if not patterns:
            return []

        for segment in segments:
            text = segment["text"]
            timestamp = self._format_time(segment["start"])
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    definitions.append({
                        "term": match.group(1),
                        "definition": match.group(2),
                        "timestamp": timestamp
                    })

        return definitions

    def _extract_questions(self, segments: List[Dict[str, Any]], language: str) -> List[Dict[str, str]]:
        """Extract questions with their answer contexts."""
        questions = []

        # Determine a 2-letter code from the language (e.g., 'en', 'pt', 'es', 'it')
        lang_code = language[:2].lower()

        # Use match-case instead of if-elif
        match lang_code:
            case "en":
                key = "english"
            case "pt":
                key = "portuguese"
            case "es":
                key = "spanish"
            case "it":
                key = "italian"
            case _:
                key = "default"

        question_words = QUESTION_WORDS.get(key, [])

        for i, segment in enumerate(segments):
            text = segment['text'].strip()
            timestamp = self._format_time(segment['start'])
            
            # Check for question marks or question words in the first three tokens
            lower_tokens = text.lower().split()
            if (text.endswith('?') or 
                any(q in lower_tokens[:3] for q in question_words)):
                
                # Get next 2 segments as potential answers
                answer_context = " ".join(
                    s['text'] for s in segments[i:i+3] if s != segment
                )[:200]  # Limit to 200 chars
                
                questions.append({
                    'question': text,
                    'timestamp': timestamp,
                    'answer_context': answer_context + "..." if answer_context else ""
                })

        return questions
    
    def _format_time(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format."""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02}"

    def _generate_timestamps(self, segments: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate important timestamps for key content."""
        return [
            {
                'text': segment['text'][:150] + "...",  # Truncate long text
                'timestamp': self._format_time(segment['start'])
            }
            for segment in segments
            if len(segment['text'].split()) > 8  # Only segments with 8+ words
        ][:10]  # Limit to 10 key timestamps

    # TINYLLAMA INTEGRATION POINT
    # def _init_llm(self):
    #     """Load 4-bit quantized model (~2GB RAM) on first use"""
    #     model_path = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    #     self.llm = Llama(
    #         model_path=model_path,
    #         n_ctx=2048,  # Adjust based on avg transcript length
    #         n_threads=4  # Limit CPU cores used
    #     )

    # TINYLLAMA INTEGRATION POINT
    # def _llm_polish_notes(self, sections: Dict[str, Any]) -> Dict[str, Any]:
    #     """Apply light LLM polishing to improve readability"""
    #     try:
    #         if not hasattr(self, 'llm'):
    #             self._init_llm()
            
    #         prompt = f"Improve these notes' organization:\n{str(sections)}"
    #         response = self.llm.create_chat_completion(
    #             messages=[{"role": "user", "content": prompt}],
    #             temperature=0.3,
    #             max_tokens=1024
    #         )
    #         return eval(response['choices'][0]['message']['content'])  # Convert back to dict
    #     except Exception:
    #         return sections  # Fallback to original                   
