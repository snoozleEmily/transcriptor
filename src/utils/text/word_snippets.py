QUESTION_WRD = {
    "english": [
        # Interrogative pronouns
        "what", "why", "how", "when", "where", "who", "which",

        # Auxiliary verbs
        "do", "does", "did", "are", "was", "were",
        "can", "could", "will", "would", "should", "shall", "may", "might"
    ],

    "portuguese": [
        # Pronouns/advérbios interrogativos
        "o que", "que", "por que", "como", "quando", "onde", "quem", "qual", "quais",

        # Auxiliares/complementos comuns
        "são", "está", "estão", "pode", "poderia", "deve", "será", "há", "têm",

        # Colloquial Brazilian forms
        "que que", "cê", "cês", "tá", "tão", "né"
    ],

    "spanish": [
        "qué", "por qué", "cómo", "cuándo", "dónde", "quién", "cuál", "cuáles",
        "son", "está", "están", "puede", "podría", "debe", "será", "hay", "tienen"
    ],

    "italian": [
        "che", "che cosa", "perché", "come", "quando", "dove", "chi", "quale", "quali",
        "sono", "sta", "stanno", "può", "potrebbe", "deve", "sarà", "c'è", "hanno"
    ],

    "french": [
        "qui", "que", "quoi", "qu'est-ce que", "comment", "pourquoi",
        "quand", "où", "quel", "quelle", "quels", "quelles", "lequel", "laquelle"
    ],

    "romanian": [
        "cine", "unde", "ce", "de ce", "cum", "care", "când",
        "câți", "câte"
    ],

    "default": []
}

DEFINITION_PAT = {
    "english": [
        r"(\b[A-Z][a-z]+\b) (?:is defined as|is called) (.+?)(?=[\.\n])",
        r"(.+?) (?:is defined as|is called) (.+)"
    ],

    "portuguese": [
        r"(\b[A-ZÀ-Ÿ][a-zà-ÿ]+\b) (?:é definido como|é chamado de|chama|significado) (.+?)(?=[\.\n])",
        r"(.+?) (?:é definido como|é chamado de|chama|significado) (.+)"
    ],

    "spanish": [
        r"(\b[A-ZÁ-Ÿ][a-zá-ÿ]+\b) (?:es definido como|se llama) (.+?)(?=[\.\n])",
        r"(.+?) (?:se define como|se llama) (.+)"
    ],

    "italian": [
        r"(\b[A-ZÀ-Ÿ][a-zà-ÿ]+\b) (?:è definito come|si chiama) (.+?)(?=[\.\n])",
        r"(.+?) (?:è definito come|si chiama) (.+)"
    ],

    "french": [
        r"(\b[A-Z][a-zéêîôû]+\b) (?:est défini comme|est appelé) (.+?)(?=[\.\n])",
        r"(.+?) (?:est défini comme|est appelé) (.+)"
    ],

    "romanian": [
        r"(\b[A-ZŞŢ][a-zşţ]+\b) (?:este definit ca|este numit) (.+?)(?=[\.\n])",
        r"(.+?) (?:este definit ca|este numit) (.+)"
    ],

    "default": []
}
