DEFINITION_PAT = {
    # ----------------------
    # ENGLISH (en)
    # ----------------------
    "english": [
        # Proper name, multiword, formal verbs
        r"(\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b)\s+(?:is defined as|is called|is known as|is referred to as|means|refers to|can be described as|is described as|is typically called|is commonly called)\s+(.+?)(?=[\.\n,:;])",

        # General phrase -> definition (catch any leading phrase)
        r"(.+?)\s+(?:is defined as|is called|means|refers to|can be described as|is known as|is sometimes called|is often called)\s+(.+?)(?=[\.\n])",

        # Quoted term forms: "term" is ...
        r"['\"](.+?)['\"]\s+(?:is|means|refers to|stands for|=|aka|is called)\s+(.+?)(?=[\.\n,:;])",

        # colon / dictionary style: Term: definition
        r"(\b[A-Za-z0-9&\.\-()' ]{1,120}?)\s*:\s*(.+?)(?=[\.\n])",

        # Parenthetical definitions: Term (means ... / i.e. ...)
        r"(\b[A-Za-z0-9&\.\-()' ]{1,120}?)\s*\(\s*(?:meaning|means|i\.e\.|that is|=)\s*(.+?)\s*\)",

        # equals sign or dash styles
        r"(\b[A-Za-z0-9&\.\-()' ]{1,120}?)\s*(?:=|—|–|-)\s*(?:meaning|means|is|:=)?\s*(.+?)(?=[\.\n])",

        # aka / also known as / also called / or simply
        r"(.+?)\s+(?:aka|a\.k\.a\.|also known as|also called|or simply|or just)\s+(.+?)(?=[\.\n,:;])",

        # short for / stands for / abbreviation
        r"(.+?)\s+(?:is short for|short for|abbr\. for|abbreviation of|stands for)\s+(.+?)(?=[\.\n])",

        # colloquial/informal: people call it / we call it / folks call it
        r"(.+?)\s+(?:is what people call|is what they call|people call it|folks call it|we call it|they call it)\s+(.+?)(?=[\.\n])",

        # "that is" / "in other words" style
        r"(.+?)\s+(?:that is|that's|that means|in other words|i\.e\.)\s+(.+?)(?=[\.\n,:;])",

        # reverse informal: "This is called X" -> capture X as term, previous as definition (common in speech)
        r"(?:This|That|It|The following)\s+(?:is|was)\s+(?:called|known as|referred to as)\s+['\"]?(.+?)['\"]?(?=[\.\n])\s*(?:,?\s*(?:meaning|which means|i\.e\.)\s*(.+?))?",

        # short dictionary entries: TERM — definition
        r"^(\b[A-Z][A-Za-z0-9 \-']{0,80}\b)\s*(?:—|–|-)\s*(.+?)(?=[\.\n])"
    ],

    # ----------------------
    # PORTUGUESE (pt-BR / pt-PT)
    # ----------------------
    "portuguese": [
        # Formal multiword proper names
        r"(\b[A-ZÀ-Ÿ][a-zà-ÿ]+(?: [A-ZÀ-Ÿ][a-zà-ÿ]+)*\b)\s+(?:é definido como|é chamado de|chama-se|significa|refere-se a|pode ser descrito como|é conhecido como)\s+(.+?)(?=[\.\n,:;])",

        # General phrase -> definition
        r"(.+?)\s+(?:é definido como|é chamado de|chama-se|significa|refere-se a|pode ser descrito como)\s+(.+?)(?=[\.\n])",

        # Quoted term
        r"['\"](.+?)['\"]\s+(?:é|significa|quer dizer|=|aka|chamado de)\s+(.+?)(?=[\.\n,:;])",

        # colon style
        r"(\b[A-Za-zÀ-ÿ0-9&\.\-()' ]{1,120}?)\s*:\s*(.+?)(?=[\.\n])",

        # parentheses / i.e.
        r"(\b[A-Za-zÀ-ÿ0-9&\.\-()' ]{1,120}?)\s*\(\s*(?:significa|quer dizer|isto é|i\.e\.|=)\s*(.+?)\s*\)",

        # aka / também chamado / também conhecido
        r"(.+?)\s+(?:também chamado de|também conhecido como|ou simplesmente|ou apenas|aka)\s+(.+?)(?=[\.\n,:;])",

        # abreviado / stands for
        r"(.+?)\s+(?:é abreviação de|abreviado como|abrevia-se|significa|representa|equivale a)\s+(.+?)(?=[\.\n])",

        # informal: a galera chama de / a gente chama de / no popular
        r"(.+?)\s+(?:a galera chama de|as pessoas chamam de|a gente chama de|popularmente conhecido como|no popular)\s+(.+?)(?=[\.\n])",

        # dash / equal / dictionary entry
        r"^(\b[A-ZÀ-Ÿ][A-Za-zÀ-ÿ0-9 '\-]{0,80}\b)\s*(?:—|–|-|=)\s*(.+?)(?=[\.\n])"
    ],

    # ----------------------
    # SPANISH (es)
    # ----------------------
    "spanish": [
        # Proper names, formal verbs
        r"(\b[A-ZÁÉÍÓÚÑÜ][a-záéíóúñü]+(?: [A-ZÁÉÍÓÚÑÜ][a-záéíóúñü]+)*\b)\s+(?:es definido como|se llama|significa|se refiere a|puede definirse como|es conocido como)\s+(.+?)(?=[\.\n,:;])",

        # General phrase -> definition
        r"(.+?)\s+(?:es definido como|se define como|se llama|significa|se refiere a|puede definirse como)\s+(.+?)(?=[\.\n])",

        # Quoted term
        r"['\"](.+?)['\"]\s+(?:es|significa|quiere decir|=|aka|se conoce como)\s+(.+?)(?=[\.\n,:;])",

        # colon style
        r"(\b[A-Za-zÁÉÍÓÚÑÜ0-9&\.\-()' ]{1,120}?)\s*:\s*(.+?)(?=[\.\n])",

        # parentheses
        r"(\b[A-Za-zÁÉÍÓÚÑÜ0-9&\.\-()' ]{1,120}?)\s*\(\s*(?:significa|quiere decir|es decir|i\.e\.|=)\s*(.+?)\s*\)",

        # informal aka / también llamado / también conocido como
        r"(.+?)\s+(?:también llamado|también conocido como|o simplemente|o sea|aka|coloquialmente)\s+(.+?)(?=[\.\n,:;])",

        # abreviado / abreviación / stands for
        r"(.+?)\s+(?:es la abreviatura de|abreviado como|abreviatura de|significa|representa)\s+(.+?)(?=[\.\n])",

        # folks / people call it
        r"(.+?)\s+(?:la gente lo llama|la gente lo conoce como|se le llama|popularmente conocido como|en la jerga)\s+(.+?)(?=[\.\n])",

        # dash / equals
        r"^(\b[A-ZÁÉÍÓÚÑÜ][A-Za-zÁÉÍÓÚÑÜ0-9 \-']{0,80}\b)\s*(?:—|–|-|=)\s*(.+?)(?=[\.\n])"
    ],

    # ----------------------
    # ITALIAN (it)
    # ----------------------
    "italian": [
        # Proper names, formal verbs
        r"(\b[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]+(?: [A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]+)*\b)\s+(?:è definito come|si chiama|significa|si riferisce a|può essere definito come|è conosciuto come)\s+(.+?)(?=[\.\n,:;])",

        # General phrase -> definition
        r"(.+?)\s+(?:è definito come|si chiama|significa|vuol dire|cioè|si riferisce a|può essere definito come)\s+(.+?)(?=[\.\n])",

        # Quoted term
        r"['\"](.+?)['\"]\s+(?:è|significa|vuol dire|=|aka|si conosce come)\s+(.+?)(?=[\.\n,:;])",

        # colon style
        r"(\b[A-Za-zÀ-ÖØ-Ý0-9&\.\-()' ]{1,120}?)\s*:\s*(.+?)(?=[\.\n])",

        # parentheses
        r"(\b[A-Za-zÀ-ÖØ-Ý0-9&\.\-()' ]{1,120}?)\s*\(\s*(?:significa|vuol dire|cioè|i\.e\.|=)\s*(.+?)\s*\)",

        # informal: anche chiamato / anche noto / aka
        r"(.+?)\s+(?:anche chiamato|anche noto come|o semplicemente|o detto anche|aka|colloquialmente)\s+(.+?)(?=[\.\n,:;])",

        # abbreviazione / short for
        r"(.+?)\s+(?:è l'abbreviazione di|abbreviazione di|abbr\. di|sta per|significa)\s+(.+?)(?=[\.\n])",

        # folks call it / popolarmente
        r"(.+?)\s+(?:la gente lo chiama|si chiama|popolarmente noto come|nella gergo|informalmente conosciuto come)\s+(.+?)(?=[\.\n])",

        # dash / equals / dictionary entry
        r"^(\b[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-Ý0-9 \-']{0,80}\b)\s*(?:—|–|-|=)\s*(.+?)(?=[\.\n])"
    ],

    # ----------------------
    # FRENCH (fr)
    # ----------------------
    "french": [
        # Proper names, formal verbs
        r"(\b[A-ZÉÈÊË][a-zéèêëàâîïôûùüÿçœæ]+(?: [A-ZÉÈÊË][a-zéèêëàâîïôûùüÿçœæ]+)*\b)\s+(?:est défini comme|est appelé|signifie|désigne|peut être défini comme|est connu comme)\s+(.+?)(?=[\.\n,:;])",

        # General phrase -> definition
        r"(.+?)\s+(?:est défini comme|est appelé|signifie|veut dire|c'est-à-dire|désigne|peut être défini comme)\s+(.+?)(?=[\.\n])",

        # Quoted term
        r"['\"](.+?)['\"]\s+(?:est|signifie|veut dire|=|aka|est appelé)\s+(.+?)(?=[\.\n,:;])",

        # colon style
        r"(\b[A-Za-zÉÈÊË0-9&\.\-()' ]{1,120}?)\s*:\s*(.+?)(?=[\.\n])",

        # parentheses
        r"(\b[A-Za-zÉÈÊË0-9&\.\-()' ]{1,120}?)\s*\(\s*(?:signifie|veut dire|c'est-à-dire|i\.e\.|=)\s*(.+?)\s*\)",

        # informal / aussi appelé / aussi connu sous le nom de
        r"(.+?)\s+(?:aussi appelé|aussi connu sous le nom de|ou simplement|ou juste|aka|dans le langage courant|familierement)\s+(.+?)(?=[\.\n,:;])",

        # abréviation / stands for
        r"(.+?)\s+(?:est l'abréviation de|abréviation de|abrév\. de|signifie|représente)\s+(.+?)(?=[\.\n])",

        # people call it / la foule l'appelle / populaire
        r"(.+?)\s+(?:les gens l'appellent|on l'appelle|populairement connu comme|dans la langue familière|familier)\s+(.+?)(?=[\.\n])",

        # dash / equals
        r"^(\b[A-ZÉÈÊË][A-Za-zÉÈÊË0-9 \-']{0,80}\b)\s*(?:—|–|-|=)\s*(.+?)(?=[\.\n])"
    ],

    # ----------------------
    # ROMANIAN (ro)
    # ----------------------
    "romanian": [
        # Proper name, formal verbs
        r"(\b[A-ZĂÂÎȘȚ][a-zăâîșț]+(?: [A-ZĂÂÎȘȚ][a-zăâîșț]+)*\b)\s+(?:este definit ca|este numit|înseamnă|se referă la|poate fi definit ca|este cunoscut ca)\s+(.+?)(?=[\.\n,:;])",

        # General phrase -> definition
        r"(.+?)\s+(?:este definit ca|este numit|înseamnă|însemnă|se referă la|poate fi definit ca)\s+(.+?)(?=[\.\n])",

        # Quoted term
        r"['\"](.+?)['\"]\s+(?:este|înseamnă|vrea să spună|=|aka|se numește)\s+(.+?)(?=[\.\n,:;])",

        # colon style
        r"(\b[A-Za-zĂÂÎȘȚ0-9&\.\-()' ]{1,120}?)\s*:\s*(.+?)(?=[\.\n])",

        # parentheses / i.e.
        r"(\b[A-Za-zĂÂÎȘȚ0-9&\.\-()' ]{1,120}?)\s*\(\s*(?:înseamnă|vrea să spună|adică|i\.e\.|=)\s*(.+?)\s*\)",

        # informal: și se numește / sau pur și simplu / aka
        r"(.+?)\s+(?:și se numește|sau pur și simplu|aka|cunoscut și ca|popular cunoscut ca)\s+(.+?)(?=[\.\n,:;])",

        # abreviere / short for
        r"(.+?)\s+(?:este abrevierea pentru|abreviere de|abreviere pentru|prescurtarea de|înseamnă)\s+(.+?)(?=[\.\n])",

        # folks call it / popular
        r"(.+?)\s+(?:oamenii îi spun|oamenii îl numesc|popular cunoscut ca|în jargon)\s+(.+?)(?=[\.\n])",

        # dash / equals
        r"^(\b[A-ZĂÂÎȘȚ][A-Za-zĂÂÎȘȚ0-9 \-']{0,80}\b)\s*(?:—|–|-|=)\s*(.+?)(?=[\.\n])"
    ],

    # ----------------------
    # fallback / default
    # ----------------------
    "default": [
        # Very generic patterns to catch "X is Y" or "X: Y"
        r"(.+?)\s+(?:is|means|=|:=|:)\s+(.+?)(?=[\.\n])",
        r"['\"]?(.+?)['\"]?\s*[:\-–—=]\s*(.+?)(?=[\.\n])",
        r"(.+?)\s+(?:aka|also known as|aka\.)\s+(.+?)(?=[\.\n])"
    ]
}