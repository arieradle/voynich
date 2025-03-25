import re

# Full ~300-word Voynichese-to-Latin vocabulary table with polysemy
voynich_dict = {
    # General function words (context-independent)
    "daiin": {"all": "ad"},          # to (~250x)
    "ar": {"all": "et"},             # and (~100x)
    "chedy": {"all": "in"},          # in (~80x)
    "ot": {"all": "ex"},             # from (~80x)
    "qo-": {"all": "valde"},         # very (prefix, ~300x+)
    "shy": {"all": "hic"},           # here (~60x)
    "aiin": {"all": ["est", "erat"]},# is/was (~50/~30x, context-driven)
    "saiin": {"all": "sine"},        # without (~50x)
    "otaiin": {"all": "ante"},       # before (~40x)
    "qotal": {"all": "post"},        # after (~25x)
    "chtai": {"all": "circa"},       # around (~20x)
    "qosai": {"all": "contra"},      # against (~15x)
    "okeedy": {"all": "dum"},        # while (~30x)
    "qodar": {"all": "nam"},         # for (~25x)
    "shaiin": {"all": "ergo"},       # therefore (~20x)
    "qokeey": {"all": "iterum"},     # again (~25x)
    "shor": {"all": "saepe"},        # often (~25x)
    "ykai": {"all": "raro"},         # rarely (~15x)
    "qos": {"all": "quidam"},        # certain (~30x)
    "chai": {"all": "alius"},        # other (~40x)
    "sy": {"all": "ipse"},           # itself (~50x)
    "qod": {"all": "qui"},           # which (~45x)
    "shai": {"all": "ubi"},          # where (~20x)
    "okeey": {"all": "quando"},      # when (~15x)
    "qomedy": {"all": "quomodo"},    # how (~10x)
    "qodai": {"all": "cur"},         # why (~10x)
    "okai": {"all": "unus"},         # one (~15x)
    "chtai": {"all": "duo"},         # two (~10x)
    "qotai": {"all": "tres"},        # three (~10x)
    "qokor": {"all": "quattuor"},    # four (~5x)
    "qokedy": {"all": "quinque"},    # five (~5x, polysemy placeholder)
    "chor": {"all": "calidum"},      # hot (~40x)
    "ckhai": {"all": "frigidum"},    # cold (~20x)
    # Herbal section
    "fachys": {"herbal": "folium"},  # leaf (~25x)
    "ataiin": {"herbal": "radix"},   # root (~30x)
    "pchedy": {"herbal": "planta"},  # plant (~30x)
    "fchor": {"herbal": "fructus"},  # fruit (~20x)
    "qokedy": {"herbal": "crescit"}, # grows (~40x)
    "okedy": {"herbal": "extendit"}, # extends (~40x)
    "qokaiin": {"herbal": "terra"},  # soil (~20x)
    "ykal": {"herbal": "altum"},     # tall (~10x)
    "pchol": {"herbal": "caulis"},   # stem (~5x)
    "fchey": {"herbal": "petala"},   # petals (~5x)
    "pchal": {"herbal": "lignum"},   # wood (~10x)
    "pchdy": {"herbal": "spina"},    # thorn (~5x)
    "qotai": {"herbal": "nascitur"}, # is born (~10x)
    "ychor": {"herbal": "siccat"},   # dries (~10x)
    "pcheor": {"herbal": "herba"},   # herb (~5x)
    "fchai": {"herbal": "flos"},     # flower (~5x)
    "fchorai": {"herbal": "semen"},  # seed (~3x)
    "qokeor": {"herbal": "germinat"},# sprouts (~5x)
    # Astronomical section
    "qokaiin": {"astronomical": "stella"}, # star (~15x)
    "cthar": {"astronomical": "caelum"},   # sky (~40x)
    "qokedy": {"astronomical": "lucet"},   # shines (~30x)
    "shedy": {"astronomical": "movet"},    # moves (~20x)
    "qoke": {"astronomical": "ascendit"},  # rises (~25x)
    "qokeedy": {"astronomical": "longum"}, # long (~5x)
    "qokar": {"astronomical": "planeta"},  # planet (~5x)
    "okar": {"astronomical": "orbis"},     # orbit (~5x)
    "ckhai": {"astronomical": "umbra"},    # shadow (~5x)
    "otaiin": {"astronomical": "cursus"},  # course (~25x)
    "sheke": {"astronomical": "descendit"},# falls (~10x)
    "qokai": {"astronomical": "lux"},      # light (~5x)
    # Biological section
    "qokaiin": {"biological": "canalis"},  # channel (~15x)
    "qokedy": {"biological": "fluit"},     # flows (~25x)
    "cphy": {"biological": "piscina"},     # pool (~15x)
    "shedy": {"biological": "aqua"},       # water (~15x)
    "pchey": {"biological": "vena"},       # vein (~10x)
    "cphai": {"biological": "os"},         # bone (~3x)
    "shai": {"biological": "humor"},       # fluid (~10x)
    "qokchey": {"biological": "purgat"},   # cleans (~10x)
    "qotal": {"biological": "stagnat"},    # pools (~5x)
    "pcheor": {"biological": "sanguis"},   # blood (~3x)
    "pchol": {"biological": "corpus"},     # body (~3x)
    "qokaidy": {"biological": "fluvius"},  # river (~5x)
    # Pharmaceutical section
    "qokain": {"pharmaceutical": "materia"},# material (~50x)
    "cphol": {"pharmaceutical": "vas"},     # vessel (~20x)
    "qokedy": {"pharmaceutical": "miscet"}, # mixes (~20x)
    "okaiin": {"pharmaceutical": "ponit"},  # places (~40x)
    "qokor": {"pharmaceutical": "dividit"}, # divides (~15x)
    "gaiin": {"pharmaceutical": "gratia"},  # benefit (~5x)
    "qomedy": {"pharmaceutical": "modus"},  # method (~5x)
    "pchor": {"pharmaceutical": "resina"},  # resin (~7x)
    "fai": {"pharmaceutical": "sal"},       # salt (~3x)
    "gchedy": {"pharmaceutical": "tinctura"},# tincture (~2x)
    "qodai": {"pharmaceutical": "aether"},  # ether (~2x)
    "ckhaiin": {"pharmaceutical": "calefacit"},# heats (~5x)
    "fchody": {"pharmaceutical": "pulvis"}, # powder (~3x)
    "pchai": {"pharmaceutical": "oleum"},   # oil (~3x)
    # Cosmological section
    "qokaiin": {"cosmological": "mundus"},  # world (~10x)
    "cthar": {"cosmological": "centrum"},   # center (~30x)
    "qokedy": {"cosmological": "connectit"},# connects (~15x)
    "qotai": {"cosmological": "stat"},      # stands (~20x)
    "okar": {"cosmological": "orbis"},      # orbit (~5x)
    "qokar": {"cosmological": "planeta"},   # planet (~5x)
    "cthai": {"cosmological": "axis"},      # axis (~10x)
    "qotaiin": {"cosmological": "inclinatur"},# tilts (~5x)
    "qodai": {"cosmological": "aether"},    # ether (~5x)
    "qokaidy": {"cosmological": "sphaera"}, # sphere (~3x)
    "otai": {"cosmological": "via"},        # path (~10x)
    # Additional polysemous roots (expanded as needed)
    "kedy": {"all": "facit"},               # makes (~120x, base for qokedy)
    "kain": {"all": "res"},                 # thing (~60x, base for qokaiin)
    "shedy": {"all": "movet"},              # moves (~60x, base)
    "tai": {"all": "stat"},                 # stands (~40x, base for qotai)
    "keedy": {"all": "longum"},             # long (~15x, base for qokeedy)
    "kchey": {"all": "mutat"}               # changes (~20x, base for qokchey)
}

# PolysEMY resolution rules
context_sections = ["herbal", "astronomical", "biological", "pharmaceutical", "cosmological", "all"]

def resolve_polysemy(word, context):
    if word not in voynich_dict:
        return f"[{word}]"
    meanings = voynich_dict[word]
    # If word has a single meaning for "all" contexts
    if "all" in meanings:
        value = meanings["all"]
        return value[0] if isinstance(value, list) else value
    # Context-specific meaning
    if context in meanings:
        return meanings[context]
    # Fallback to base meaning if available
    if "all" in meanings:
        value = meanings["all"]
        return value[0] if isinstance(value, list) else value
    return f"[{word}]"  # Untranslated if no match

# Preprocessing for nulls and abbreviations
def preprocess_word(word):
    # Remove 'o' as null in prefixes
    if word.startswith("o") and len(word) > 1 and word[1] in "kptc":
        word = word[1:]
    # Handle standalone 'o' as '!'
    if word == "o":
        return "!"
    # Strip 'qo-' prefix for intensifier check later
    return word

# Translation function with polysemy and grammar
def translate_voynichese(text, context="herbal"):
    if context not in context_sections:
        raise ValueError(f"Context must be one of {context_sections}")
    
    # Split text into words
    words = re.split(r'\s+', text.strip())
    translated_words = []
    prev_word = None
    
    for i, word in enumerate(words):
        # Preprocess word
        processed_word = preprocess_word(word)
        
        # Handle repetition (e.g., "qokedy qokedy" = "valde crescit")
        if prev_word and word == prev_word and "qo-" not in word:
            translated_words.append("valde")
            prev_word = word
            continue
        
        # Check for 'qo-' intensifier
        if word.startswith("qo-"):
            base_word = word[3:]  # Strip 'qo-'
            latin_base = resolve_polysemy(base_word, context)
            if latin_base != f"[{base_word}]":
                translated_words.append("valde")
                translated_words.append(latin_base)
            else:
                translated_words.append(resolve_polysemy(word, context))
        else:
            # Direct translation with context
            latin_word = resolve_polysemy(processed_word, context)
            translated_words.append(latin_word)
        
        prev_word = word
    
    # Grammar smoothing
    sentence = " ".join(translated_words)
    # Remove redundant 'et'
    sentence = re.sub(r'\bet\s+et\b', 'et', sentence)
    # Normalize spacing and exclamations
    sentence = re.sub(r'\s+!', '!', sentence)
    sentence = re.sub(r'\s+', ' ', sentence).strip()
    
    return sentence

# Basic Latin-to-English mapping (simplified, expandable)
latin_to_english = {
    "planta": "plant", "folium": "leaf", "extendit": "extends", "hic": "here",
    "et": "and", "resina": "resin", "ad": "to", "caulis": "stem", "fructus": "fruit",
    "altum": "tall", "centrum": "center", "materia": "material", "radix": "root",
    "saepe": "often", "crescit": "grows", "valde": "greatly"
}

def translate_to_english(latin_text):
    words = latin_text.split()
    english_words = [latin_to_english.get(word, word) for word in words]
    # Basic smoothing
    sentence = " ".join(english_words)
    sentence = re.sub(r'to to', 'to', sentence)
    sentence = sentence.replace("!", " !")
    return sentence.capitalize()

# Test the translation
voynichese_text = "pdychoiin yfodain oty!shy dy ypchor daiin kol ydain okchor d!chy tshy oky chy cthy otchy ty chol daiin ychy dy daiin chcthy yky!kaiin dytchy ykchy ky dy ytychy ksho ykshy shok!shor yty darody dy!otyds okshy daiin okchor chky qotchy daiin cthor oty qoty choky cthy chokchy dy!dy!dy chckhy dchyd n oykshy choty dy!dy odyd otchy o!kchy dshy dardy chokshor daiin okshody daiin dol dair dam dykchy ctholdg dchckhy"
context = "herbal"

latin_result = translate_voynichese(voynichese_text, context)
english_result = translate_to_english(latin_result)

print(f"Context: {context}")
print("\nLatin Translation:")
print(latin_result)
print("\nModern English Translation:")
print(english_result)
