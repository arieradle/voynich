# Validation Tools Integration Guide

**Date:** November 30, 2025  
**Status:** ✅ Integrated into Workflow

---

## Overview

Validation tools are now fully integrated into the Voynich translation workflow to automatically assess translation quality using information theory and statistical validation.

---

## Integrated Tools

### 1. **Entropy Analyzer** (`scripts/entropy_analyzer.py`)

**Purpose:** Calculate information theory metrics for all translations

**Metrics Calculated:**
- Character entropy (bits/char)
- Word entropy (bits/word)
- Conditional entropy (predictability)
- Compression ratio (redundancy)
- Lexical diversity (type-token ratio)
- Word length distribution

**Usage:**
```bash
python scripts/entropy_analyzer.py
```

**Output:** `data/entropy_analysis.json`

---

### 2. **Null Hypothesis Tester** (`scripts/null_hypothesis_tester.py`)

**Purpose:** Compare real translations against random baseline

**Tests:**
- Coherence (word-to-word transitions)
- Grammar patterns (Latin-like structures)
- Repetition control (vocabulary diversity)

**Usage:**
```bash
python scripts/null_hypothesis_tester.py
```

**Output:** `data/null_hypothesis_test.json`

---

### 3. **Embedded Validation Metrics** (in translation files)

**Purpose:** Real-time quality assessment during translation

**Automatically Included in Every Translation File:**
```json
{
  "folio_id": "014r",
  "section": "Herbal B",
  "voynich_text": "...",
  "latin_text": "...",
  "english_text": "...",
  "word_translations": [...],
  "statistics": {...},
  "validation_metrics": {
    "voynich": {
      "char_entropy": 3.742,
      "word_entropy": 5.871,
      "compression_ratio": 0.233,
      "lexical_diversity": {...}
    },
    "latin": {
      "char_entropy": 3.718,
      "word_entropy": 5.341,
      "compression_ratio": 0.260,
      "lexical_diversity": {...}
    },
    "english": {
      "char_entropy": 3.683,
      "word_entropy": 4.922,
      "compression_ratio": 0.281,
      "lexical_diversity": {...}
    },
    "quality_flags": {
      "low_word_entropy": false,
      "high_compression": false,
      "low_diversity": true
    },
    "expected_values": {
      "latin_char_entropy": "~3.8 bits/char",
      "latin_word_entropy": "~9.5 bits/word",
      "english_char_entropy": "~4.1 bits/char",
      "english_word_entropy": "~10.0 bits/word"
    }
  }
}
```

---

## Workflow Integration

### Phase 5 (TEST) - Automatic Validation

After re-translating folios, the workflow now automatically:

**Step 5.6:** Run entropy analysis
```bash
python scripts/entropy_analyzer.py
```

**Step 5.7:** Run null hypothesis test
```bash
python scripts/null_hypothesis_tester.py
```

**Validation Gate:** Reviews quality metrics before proceeding

---

## Quality Flags & Warnings

### Automatic Warnings in Translation Output

When translating, you'll see warnings if quality issues detected:

```
🔬 Validation Metrics:
   • Latin word entropy: 5.341 bits/word (expected: ~9.5)
   • English word entropy: 4.922 bits/word (expected: ~10.0)
   • Lexical diversity (TTR): 0.239
   ⚠️  WARNING: Low word entropy (excessive repetition)
   ⚠️  WARNING: Low lexical diversity (limited vocabulary)
```

### Quality Flag Thresholds

| Flag | Condition | Meaning |
|------|-----------|---------|
| `low_word_entropy` | < 5.0 bits/word | Excessive repetition |
| `high_compression` | < 0.25 ratio | Too predictable/formulaic |
| `low_diversity` | TTR < 0.3 | Limited vocabulary use |

---

## Interpretation Guidelines

### Entropy Metrics

**Character Entropy:**
- ✅ **Normal:** 3.5-4.2 bits/char
- ⚠️ **Low:** < 3.5 (too repetitive)
- ⚠️ **High:** > 4.5 (too random)

**Word Entropy:**
- ✅ **Natural Language:** 9-11 bits/word
- ⚠️ **Moderate:** 6-9 bits/word (some repetition)
- ❌ **Low:** < 6 bits/word (excessive repetition)

**Compression Ratio:**
- ✅ **Natural Language:** 0.35-0.45
- ⚠️ **High Compression:** 0.25-0.35 (repetitive)
- ❌ **Very High Compression:** < 0.25 (formulaic)

### Null Hypothesis Results

**Coherence:**
- ✅ **Significant:** > 80% better than random
- ⚠️ **Moderate:** 60-80% better
- ❌ **Not Significant:** < 60% better

**Grammar Patterns:**
- ✅ **Strong:** > 70% better than random
- ⚠️ **Weak:** 50-70% better
- ❌ **Random:** < 50% better

**Repetition Control:**
- ✅ **Good:** > 0 (better than random)
- ⚠️ **Neutral:** -0.2 to 0
- ❌ **Poor:** < -0.2 (worse than random)

---

## Fallback Strategies

### If Poor Entropy Metrics Detected

**Triggered When:**
- Word entropy < 5.0
- Compression ratio < 0.25
- Low lexical diversity (TTR < 0.3)

**Actions:**
1. Check if translations are too repetitive
2. Investigate label vs. prose distinction
3. Review if translating structural markers vs. semantic content
4. Consider visual correlation testing
5. Re-evaluate linguistic assumptions

**Warning:** Low word entropy suggests non-linguistic patterns

### If Worse Than Random

**Triggered When:**
- Coherence < 50% better than random
- Grammar patterns < 50% better
- Repetition control < -0.3

**Actions:**
1. **HALT further iterations**
2. Review validation report
3. Consider if base hypothesis is incorrect
4. Test visual correlation with images
5. Distinguish labels from continuous text

**Alert:** CRITICAL - Translations performing worse than random baseline

---

## Success Criteria Updates

### Quality Gates (Updated)

```yaml
quality_gates:
  - no_duplicate_entries: true
  - all_words_have_descriptions: true
  - latin_translations_valid: true
  - polysemy_properly_formatted: true
  - entropy_within_acceptable_range: true  # NEW
  - better_than_random_baseline: true      # NEW
  - repetition_control_positive: true      # NEW
```

### Overall Success Criteria (Updated)

```yaml
overall_success:
  - coverage_overall: ">= 0.65"
  - word_entropy: ">= 7.0"              # NEW: Minimum word entropy
  - coherence_vs_random: ">= 0.80"     # NEW: 80% better than random
```

---

## Example Usage

### During Iteration

```bash
# Step 1: Translate with embedded validation
python translate_folio.py --section q02 --start 14 --end 16 --force

# Step 2: Run full validation suite
python scripts/entropy_analyzer.py
python scripts/null_hypothesis_tester.py

# Step 3: Review reports
cat data/entropy_analysis.json
cat data/null_hypothesis_test.json
cat docs/TRANSLATION_VALIDATION_REPORT.md
```

### Checking Quality Flags

```python
import json

# Load translation
with open('data/translations/q02_f014r_translation.json') as f:
    trans = json.load(f)

# Check quality
vm = trans['validation_metrics']
flags = vm['quality_flags']

if any(flags.values()):
    print("⚠️ Quality issues detected:")
    for flag, triggered in flags.items():
        if triggered:
            print(f"  • {flag}")
```

---

## Files Generated

### Per-Translation Files
- Each translation JSON now includes `validation_metrics` section

### Global Analysis Files
- `data/entropy_analysis.json` - Entropy metrics for all translations
- `data/null_hypothesis_test.json` - Statistical validation results
- `docs/TRANSLATION_VALIDATION_REPORT.md` - Comprehensive analysis

### Workflow Integration
- `research_workflow.yaml` - Updated with validation steps (Phase 5.6, 5.7)

---

## Benefits

✅ **Real-time Quality Feedback:** Immediate warnings during translation  
✅ **Objective Metrics:** Quantitative assessment, not subjective  
✅ **Early Detection:** Catch quality issues before they compound  
✅ **Statistical Rigor:** Compare against random baseline  
✅ **Historical Tracking:** All metrics stored in JSON for analysis  
✅ **Workflow Integration:** Automatic execution during iterations  

---

## Next Steps

1. **Monitor quality flags** during future iterations
2. **Investigate any warnings** before adding more words
3. **Run full validation** after major dictionary updates
4. **Review validation report** if metrics degrade
5. **Consider visual correlation testing** if quality issues persist

---

**Status:** ✅ All validation tools integrated and operational  
**Last Updated:** November 30, 2025  
**Integration Version:** 2.0

