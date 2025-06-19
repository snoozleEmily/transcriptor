QUESTION_WRD = {
    "english": [
        # Pronomes/advérbios interrogativos
        "what", "why", "how", "when", "where", "who", "which",

        # Auxiliares comuns em perguntas
        "do", "does", "did", "is", "are", "was", "were", 
        "can", "could", "will", "would", "should", "shall", "may", "might"
    ],
    "portuguese": [
        # Pronomes/advérbios interrogativos
        "o que", "que", "por que", "como", "quando", "onde", "quem", "qual", "quais",

        # Auxiliares/complementos comuns em perguntas
        "é", "são", "está", "estão", "pode", "poderia", "deve", "será", "há", "têm"
    ],
    "spanish": [
        # Pronomes/advérbios interrogativos
        "qué", "por qué", "cómo", "cuándo", "dónde", "quién", "cuál", "cuáles",

        # Auxiliares/complementos comuns em perguntas
        "es", "son", "está", "están", "puede", "podría", "debe", "será", "hay", "tienen"
    ],
    "italian": [
        # Pronomes/advérbios interrogativos
        "che", "che cosa", "perché", "come", "quando", "dove", "chi", "quale", "quali",

        # Auxiliares/complementos comuns em perguntas
        "è", "sono", "sta", "stanno", "può", "potrebbe", "deve", "sarà", "c'è", "hanno"
    ],
    "default": [ # WIP
        # Pronomes/advérbios interrogativos
        "",

        # Auxiliares/complementos comuns em perguntas
        ""
    ],
}

DEFINITION_PAT = {
    "english": [
        r"(\b[A-Z][a-z]+\b) (?:is|are|means|refers to) (.+?)(?=[\.\n])",
        r"(.+?) (?:is defined as|is called) (.+)"
    ],
    "portuguese": [
        r"(\b[A-ZÀ-Ÿ][a-zà-ÿ]+\b) (?:é|são|significa|se refere a) (.+?)(?=[\.\n])",
        r"(.+?) (?:é definido como|é chamado de|chama) (.+)"
    ],
    "spanish": [
        r"(\b[A-ZÁ-Ÿ][a-zá-ÿ]+\b) (?:es|son|significa|se refiere a) (.+?)(?=[\.\n])",
        r"(.+?) (?:se define como|se llama) (.+)"
    ],
    "italian": [
        r"(\b[A-ZÀ-Ÿ][a-zà-ÿ]+\b) (?:è|sono|significa|si riferisce a) (.+?)(?=[\.\n])",
        r"(.+?) (?:è definito come|si chiama) (.+)"
    ],
    # Opcional: padrão genérico ou default
    "default": []
}
