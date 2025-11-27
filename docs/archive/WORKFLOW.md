# Voynich Translation Workflow

This document explains how to use the automated translation pipeline.

## 🎯 Overview

The workflow consists of three main steps:

1. **Download** folios from voynich.nu
2. **Translate** using the deterministic dictionary
3. **Analyze** gaps and extend the dictionary

## 📋 Setup

Install dependencies:
```bash
pip install httpx pyyaml
```

## 🚀 Quick Start

### Step 1: Download Folios

Download a batch of folios from a specific section:

```bash
# Download Herbal B folios 1-20
python download_folios.py --section q02 --start 1 --end 20

# Download Astronomical folios 67-75
python download_folios.py --section q04 --start 67 --end 75

# List what's cached
python download_folios.py --list
```

**Available sections:**
- `q01` - Herbal A
- `q02` - Herbal B
- `q03` - Biological
- `q04` - Astrological  
- `q05` - Pharmaceutical
- `q13` - Stars
- `q20` - Text-only

### Step 2: Translate Folios

Translate a single folio:
```bash
# Translate folio 14v from Herbal B
python translate_folio.py --section q02 --folio 014v

# Specify context explicitly
python translate_folio.py --section q02 --folio 014v --context herbal
```

Batch translate multiple folios:
```bash
# Translate folios 1-10 from Herbal B
python translate_folio.py --section q02 --start 1 --end 10
```

View a translation:
```bash
python translate_folio.py --section q02 --show 014v
```

### Step 3: Analyze Gaps

After translating several folios, analyze what's missing from the dictionary:

```bash
# Analyze gaps (words appearing 2+ times)
python analyze_gaps.py --min-freq 2 --max-suggestions 20

# More aggressive (words appearing 1+ times)
python analyze_gaps.py --min-freq 1 --max-suggestions 50
```

This generates:
- **Console report** with top unknown words and suggestions
- **JSON file** (`data/dictionary_suggestions.json`) for review

## 📁 File Structure

```
voynich/
├── download_folios.py       # Download script
├── translator.py            # Core translation engine
├── translate_folio.py       # CLI translator
├── analyze_gaps.py          # Gap analysis
├── voynich.yaml            # Dictionary & rules
├── data/
│   ├── folios/             # Downloaded folios (cached)
│   │   ├── q02_f014v.txt
│   │   └── metadata.json
│   ├── translations/       # Translation outputs
│   │   └── q02_f014v_translation.json
│   └── dictionary_suggestions.json  # Suggested additions
```

## 🔄 Iterative Workflow

### Iteration 1: First Pass

```bash
# 1. Download untested folios
python download_folios.py --section q02 --start 21 --end 30

# 2. Translate them
python translate_folio.py --section q02 --start 21 --end 30

# 3. Analyze gaps
python analyze_gaps.py --min-freq 3
```

### Iteration 2: Review & Extend

1. **Review suggestions** in `data/dictionary_suggestions.json`
2. **Research patterns** - look at folio images, compare with known words
3. **Update voynich.yaml** - add new vocabulary entries
4. **Re-translate** with updated dictionary:
   ```bash
   python translate_folio.py --section q02 --folio 021r --force
   ```

### Iteration 3: Validate

```bash
# Re-analyze with updated dictionary
python analyze_gaps.py --min-freq 2

# Check if coverage improved
python translate_folio.py --section q02 --show 021r
```

## 📊 Understanding Output

### Translation JSON Structure

```json
{
  "folio_id": "014v",
  "section": "Herbal B",
  "context": "herbal",
  "voynich_text": "pdychoiin yfodain oty shy...",
  "latin_text": "planta folium ex hic...",
  "word_translations": [
    {
      "original": "pdychoiin",
      "latin": "planta",
      "confidence": 0.9,
      "notes": "near plants"
    }
  ],
  "statistics": {
    "total": 45,
    "known": 38,
    "unknown": 7,
    "coverage": 0.844,
    "avg_confidence": 0.82
  },
  "unknown_words": ["word1", "word2"]
}
```

### Gap Analysis Output

- **Frequency**: How many times the word appears
- **Sections**: Which manuscript sections contain it
- **Priority**: Calculated importance score
- **Analysis**: Structural patterns (prefixes, suffixes, roots)
- **Suggestions**: Educated guesses based on patterns

## 🎯 Dictionary Extension Guidelines

When reviewing suggestions, consider:

1. **Frequency** - High-frequency words are most important
2. **Context** - Does it appear in specific sections?
3. **Structure** - Does it follow known patterns?
4. **Visuals** - Look at the folio image for context clues
5. **Existing roots** - Is it a compound of known words?

### Adding to voynich.yaml

For a new word `newword` → `novum`:

```yaml
vocab:
  - word: newword
    description: "appears near X in folios Y"
    latin: novum
```

For polysemous words (different meanings by section):

```yaml
polysemy:
  - word: newword
    meanings:
      - latin: novum
        context: "herbal section, near plants"
      - latin: stella
        context: "astronomical section, near stars"
    base: novum
```

## 🔧 Advanced Usage

### Test Translator Directly

```bash
python translator.py
```

### Custom Context

```bash
python translate_folio.py --section q04 --folio 067r --context astronomical
```

### Force Re-download

```bash
python download_folios.py --section q02 --start 1 --end 5 --force
```

## 📝 Next Steps

1. Start with well-illustrated folios (Herbal sections)
2. Build up vocabulary in one section first
3. Test polysemy by comparing same words across sections
4. Validate with visual context from folio images
5. Document reasoning for each addition

## 🤝 AI-Assisted Review

After running analyze_gaps.py, you can:

1. Share suggestions with AI for pattern analysis
2. Request image lookups for specific folios
3. Cross-reference with existing translations
4. Validate etymological connections

