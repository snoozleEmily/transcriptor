import re
import nltk
from typing import List, Dict, Any
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer


from src.utils.content_type import ContentType


# TODO: Move this to a json and add more languages
QUESTION_WORDS_EN = [ 
    # Question words for English question detection
    "what", "why", "how", "when", "where", "who", "which",
    "does", "do", "is", "are", "can", "could", "would", "should"
]

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

    def create_notes(self, transcription_result: Dict[str, Any]) -> str:
        """Generate structured notes from Whisper transcription output.

        Args:
            transcription_result: Dictionary containing Whisper output with:
                - 'text': Full transcribed text
                - 'segments': List of dicts with 'text' and 'start' timestamp
                - 'language': Detected language code

        Returns:
            str: Formatted markdown notes with key sections
        """
        language = transcription_result.get('language', self.config.language)
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
        #     return self._llm_polish_notes(markdown)

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

        parser = PlaintextParser.from_string(text, self._get_sumy_tokenizer(language))
        summarizer = TextRankSummarizer()
        summary_sentences = summarizer(parser.document, sentences_count=3)
        return " ".join(str(s) for s in summary_sentences)
    
    def _get_sumy_tokenizer(self, language: str) -> str:
        """Get appropriate tokenizer language for Sumy."""
        return "english" if language.startswith('en') else language

    def _extract_key_terms(self, segments: List[Dict[str, Any]], language: str) -> List[str]:
        """Extract important terms using frequency and TextRank ranking.

        - For English: Uses NLTK POS tagging to extract nouns.
        - For other languages: Skips POS tagging; uses frequent words from key sentences.
        """
        full_text = " ".join(s['text'] for s in segments)

        parser = PlaintextParser.from_string(full_text, self._get_sumy_tokenizer(language))
        summarizer = TextRankSummarizer()
        key_sentences = [str(s) for s in summarizer(parser.document, 5)]

        terms = set()

        if language.startswith('en'):
            # Use POS tagging for English
            for sent in key_sentences:
                for word, pos in nltk.pos_tag(nltk.word_tokenize(sent)):
                    if pos.startswith('NN') and len(word) > 3:  # Only nouns longer than 3 characters
                        terms.add(word.lower())
        else:
            # Skip POS tagging for other languages, fallback to word frequency
            for sent in key_sentences:
                words = re.findall(r'\w{4,}', sent)  # Words with at least 4 characters
                terms.update(word.lower() for word in words)

        return sorted(terms, key=lambda x: len(x), reverse=True)[:10]  # Top 10 longest terms

    def _extract_definitions(self, segments: List[Dict[str, Any]], language: str) -> List[Dict[str, Any]]:
        """Extract potential definition statements.

        NOTE: Regex patterns are English-specific and skipped for non-English.
        """
        definitions = []

        if language.startswith('en'):
            pattern = re.compile(r"(?:means|refers to|is defined as|is called|is)", re.IGNORECASE)

            for segment in segments:
                if pattern.search(segment['text']):
                    definitions.append({
                        'text': segment['text'],
                        'timestamp': self._format_time(segment['start'])
                    })

        return definitions

    def _extract_questions(self, segments: List[Dict[str, Any]], language: str) -> List[Dict[str, Any]]:
        """Extract questions from the text.

        NOTE: Works reliably only for English since question word patterns are language-specific.
        """
        questions = []

        if language.startswith('en'):
            # Organized question words into a variable
            question_pattern = re.compile(
                r'\b(' + '|'.join(re.escape(q) for q in QUESTION_WORDS_EN) + r')\b',
                re.IGNORECASE
            )

            for segment in segments:
                text = segment['text'].strip()
                if text.endswith('?') or question_pattern.match(text.lower()):
                    questions.append({
                        'text': text,
                        'timestamp': self._format_time(segment['start'])
                    })

        return questions
    
    def _format_time(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format.

        Args:
            seconds: Time in seconds (e.g. 123.5)

        Returns:
            str: Formatted timestamp (e.g. "02:03:30")
        """
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02}"

    def _generate_timestamps(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate important timestamps for key content."""
        return [
            {
                'text': segment['text'],
                'timestamp': self._format_time(segment['start'])
            }
            for segment in segments
            if len(segment['text'].split()) > 10  # Only segments with substantial content
        ]

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
    # def _llm_polish_notes(self, markdown: str) -> str:
    #     """Apply light LLM polishing to improve readability"""
    #     prompt = f"Improve this notes' formatting and clarity without changing content:\n{markdown}"
    #     try:
    #         response = self.llm.create_chat_completion(
    #             messages=[{"role": "user", "content": prompt}],
    #             temperature=0.3,
    #             max_tokens=1024
    #         )
    #         return response['choices'][0]['message']['content']
    #     except Exception as e:
    #         logging.warning(f"LLM polishing failed: {str(e)}")
    #         return markdown  # Fallback to original