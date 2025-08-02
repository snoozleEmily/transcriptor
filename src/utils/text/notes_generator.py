import re
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from src.utils.text.word_snippets import QUESTION_WRD, DEFINITION_PAT
from src.errors.exceptions import TranscriptionError
from src.errors.logging import log_unexpected_error



class NotesGenerator:
    def __init__(self, language, config):
        """
        Args:
            language: Language processor instance
            config: ContentType configuration
        """
        self.language = language
        self.config = config

    def create_notes(self, data: Dict[str, Any]) -> str:
        """Generates structured notes from transcription data.
        
        Args:
            data: Dict with 'text' and 'segments' keys from Whisper
            
        Returns:
            Markdown-formatted notes string
            
        Raises:
            TranscriptionError: If input data is invalid
        """
        # Input validation
        if not data.get('text'):
            raise TranscriptionError.no_result()
            
        text = data['text']
        segments = data.get('segments', [])
        
        # Core note sections
        sections = {
            'Summary': self._generate_summary(text),
            'Key Terms': self._extract_key_terms(segments),
            'Questions': self._find_questions(segments),
            'Timestamps': self._get_important_timestamps(segments)
        }
        
        return self._format_as_markdown(sections)

    def _generate_summary(self, text: str) -> str:
        """Generate a 1-2 sentence summary"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return ' '.join(sentences[:2]) if sentences else text[:200] + "..."

    def _extract_key_terms(self, segments: List[Dict]) -> List[str]:
        """Extract important terms from segments"""
        terms = set()
        for seg in segments:
            # Simple heuristic: Capitalized words of 4+ chars
            words = re.findall(r'\b[A-Z][a-z]{3,}\b', seg['text'])
            terms.update(w for w in words if w.lower() not in QUESTION_WRD.get('english', []))
        
        return sorted(terms)[:10]  # Return top 10 terms

    def _find_questions(self, segments: List[Dict]) -> List[Dict]:
        """Identify questions with timestamps"""
        questions = []
        question_words = set(QUESTION_WRD.get(self.language.get_language_code(), []))
        
        for seg in segments:
            text = seg['text'].strip()
            if text.endswith('?') or any(
                text.lower().startswith(word) 
                for word in question_words
            ):
                questions.append({
                    'question': text,
                    'timestamp': self._format_timestamp(seg['start'])
                })
                
        return questions[:5]  # Limit to 5 most important questions

    def _get_important_timestamps(self, segments: List[Dict]) -> List[Dict]:
        """Identify key moments with timestamps"""
        return [
            {
                'text': seg['text'][:100] + ('...' if len(seg['text']) > 100 else ''),
                'timestamp': self._format_timestamp(seg['start'])
            }
            for seg in segments 
            if len(seg['text'].split()) > 10  # Only segments with 10+ words
        ][:5]  # Top 5 timestamps

    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS"""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02}"

    def _format_as_markdown(self, sections: Dict[str, Any]) -> str:
        """Convert sections to markdown text"""
        output = []
        for section, content in sections.items():
            output.append(f"## {section}\n")
            
            if isinstance(content, list):
                if not content:
                    output.append("None found\n")
                    continue
                    
                if isinstance(content[0], dict):  # For questions/timestamps
                    for item in content:
                        output.append(f"- **{item['timestamp']}**: {item['text']}\n")

                else:  # Simple list of terms
                    output.extend(f"- {item}\n" for item in content)

            else:  # String content (summary)
                output.append(f"{content}\n")
                
            output.append("\n")  # Section spacing
            
        return "".join(output)