# Voynich Translation System - Development Guide
# Complete Usage Instructions and Quick Start

This guide consolidates all practical information for using, extending, and improving the Voynich translation system.

---

## 🎉 System Overview

You now have a fully functional pipeline for:
1. **Downloading** Voynich manuscript folios from voynich.nu
2. **Translating** them deterministically (Latin + English)
3. **Analyzing** gaps and identifying vocabulary priorities
4. **Extending** the dictionary systematically
5. **Validating** improvements through metrics

---

## 📦 Script Reference

### Core Scripts

| Script | Purpose | Example |
|--------|---------|---------|
| `download_folios.py` | Download and cache folios | `python download_folios.py --section q02 --start 1 --end 20` |
| `translator.py` | Core translation engine | Used by other scripts (library) |
| `translate_folio.py` | Translate cached folios | `python translate_folio.py --section q02 --folio 014v` |
| `analyze_gaps.py` | Find unknown words | `python analyze_gaps.py --min-freq 2` |
| `review_and_update.py` | Update dictionary | `python review_and_update.py --add-examples` |

### Helper Scripts (in `scripts/`)

| Script | Purpose | Example |
|--------|---------|---------|
| `word_frequency.py` | Frequency analysis | `python scripts/word_frequency.py --min-freq 5` |
| `morphology_analyzer.py` | Morphological decomposition | `python scripts/morphology_analyzer.py --word kokaiin` |
| `pattern_detector.py` | Pattern detection | `python scripts/pattern_detector.py --pattern-type all` |
| `compound_decomposer.py` | Compound word analysis | `python scripts/compound_decomposer.py --word qotchedy` |
| `batch_dictionary_updater.py` | Dictionary updates | `python scripts/batch_dictionary_updater.py --interactive` |
| `validation_checker.py` | Integrity checks | `python scripts/validation_checker.py --check-type all` |
| `iteration_orchestrator.py` | Full workflow automation | `python scripts/iteration_orchestrator.py --validation-gates` |

---

## 🚀 Quick Start

### Complete Workflow Example

```bash
# 1. Download some folios
python download_folios.py --section q02 --start 14 --end 16

# 2. Translate them
python translate_folio.py --section q02 --start 14 --end 16

# 3. Analyze what's missing
python analyze_gaps.py --min-freq 2

# 4. Review suggestions and update dictionary
python scripts/batch_dictionary_updater.py --interactive

# 5. Re-translate with updated dictionary
python translate_folio.py --section q02 --folio 014v --force
```

### 5-Minute Quick Test

```bash
# Translate a single folio
python translate_folio.py --section q02 --folio 014r

# View the results
python translate_folio.py --section q02 --show 014r
```

---

## 📋 Installation & Setup

### Dependencies

```bash
pip install httpx pyyaml
```

### Verify Installation

```bash
# Check system status
python scripts/validation_checker.py --check-type all

# Should output: "✅ VALIDATION PASSED"
```

### File Structure

```
voynich/
├── Core Scripts (download, translate, analyze)
├── scripts/ (helper utilities)
├── voynich.yaml (708-word dictionary)
├── data/
│   ├── folios/ (downloaded transcriptions)
│   ├── translations/ (JSON outputs)
│   └── dictionary_suggestions.json (gap analysis)
└── Documentation (this file and others)
```

---

## 🔄 Iterative Improvement Workflow

### Phase 1: Explore New Folios

**Download untested folios:**
```bash
# Herbal sections (well-illustrated, easier to validate)
python download_folios.py --section q01 --start 1 --end 8
python download_folios.py --section q02 --start 14 --end 16

# Other sections (when ready)
python download_folios.py --section q04 --start 67 --end 72  # Astronomical
python download_folios.py --section q05 --start 101 --end 105  # Pharmaceutical
```

**Translate them all:**
```bash
python translate_folio.py --section q01 --start 1 --end 8
python translate_folio.py --section q02 --start 14 --end 16
```

### Phase 2: Analyze Patterns

**Find high-frequency unknown words:**
```bash
# Standard analysis (words appearing 3+ times)
python scripts/word_frequency.py --min-freq 3 --format json --output data/unknown_ranked.json

# Generate markdown report for easier reading
python scripts/word_frequency.py --min-freq 5 --format md --output data/frequency_report.md
```

**Detect patterns:**
```bash
# All pattern types
python scripts/pattern_detector.py --pattern-type all --min-occurrences 3

# Formulaic phrases only
python scripts/pattern_detector.py --pattern-type formulaic --min-occurrences 5
```

**Comprehensive gap analysis:**
```bash
python analyze_gaps.py --min-freq 3 --max-suggestions 50
# Creates: data/dictionary_suggestions.json
```

### Phase 3: Morphological Analysis

**Analyze single word:**
```bash
python scripts/morphology_analyzer.py --word kokaiin
```

**Batch analysis:**
```bash
# Create a file with high-priority words (one per line)
echo "kokaiin
schy
otchody" > priority_words.txt

python scripts/morphology_analyzer.py --batch-file priority_words.txt --output data/morphology_analysis.json
```

**Generate word families:**
```bash
# Generate systematic variations of a known root
python scripts/morphology_analyzer.py --generate-family chol
```

**Compound decomposition:**
```bash
# Try all strategies
python scripts/compound_decomposer.py --word qotchedy --strategy all

# Heuristic strategy (usually best)
python scripts/compound_decomposer.py --word qotchedy --strategy heuristic
```

### Phase 4: Update Dictionary

#### Option A: Interactive Mode (Recommended)

```bash
python scripts/batch_dictionary_updater.py --interactive --backup

# Follow prompts:
# Format: word|latin|description
# Example: kokaiin|maturat|appears near fruits/seeds; kok + aiin compound
```

#### Option B: Manual Edit

Edit `voynich.yaml`:

```yaml
vocab:
  - word: kokaiin
    latin: maturat
    description: "appears near fruits/seeds; kok + aiin compound"
    
  - word: schy
    latin: hic tangit
    description: "s + chy compound, describing touch"
```

#### Option C: Batch Import

Create `approved_words.json`:
```json
[
  {
    "word": "kokaiin",
    "latin": "maturat",
    "description": "appears near fruits/seeds; kok + aiin compound"
  },
  {
    "word": "schy",
    "latin": "hic tangit",
    "description": "s + chy compound, describing touch"
  }
]
```

Then import:
```bash
python scripts/batch_dictionary_updater.py --import-file approved_words.json --backup
```

### Phase 5: Validate Changes

**Validate dictionary:**
```bash
python scripts/validation_checker.py --check-type all

# Should output:
# ✓ YAML syntax valid
# ✓ No duplicates found
# ✓ All entries have required fields
```

**Re-translate with updated dictionary:**
```bash
# Force re-translation
python translate_folio.py --section q01 --start 1 --end 8 --force
python translate_folio.py --section q02 --start 14 --end 16 --force
```

**Check improvements:**
```bash
# Re-analyze gaps
python analyze_gaps.py --min-freq 5 --max-suggestions 20

# View specific folio
python translate_folio.py --section q02 --show 014r

# Look for coverage increase in statistics
```

### Phase 6: Measure Progress

**Track metrics:**
```bash
# Count vocabulary entries
grep -c "^  - word:" voynich.yaml

# Check for duplicates
python scripts/validation_checker.py --check-type dictionary
```

**Generate reports:**
```bash
# Create iteration report
# (Manual: document what was added, coverage improvements, next priorities)
```

---

## 📖 Complete Command Reference

### Download Commands

```bash
# Single section with auto-detected range
python download_folios.py --section q01

# Custom range
python download_folios.py --section q01 --start 1 --end 5

# Force re-download with cleaning
python download_folios.py --section q01 --force

# List cached folios
python download_folios.py --list
```

### Translation Commands

```bash
# Single folio
python translate_folio.py --section q02 --folio 014v

# Batch translate
python translate_folio.py --section q01 --start 1 --end 8

# Force re-translate
python translate_folio.py --section q01 --start 1 --end 8 --force

# Show existing translation
python translate_folio.py --section q01 --show 001r

# Custom context
python translate_folio.py --section q04 --folio 067r --context astronomical
```

### Analysis Commands

```bash
# Word frequency analysis
python scripts/word_frequency.py --min-freq 5 --format json
python scripts/word_frequency.py --min-freq 10 --top 20 --format md

# Gap analysis
python analyze_gaps.py --min-freq 3 --max-suggestions 30
python analyze_gaps.py --min-freq 10 --max-suggestions 10  # High-priority only

# Pattern detection
python scripts/pattern_detector.py --pattern-type all --min-occurrences 3
python scripts/pattern_detector.py --pattern-type pairs --section q01

# Morphological analysis
python scripts/morphology_analyzer.py --word kokaiin
python scripts/morphology_analyzer.py --batch-file words.txt --output analysis.json

# Compound decomposition
python scripts/compound_decomposer.py --word qotchedy --strategy all
python scripts/compound_decomposer.py --batch-file unknowns.txt
```

### Dictionary Commands

```bash
# Interactive update
python scripts/batch_dictionary_updater.py --interactive --backup

# Batch import
python scripts/batch_dictionary_updater.py --import-file words.json --backup

# Add single word
python scripts/batch_dictionary_updater.py --add-word kokaiin --latin maturat --description "ripens"

# Validate only (no changes)
python scripts/batch_dictionary_updater.py --import-file words.json --validate-only
```

### Validation Commands

```bash
# Validate all
python scripts/validation_checker.py --check-type all

# Validate dictionary only
python scripts/validation_checker.py --check-type dictionary

# Validate translations
python scripts/validation_checker.py --check-type translations

# Generate report
python scripts/validation_checker.py --check-type all --report-file validation_report.json
```

### Orchestration Commands

```bash
# Full iteration with validation gates
python scripts/iteration_orchestrator.py --validation-gates

# Auto mode (bypass some gates)
python scripts/iteration_orchestrator.py --auto-mode

# Target specific coverage
python scripts/iteration_orchestrator.py --target-coverage 0.65 --validation-gates

# Multiple iterations
python scripts/iteration_orchestrator.py --iterations 3 --auto-mode
```

---

## 🎯 Strategy & Best Practices

### 1. Start with High-Frequency Words

**Why:** Maximum impact per word added

**How:**
- Use `--min-freq 10` or `--min-freq 15` to focus on top priorities
- Words appearing 20+ times are critical
- Words appearing 10-19 times are high priority

**Example:**
```bash
python scripts/word_frequency.py --min-freq 15 --top 20
```

### 2. Focus on Structural Patterns

**Common Patterns:**
- **qo- prefix**: Intensifier ("very") or specific verb
- **-edy suffix**: Verb marker (action/movement)
- **-aiin suffix**: State marker (is/was)
- **ch- prefix**: Common in herbal terms

**How to use:**
- Identify patterns in unknown words
- Look for known roots within compounds
- Build word families systematically

### 3. Cross-Reference Sections

**Check for polysemy:**
- Same word in different sections → may have different meanings
- Example: `qokedy` = "grows" (herbal) / "shines" (astronomical)

**How:**
```bash
# Check where word appears
grep -r "wordname" data/folios/
```

### 4. Use Visual Context

**Download folio images:**
- Visit https://voynich.nu/q01/f001r.jpg (replace with relevant folio)
- Match unknown words with visible elements
- Near plants? → botanical term
- Near stars? → astronomical term

### 5. Build on Roots

**Example:**
- If "kedy" = "facit" (makes)
- Then "qokedy" likely = "valde facit" (makes greatly)
- Add as dictionary entry or polysemy

### 6. Document Reasoning

**In descriptions:**
```yaml
- word: kokaiin
  latin: maturat
  description: "kok (makes) + aiin (is/was) = ripens; appears near fruits/seeds"
```

**Why:**
- Future reference
- Pattern identification
- Easier refinement

---

## 📊 Understanding Output Formats

### Translation JSON Structure

```json
{
  "folio_id": "014v",
  "section": "Herbal B",
  "context": "herbal",
  "voynich_text": "fachys ykal ar shy daiin...",
  "latin_text": "folium altum et hic ad...",
  "english_text": "leaf tall and here to...",
  "word_translations": [
    {
      "original": "fachys",
      "latin": "folium",
      "english": "leaf",
      "confidence": 0.9,
      "method": "dictionary",
      "notes": "near plants"
    }
  ],
  "statistics": {
    "total_words": 267,
    "known_words": 122,
    "unknown_words": 145,
    "coverage": 0.457,
    "avg_confidence": 0.82
  },
  "unknown_words": ["word1", "word2", ...]
}
```

### Gap Analysis Output

```json
{
  "word": "kokaiin",
  "frequency": 20,
  "priority_score": 285.0,
  "sections": ["q01", "q02"],
  "contexts": ["herbal"],
  "length": 7,
  "analysis": {
    "structure": {
      "prefixes": [],
      "suffixes": ["aiin"],
      "potential_roots": ["kok"]
    }
  },
  "suggested_latin": "maturat",
  "reasoning": "Appears near fruits/seeds; kok + aiin compound"
}
```

---

## 🎯 Next Iteration: Priority Words

### Top 10 High-Priority Unknowns

These 10 words appear **175 times** total. Adding them should boost coverage by **~3-5%**.

1. **kokaiin** (20x) → "maturat" (ripens)
   - Pattern: kok + aiin = makes + is = ripens
   - Context: Near fruits/seeds

2. **schy** (19x) → "hic tangit" (here touches)
   - Pattern: s + chy
   - Context: Physical plant features

3. **ols** (19x) → "aut" (or)
   - Pattern: Short function word
   - Context: Conjunction

4. **otchody** (18x) → "variat extensum" (varies extended)
   - Pattern: ot + chod + y
   - Context: Growth patterns

5. **dan** (17x) → "de" (from/of)
   - Pattern: Preposition
   - Context: Source/possession

6. **qokchor** (16x) → "valde ramulus" (very branch)
   - Pattern: qo + kchor
   - Context: Branching structure

7. **qotchey** (16x) → "valde tangit" (very touches)
   - Pattern: qo + tchey
   - Context: Physical contact

8. **qoy** (16x) → "valde ad" (very to)
   - Pattern: qo + y
   - Context: Directional movement

9. **yty** (16x) → "transit" (passes through)
   - Pattern: y-t-y
   - Context: Flow or passage

10. **charod** (16x) → "plantae variatio" (plant variation)
    - Pattern: char + od
    - Context: Plant differences

---

## 🛠️ Advanced: Morphological Parser

When ready for a major leap in coverage (~10-15%), build a morphological parser:

### Concept

```python
class MorphologicalAnalyzer:
    def __init__(self, dictionary):
        self.dict = dictionary
        self.prefixes = ['qo', 'ot', 'dy', 'ch', 's', 'y']
        self.suffixes = ['ain', 'aiin', 'edy', 'ody', 'idy', 'ar', 'or', 'ol']
    
    def decompose(self, word):
        # Try: prefix + root + suffix
        for prefix in self.prefixes:
            if word.startswith(prefix):
                remainder = word[len(prefix):]
                for suffix in self.suffixes:
                    if remainder.endswith(suffix):
                        root = remainder[:-len(suffix)]
                        if root in self.dict:
                            return {
                                'prefix': prefix,
                                'root': root,
                                'suffix': suffix,
                                'confidence': 0.8
                            }
        
        # Try: root + suffix (no prefix)
        for suffix in self.suffixes:
            if word.endswith(suffix):
                root = word[:-len(suffix)]
                if root in self.dict:
                    return {
                        'root': root,
                        'suffix': suffix,
                        'confidence': 0.7
                    }
        
        return None
    
    def synthesize_meaning(self, components):
        prefix = components.get('prefix')
        root = components['root']
        suffix = components.get('suffix')
        
        meaning = self.dict[root]['latin']
        
        # Apply prefix modifier
        if prefix == 'qo':
            meaning = f"valde {meaning}"  # intensifier
        elif prefix == 'ot':
            meaning = f"extendit {meaning}"  # extends
        
        # Apply suffix modifier
        if suffix == 'edy':
            meaning = f"{meaning} agit"  # action verb
        elif suffix in ['ain', 'aiin']:
            meaning = f"{meaning} erat"  # past state
        
        return meaning
```

### Integration

The morphology analyzer is already available as `scripts/morphology_analyzer.py`. Use it!

---

## 🐛 Troubleshooting

### Problem: "Folio not found"

**Solution:**
```bash
# Download it first
python download_folios.py --section q02 --folio 014v
```

### Problem: Low coverage on translation

**Solution:**
```bash
# Normal for first pass! Add more vocabulary
python analyze_gaps.py --min-freq 2
python scripts/batch_dictionary_updater.py --interactive
```

### Problem: httpx/SSL errors

**Solution:**
```bash
# Install dependencies
pip install httpx pyyaml

# On macOS, if SSL issues persist:
pip install --upgrade certifi
```

### Problem: YAML syntax error after editing

**Solution:**
```bash
# Validate dictionary
python scripts/validation_checker.py --check-type all

# Common issues:
# - Missing quotes around special characters
# - Incorrect indentation (use 2 spaces)
# - Missing hyphen before "word:"
```

### Problem: Dictionary duplicates

**Solution:**
```bash
# Check for duplicates
python scripts/validation_checker.py --check-type dictionary

# The validator will identify duplicates
```

### Problem: Coverage decreased after update

**Solution:**
```bash
# Check what changed
# Restore from backup if needed
cp voynich.yaml.backup-[timestamp] voynich.yaml

# Re-translate
python translate_folio.py --section q01 --start 1 --end 8 --force
```

---

## 📈 Progress Tracking

### Metrics to Monitor

Track these metrics to measure success:

| Metric | Start | Goal | Current |
|--------|-------|------|---------|
| Vocabulary size | ~50 | 800+ | **708** ✓ |
| Average coverage | ~10% | 65%+ | **56.6%** |
| Herbal B coverage | ~45% | 65%+ | **67.0%** ✓ |
| Herbal A coverage | ~35% | 60%+ | **52.8%** |
| Best folio | ~45% | 75%+ | **73.1%** |
| Unknown words | ~90% | <35% | **44.0%** |

### Expected Progress Path

**After Adding Top 10 Words (+175 instances):**
- Target: 60% average coverage
- Herbal A: ~56% (+3%)
- Herbal B: ~70% (+3%)

**After Adding Top 20 Words (+290 instances):**
- Target: 62-63% average coverage
- Herbal A: ~58% (+5%)
- Herbal B: ~72% (+5%)

**After Building Morphological Parser:**
- Target: 70-75% average coverage
- Automatically decompose compounds
- Handle prefix/suffix variations

---

## ✅ Success Criteria

You'll know you're making progress when:

1. ✅ **Coverage increases** after adding words
2. ✅ **Translations read more naturally** in English
3. ✅ **Unknown word count decreases** steadily
4. ✅ **High-frequency unknowns** appear in gap analysis
5. ✅ **Patterns become clearer** across folios
6. ✅ **Confidence scores improve**
7. ✅ **Coherency increases** in translations

---

## 🎓 Learning Resources

### Within This Repository

- `AI_RESEARCH_GUIDE.md` - Complete AI agent instructions
- `WORKFLOW_INSTRUCTIONS.md` - Detailed step-by-step workflow
- `VOCABULARY_EXTENSION_GUIDE.md` - Linguistic methodology
- `SYSTEM_ARCHITECTURE.md` - Technical architecture
- `RESEARCH_RESULTS.md` - Performance and analysis
- `MASTER_INDEX.md` - Navigation hub

### External Resources

- **voynich.nu** - EVA transcriptions and folio images
- **Wikipedia** - Voynich Manuscript overview
- **Yale Beinecke** - High-resolution manuscript scans

---

## 💡 Tips for Success

### 1. Visual Validation is Key
- Look at folio images
- Match words to visual elements
- Confirms translation makes sense

### 2. Use Frequency as Guide
- High frequency (>15x) = core vocabulary
- Medium frequency (5-15x) = important
- Low frequency (<5x) = wait for patterns

### 3. Leverage Known Roots
- Many unknowns are compounds
- Break down: kokaiin = kok + aiin
- Guides meaning

### 4. Cross-Reference Sections
- Compare Herbal A vs Herbal B
- Different meaning → polysemy
- Same meaning → main vocabulary

### 5. Document Your Reasoning
- Future you will thank you
- Helps identify patterns
- Easier to refine

---

## 🚀 Ready to Start?

```bash
# 1. Validate system
python scripts/validation_checker.py --check-type all

# 2. Download folios
python download_folios.py --section q02 --start 14 --end 16

# 3. Translate
python translate_folio.py --section q02 --start 14 --end 16

# 4. Analyze
python analyze_gaps.py --min-freq 5

# 5. Start adding words!
python scripts/batch_dictionary_updater.py --interactive --backup
```

---

## 📚 Quick Reference Card

```bash
# === ESSENTIAL COMMANDS ===

# Validate system
python scripts/validation_checker.py --check-type all

# Translate folio
python translate_folio.py --section q02 --folio 014r

# Analyze gaps
python analyze_gaps.py --min-freq 5

# Update dictionary
python scripts/batch_dictionary_updater.py --interactive --backup

# Re-translate after updates
python translate_folio.py --section q02 --start 14 --end 16 --force

# Check word frequency
python scripts/word_frequency.py --min-freq 10 --top 20

# Analyze morphology
python scripts/morphology_analyzer.py --word kokaiin

# Full iteration
python scripts/iteration_orchestrator.py --validation-gates
```

---

**System Status:** OPERATIONAL ✅  
**Documentation:** COMPLETE ✅  
**Ready for:** Iterative Improvement 🚀

For technical details, see `SYSTEM_ARCHITECTURE.md`.  
For research results, see `RESEARCH_RESULTS.md`.  
For AI agent use, see `AI_RESEARCH_GUIDE.md`.

