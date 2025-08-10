COMMON_WORDS = {
    "english": [
        # Determiners / articles / quantifiers
        "the", "a", "an", "this", "that", "these", "those", "each", "every", "any", "some", "no", "none",
        "all", "both", "either", "neither", "other", "another", "such",

        # Personal / possessive pronouns
        "i", "me", "my", "mine", "you", "your", "yours", "he", "him", "his", "she", "her", "hers",
        "it", "its", "we", "us", "our", "ours", "they", "them", "their", "theirs",

        # Reflexive / emphatic
        "myself", "yourself", "himself", "herself", "itself", "ourselves", "yourselves", "themselves",

        # Question words (non-key for note extraction)
        "who", "whom", "whose", "which", "what", "when", "where", "why", "how",

        # Auxiliaries & modals (many tenses & contractions)
        "be", "am", "is", "are", "was", "were", "been", "being",
        "have", "has", "had", "having",
        "do", "does", "did", "doing",
        "will", "would", "shall", "should", "can", "could", "may", "might", "must", "ought",

        # Contractions
        "i'm", "you're", "he's", "she's", "it's", "we're", "they're",
        "i've", "you've", "we've", "they've", "i'd", "you'd", "we'd", "they'd",
        "i'll", "you'll", "he'll", "she'll", "we'll", "they'll",
        "isn't", "aren't", "wasn't", "weren't", "don't", "doesn't", "didn't",
        "haven't", "hasn't", "hadn't", "won't", "wouldn't", "can't", "couldn't", "shouldn't", "mustn't",

        # Very common verbs (base + typical inflections)
        "get", "gets", "got", "getting", "gotten",
        "make", "makes", "made", "making",
        "take", "takes", "took", "taken", "taking",
        "go", "goes", "went", "going", "gone",
        "come", "comes", "came", "coming",
        "see", "sees", "saw", "seen", "seeing",
        "look", "looks", "looked", "looking",
        "say", "says", "said", "saying",
        "tell", "tells", "told", "telling",
        "ask", "asks", "asked", "asking",
        "think", "thinks", "thought", "thinking",
        "know", "knows", "knew", "known", "knowing",
        "work", "works", "worked", "working",
        "use", "uses", "used", "using",
        "give", "gives", "gave", "given", "giving",
        "find", "finds", "found", "finding",
        "feel", "feels", "felt", "feeling",
        "leave", "leaves", "left", "leaving",
        "keep", "keeps", "kept", "keeping",
        "help", "helps", "helped", "helping",
        "start", "starts", "started", "starting", "begin", "begins", "began",
        "change", "changes", "changed", "changing",
        "show", "shows", "showed", "shown", "showing",
        "call", "calls", "called", "calling",
        "try", "tries", "tried", "trying",
        "turn", "turns", "turned", "turning",
        "talk", "talks", "talked", "talking",
        "write", "writes", "wrote", "written", "writing",
        "read", "reads", "read", "reading",
        "play", "plays", "played", "playing",
        "run", "runs", "ran", "running",
        "move", "moves", "moved", "moving",
        "live", "lives", "lived", "living",
        "believe", "believes", "believed", "believing",
        "bring", "brings", "brought", "bringing",
        "hold", "holds", "held", "holding",
        "sit", "sits", "sat", "sitting",
        "stand", "stands", "stood", "standing",
        "lose", "loses", "lost", "losing",
        "pay", "pays", "paid", "paying",
        "meet", "meets", "met", "meeting",
        "include", "includes", "included", "including",

        # Common adjectives & adverbs (often not useful as key nouns)
        "good", "bad", "better", "best", "worse", "worst",
        "big", "small", "large", "little", "new", "old", "same", "different",
        "more", "most", "less", "least", "many", "much", "few", "several",
        "very", "really", "quite", "just", "only", "already", "still", "yet", "also", "else",
        "almost", "nearly", "about", "around", "exactly", "approximately",

        # Conjunctions & discourse markers / fillers
        "and", "or", "but", "so", "because", "as", "since", "if", "though", "although", "however",
        "therefore", "thus", "hence", "meanwhile", "then", "otherwise", "besides",
        "well", "oh", "um", "uh", "erm", "like", "you know", "i mean", "sort of", "kind of", "kinda",

        # Prepositions
        "of", "in", "to", "for", "with", "on", "at", "from", "by", "about", "as", "into", "onto", "over", "under",
        "between", "among", "through", "during", "before", "after", "since", "until", "within", "without", "around", "toward", "towards",

        # Numbers & quantifiers
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "first", "second", "third", "next", "last", "few", "many", "several", "various", "multiple",

        # Time words / pragmatic
        "today", "tomorrow", "yesterday", "now", "then", "later", "soon", "ago", "recently", "again",

        # Short answers / speech tokens
        "yes", "no", "maybe", "okay", "ok", "alright", "right", "sure", "uh-huh", "hmm",

        # Neutral informal tokens (not local slang)
        "yeah", "yep", "nah", "huh", "wow", "cool",

        # Abbreviations etc.
        "etc", "e.g.", "i.e.", "vs", "vs.", "approx", "per", "each", "via"
    ],

    "portuguese": [
        # Artigos / determinantes
        "o", "a", "os", "as", "um", "uma", "uns", "umas", "este", "esta", "esses", "essas",

        # Pronomes pessoais / possessivos
        "eu", "me", "mim", "comigo", "tu", "te", "ti", "você", "voce", "vocês", "eles", "elas", "nós", "nos",
        "meu", "minha", "teu", "tua", "seu", "sua", "nosso", "nossa", "se", "si",

        # Reflexivos / enfáticos
        "mim mesmo", "si mesmo", "nós mesmos",

        # Interrogativos
        "quem", "o que", "que", "qual", "quais", "quando", "onde", "por que", "como",

        # Auxiliares / modais / formas comuns
        "ser", "sou", "é", "são", "era", "foi", "estar", "está", "estão", "estava", "estarão",
        "ter", "tem", "têm", "tinha", "haver", "há", "houve",
        "poder", "pode", "podem", "podia", "dever", "deve", "deviam",
        "fazer", "faz", "fazem", "fez", "fizeram", "ir", "vai", "vão", "fui", "foi",

        # Verbos usuais
        "dizer", "diz", "disseram", "ver", "ve", "vir", "vem", "saber", "sabe", "achar", "achar", "pensar", "pensou",

        # Adjetivos / advérbios / conectores
        "mais", "menos", "muito", "pouco", "bastante", "bem", "mal", "novo", "velho", "grande", "pequeno",
        "então", "logo", "pois", "assim", "também", "além", "assim mesmo", "portanto",

        # Conjunções / marcadores
        "e", "ou", "mas", "porém", "porque", "se", "enquanto", "quando", "entretanto", "portanto", "logo",

        # Preposições
        "de", "em", "para", "por", "com", "sobre", "como", "entre", "até", "desde", "após", "antes", "contra", "sem", "sob",

        # Números / quantificadores
        "um", "uma", "dois", "duas", "três", "primeiro", "segundo", "último", "vários", "muitos", "alguns",

        # Tempo / práticos
        "hoje", "amanhã", "ontem", "agora", "depois", "logo", "cedo", "tarde", "já", "ainda",

        # Fillers / neutral informal tokens
        "ok", "okay", "hmm", "ah", "oh", "não", "sim", "talvez", "certamente", "claro",

        # Abreviações / etc.
        "etc", "ex.", "p.ex.", "aprox", "via"
    ],

    "spanish": [
        # Artículos / determinantes
        "el", "la", "los", "las", "un", "una", "unos", "unas", "este", "esta", "estos", "estas", "ese", "esa",

        # Pronombres / posesivos
        "yo", "me", "mí", "conmigo", "tú", "te", "usted", "ustedes", "vos", "él", "ella", "nosotros", "nos", "nuestro",
        "mi", "tu", "su", "sus", "mío", "mía", "tuyo", "tuya",

        # Reflexivos
        "sí mismo", "nosotros mismos",

        # Interrogativos
        "qué", "que", "quién", "quien", "cuál", "cual", "cuándo", "cuando", "dónde", "donde", "por qué", "cómo", "como",

        # Auxiliares / verbos frecuentes
        "ser", "es", "son", "era", "fue", "fueron", "estar", "está", "están", "estaré", "haber", "hay", "hubo",
        "tener", "tiene", "tuvo", "tener que", "poder", "puede", "podría", "deber", "hacer", "hace", "ir", "va", "venir",

        # Verbos comunes
        "decir", "dice", "dijo", "ver", "ve", "vio", "pensar", "piensa", "creer", "creo", "saber", "supo",

        # Adjetivos / adverbios / conectores
        "más", "menos", "muy", "mucho", "poco", "bien", "mal", "otro", "otra", "nuevo", "viejo",
        "entonces", "por tanto", "por eso", "además", "así", "así que", "por lo tanto",

        # Conjunciones / marcadores
        "y", "o", "pero", "porque", "si", "aunque", "mientras", "luego", "entonces",

        # Preposiciones
        "de", "en", "a", "por", "con", "sobre", "entre", "hasta", "desde", "sin", "bajo", "hacia",

        # Números / cuantificadores
        "uno", "dos", "tres", "primero", "segundo", "varios", "muchos", "algunos",

        # Fillers / neutral informal tokens
        "ok", "okay", "hmm", "ah", "oh", "vale", "bueno", "quizás", "tal vez", "sí", "no",

        # Abreviaturas / etc
        "etc", "ej.", "p.ej.", "aprox", "via"
    ],

    "italian": [
        # Articoli / determinanti
        "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "questo", "quello", "questi", "quelle",

        # Pronomi / possessivi
        "io", "me", "mi", "con me", "tu", "te", "ti", "lui", "lei", "noi", "voi", "loro", "mio", "mia", "tuo", "tua",

        # Riflessivi
        "me stesso", "te stesso", "se stesso", "noi stessi",

        # Interrogativi
        "chi", "che", "che cosa", "cosa", "quando", "dove", "come", "perché", "quanto", "quale",

        # Ausiliari / verbi frequenti
        "essere", "sono", "è", "eravamo", "stare", "sta", "stanno", "avere", "ho", "hai", "ha", "abbiamo", "hanno",
        "fare", "fa", "fanno", "andare", "va", "vanno", "venire", "viene", "potere", "può", "dovere", "deve",

        # Verbi comuni
        "dire", "dice", "detto", "vedere", "vede", "visto", "sapere", "sa", "pensare", "penso", "trovare", "trova",

        # Aggettivi / avverbi / connettori
        "più", "meno", "molto", "poco", "bene", "male", "nuovo", "vecchio", "grande", "piccolo",
        "allora", "quindi", "dunque", "però", "cioè", "inoltre", "anche",

        # Congiunzioni / preposizioni
        "e", "o", "ma", "perché", "se", "quindi", "pertanto", "di", "a", "da", "in", "su", "per", "con", "tra", "fra",

        # Numerali
        "uno", "due", "tre", "primo", "secondo", "molti", "alcuni",

        # Fillers / neutral informal tokens
        "ok", "okay", "ah", "oh", "hmm", "d'accordo", "forse", "sì", "no",

        # Abbreviazioni / etc
        "ecc", "ecc.", "etc", "es.", "p.es."
    ],

    "french": [
        # Articles / déterminants
        "le", "la", "les", "un", "une", "des", "ce", "cet", "cette", "ces", "cela", "ça", "celui", "celle",

        # Pronoms / possessifs
        "je", "me", "moi", "tu", "te", "toi", "il", "elle", "nous", "vous", "ils", "elles",
        "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses", "notre", "nos", "votre", "vos", "leur", "leurs",

        # Réflexifs
        "moi-même", "toi-même", "nous-mêmes",

        # Interrogatifs
        "qui", "que", "quoi", "comment", "pourquoi", "quand", "où", "combien", "lequel", "laquelle",

        # Auxiliaires / verbes fréquents
        "être", "suis", "est", "sommes", "sont", "avoir", "ai", "a", "avons", "ont",
        "faire", "fait", "faire", "aller", "va", "vont", "pouvoir", "peut", "devoir", "doit",

        # Verbes fréquents
        "dire", "dit", "dire", "voir", "voit", "savoir", "sait", "penser", "penser",

        # Adjectifs / adverbes / connecteurs
        "plus", "moins", "très", "beaucoup", "peu", "bien", "mal", "autre", "même", "nouveau", "ancien",
        "alors", "donc", "parce que", "car", "mais", "ou", "et", "ainsi", "enfin", "puis",

        # Marqueurs / fillers neutres
        "alors", "donc", "voilà", "ben", "euh", "bah", "quoi", "bon", "ok", "d'accord",

        # Prépositions / conjonctions
        "de", "à", "dans", "par", "pour", "sur", "avec", "sans", "entre", "chez", "vers", "après", "avant",

        # Numéraux / quantificateurs
        "un", "deux", "trois", "premier", "second", "plusieurs", "quelques", "beaucoup",

        # Abbréviations
        "etc", "p.ex.", "ex.", "i.e."
    ],

    "romanian": [
        # Articole / determinanți
        "un", "o", "niște", "cei", "acei", "această", "acest", "aceea", "acela",

        # Pronume / posesive
        "eu", "mă", "îmi", "tu", "îți", "el", "ea", "noi", "ne", "voi", "vă", "ei", "ele",
        "meu", "mea", "tău", "ta", "său", "nostru", "noastră", "vostru",

        # Reflexive
        "mă însumi", "tu însuți", "noi înșine",

        # Interogative
        "cine", "ce", "care", "când", "unde", "de ce", "cum", "cât", "câți", "câte",

        # Auxiliare / verbe comune
        "a fi", "este", "sunt", "era", "erau", "a avea", "are", "au", "avea", "a face", "face", "merge", "vine",
        "putea", "trebuie", "poate", "vrea", "vor", "spune", "vede", "știu",

        # Verbe frecvente
        "zice", "zic", "știu", "am", "ai", "are", "avem", "au", "făcut", "făceam",

        # Adverbe / adjective / conectoare
        "mai", "mai puțin", "foarte", "mult", "puțin", "bine", "rău", "nou", "vechi", "altul",

        # Conjuncții / filler
        "și", "sau", "dar", "deoarece", "pentru că", "dacă", "în timp ce", "deci", "atunci",

        # Prepoziții
        "de", "la", "în", "pe", "cu", "fără", "pentru", "sub", "peste", "între", "prin",

        # Numerale
        "unu", "doi", "trei", "primul", "al doilea", "mai mulți", "câțiva",

        # Neutral fillers / tokens
        "ok", "hmm", "ah", "oh", "da", "nu", "poate", "mulțumesc"
    ],

    "default": [
        # Generic fallback - core function words
        "the", "a", "an", "and", "or", "but", "of", "in", "to", "for", "with", "on", "at", "from",
        "is", "are", "was", "were", "be", "have", "has", "had", "do", "does", "did", "that", "this", "these", "those",
        "ok", "etc", "e.g.", "i.e."
    ]
}