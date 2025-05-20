# Deprecated

import re
import numpy as np
from nltk import pos_tag, ne_chunk, word_tokenize, sent_tokenize
from nltk.tree import Tree
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer as SumyTokenizer
from scipy.special import softmax



class AdvancedTextReviser:
    def __init__(self, technical_terms=None, min_confidence=0.4):
        self.technical_terms = set(technical_terms or [])
        self.min_confidence = min_confidence
        self._verify_nltk_resources()

    def _verify_nltk_resources(self):
        """Ensure required NLTK resources are available"""
        required = [
            ("punkt", "tokenizers/punkt"),
            ("averaged_perceptron_tagger", "taggers/averaged_perceptron_tagger"),
            ("maxent_ne_chunker", "chunkers/maxent_ne_chunker"),
            ("words", "corpora/words"),
            ("stopwords", "corpora/stopwords"),
        ]

        missing = []
        import nltk

        for resource, path in required:
            try:
                nltk.data.find(path)
            except LookupError:
                missing.append(resource)

        if missing:
            nltk.download(missing, quiet=True)

    def _init_nltk(self):
        # First-time run: nltk.download(['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words'])
        pass

    def revise(self, text, whisper_result=None):
        """Safe revision pipeline"""
        try:
            text = self._clean_repeats(text)

            if whisper_result:
                text = self._confidence_based_correction(text, whisper_result)

            text = self._validate_semantics(text)
            text = self._enforce_grammar_rules(text)
            return self._restore_proper_nouns(text, whisper_result)

        except Exception as e:
            print(f"Text revision failed: {str(e)}")
            return text  # Return original text on failure

    def _clean_repeats(self, text):
        """Safe word tokenization with fallback"""
        try:
            words = word_tokenize(text)
        except LookupError:
            # Fallback to simple whitespace tokenization
            words = text.split()
            self._verify_nltk_resources()

        cleaned = []
        for i, word in enumerate(words):
            if i > 2 and word == words[i - 2] and word == words[i - 1]:
                continue
            cleaned.append(word)
        return " ".join(cleaned)

    def _confidence_based_correction(self, text, whisper_result):
        """Use Whisper's word-level confidence scores"""
        segments = whisper_result.get("segments", [])
        words = []
        confidences = []

        for seg in segments:
            for word_info in seg.get("words", []):
                words.append(word_info["word"])
                confidences.append(word_info.get("probability", 1.0))

        if len(words) != len(word_tokenize(text)):
            return text  # Alignment failed

        return " ".join(
            [
                w if c >= self.min_confidence else f"[{w}]"
                for w, c in zip(words, confidences)
            ]
        )

    def _validate_semantics(self, text):
        """Check semantic coherence using multiple metrics"""
        if self._is_gibberish(text):
            return self._salvage_content(text)
        return text

    def _is_gibberish(self, text):
        """Combination of linguistic checks"""
        # 1. Named Entity ratio check
        trees = ne_chunk(pos_tag(word_tokenize(text)))
        entity_count = sum(1 for t in trees if isinstance(t, Tree))

        # 2. Verb presence check
        pos_tags = [tag for word, tag in pos_tag(word_tokenize(text))]
        verb_count = sum(1 for tag in pos_tags if tag.startswith("VB"))

        # 3. Technical term match ratio
        tech_matches = sum(
            1 for w in word_tokenize(text) if w.lower() in self.technical_terms
        )

        # 4. LexRank coherence check
        parser = PlaintextParser.from_string(text, SumyTokenizer("english"))
        summarizer = LexRankSummarizer()
        summary = summarizer(parser.document, sentences_count=1)

        return (
            (verb_count == 0 and len(text) > 15)
            or (entity_count / len(word_tokenize(text)) > 0.4)
            or (
                tech_matches / len(self.technical_terms) < 0.2
                if self.technical_terms
                else False
            )
            or (not summary or summary[0].text.count(" ") < 5)
        )

    def _salvage_content(self, text):
        """Extract meaningful fragments using graph ranking"""
        sentences = sent_tokenize(text)
        ranks = self._textrank_scores(sentences)
        best = sentences[np.argmax(ranks)]
        return f"[Possible Meaningful Fragment] {best}" if any(ranks) else text

    def _textrank_scores(self, sentences):
        """Compute sentence importance scores"""
        # Implementation using similarity graph (simplified)
        n = len(sentences)
        scores = np.ones(n)
        # Add real similarity computation here
        return softmax(scores)

    def _enforce_grammar_rules(self, text):
        """Fix common grammatical errors patterns"""
        # Rule 1: Detected repeated articles ("a a book" → "a book")
        text = re.sub(r"\b(a|an|the) \1\b", r"\1", text, flags=re.I)

        # Rule 2: Missing prepositions between nouns
        words = word_tokenize(text)
        pos_tags = pos_tag(words)
        for i in range(2, len(pos_tags)):
            if (
                pos_tags[i - 2][1].startswith("NN")
                and pos_tags[i - 1][1].startswith("NN")
                and pos_tags[i][1].startswith("NN")
            ):
                words.insert(i - 1, "[MISSING_PREP]")
        return " ".join(words)

    def _restore_proper_nouns(self, text, whisper_result):
        """Use Whisper's capitalization hints"""
        if not whisper_result:
            return text
        original_words = [
            w["word"]
            for seg in whisper_result["segments"]
            for w in seg.get("words", [])
        ]
        return " ".join(original_words[: len(word_tokenize(text))])
