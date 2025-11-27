# Voynich Translation System - Usage Guide

## 🎉 System Complete!

You now have a fully functional pipeline for:
1. Downloading Voynich manuscript folios
2. Translating them deterministically
3. Analyzing gaps and extending the dictionary

## 📦 Scripts Overview

| Script | Purpose | Example Usage |
|--------|---------|---------------|
| `download_folios.py` | Download and cache folios | `python download_folios.py --section q02 --start 1 --end 20` |
| `translator.py` | Core translation engine | Used by other scripts |
| `translate_folio.py` | Translate cached folios | `python translate_folio.py --section q02 --folio 014v` |
| `analyze_gaps.py` | Find unknown words | `python analyze_gaps.py --min-freq 2` |
| `review_and_update.py` | Update dictionary | `python review_and_update.py --add-examples` |

## 🚀 Quick Start Example

Here's a complete workflow:

```bash
# 1. Download some folios
python download_folios.py --section q02 --start 14 --end 16

# 2. Translate them
python translate_folio.py --section q02 --start 14 --end 16

# 3. Analyze what's missing
python analyze_gaps.py --min-freq 2

# 4. Review suggestions and update dictionary
python review_and_update.py --interactive

# 5. Re-translate with updated dictionary
python translate_folio.py --section q02 --folio 014v --force
```

## 📈 Demonstrated Results

**Initial Translation** (with base dictionary):
- Coverage: 7.9% (21/267 words)
- Unknown words: 246

**After Adding 21 Words**:
- Coverage: 45.7% (122/267 words)  
- Unknown words: 145
- **Improvement: 5.7x better coverage!**

## 🔄 Iterative Improvement Workflow

### Phase 1: Explore New Folios

```bash
# Download untested folios from different sections
python download_folios.py --section q02 --start 20 --end 30  # Herbal
python download_folios.py --section q04 --start 67 --end 72  # Astronomical
python download_folios.py --section q05 --start 101 --end 105  # Pharmaceutical

# Translate them all
python translate_folio.py --section q02 --start 20 --end 30
python translate_folio.py --section q04 --start 67 --end 72  
python translate_folio.py --section q05 --start 101 --end 105
```

### Phase 2: Analyze Patterns

```bash
# Find high-frequency unknown words
python analyze_gaps.py --min-freq 3 --max-suggestions 50

# This creates: data/dictionary_suggestions.json
```

### Phase 3: Review with AI (You!)

1. Look at `data/dictionary_suggestions.json`
2. Review top suggestions (sorted by priority)
3. For each high-priority word:
   - Check which sections it appears in
   - Look for structural patterns (prefixes, suffixes)
   - Compare with known roots
   - Make educated guesses based on context

### Phase 4: Update Dictionary

**Option A: Interactive Mode**
```bash
python review_and_update.py --interactive

# Then use commands:
# - show 20          # Show top 20 suggestions
# - add              # Add a new word manually
# - save             # Save changes
```

**Option B: Programmatic**
Edit `review_and_update.py` to add your analyzed words, then:
```bash
python review_and_update.py --add-examples
```

### Phase 5: Validate

```bash
# Re-translate folios with updated dictionary
python translate_folio.py --section q02 --folio 020r --force

# Check coverage improvement
python analyze_gaps.py --min-freq 3
```

## 🎯 Strategy Tips

### 1. Start with High-Frequency Words
- Words appearing 5+ times are most impactful
- Use `--min-freq 5` in analyze_gaps.py

### 2. Focus on Structural Patterns
- **qo- prefix**: Usually intensifier ("very") or specific verb
- **-edy suffix**: Often indicates verbs
- **-aiin suffix**: May indicate nouns or past tense
- **ch- prefix**: Common in herbal terms

### 3. Cross-Reference Sections
- Same word in different sections → polysemous
- Example: `qokedy` = "grows" (herbal) / "shines" (astronomical)

### 4. Use Visual Context
- Download folio images from voynich.nu
- Match unknown words with visible elements
- Near plants? Probably botanical term
- Near stars? Probably astronomical term

### 5. Build on Roots
- If "kedy" = "facit" (makes)
- Then "qokedy" likely = "valde facit" (makes greatly)
- Add as polysemy with contextual meanings

## 📊 Tracking Progress

Monitor your dictionary growth:

```bash
# Count vocabulary entries
grep -c "word:" voynich.yaml

# Check average coverage across translations
ls data/translations/*.json | wc -l

# See improvement over time
git log --oneline voynich.yaml
```

## 🔍 AI-Assisted Analysis (For You)

As the AI assistant, here's how I can help in each iteration:

1. **Pattern Recognition**: "Show me all words with 'qo-' prefix"
2. **Context Analysis**: "What section are these words most common in?"
3. **Etymological Guesses**: "Based on Latin roots, what could this mean?"
4. **Visual Research**: "Can you look at folio 14v image and tell me what's near this word?"
5. **Validation**: "Does this translation make sense given the context?"

## 📝 Dictionary Entry Format

### Simple Word
```yaml
- word: newword
  description: "appears near X in Y context"
  latin: novum
```

### Polysemous Word
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

## 🎓 Learning from Existing Patterns

Study successful entries in `voynich.yaml`:

1. **daiin** (~250x) → "ad" (to)
   - High frequency → function word
   
2. **qokedy** (varies) → multiple meanings
   - Polysemous based on section
   
3. **shy** (~60x) → "hic" (here)
   - Location marker

Apply these patterns to new unknowns!

## ⚡ Power User Commands

```bash
# Download all herbal folios
for i in {1..58}; do
  python download_folios.py --section q01 --start $i --end $i
done

# Batch translate everything cached
python translate_folio.py --section q01 --start 1 --end 58

# Get comprehensive gap analysis
python analyze_gaps.py --min-freq 1 --max-suggestions 100 > gaps_report.txt

# Compare before/after coverage
python translate_folio.py --section q02 --show 014v | grep Coverage
```

## 🐛 Troubleshooting

**Problem**: "Folio not found"
```bash
# Download it first
python download_folios.py --section q02 --folio 014v
```

**Problem**: Low coverage on translation
```bash
# Normal for first pass! Add more vocabulary
python analyze_gaps.py --min-freq 2
python review_and_update.py --interactive
```

**Problem**: httpx/SSL errors
```bash
# Make sure dependencies are installed
pip install httpx pyyaml
```

## 🎯 Goals & Metrics

Track these metrics to measure success:

- **Vocabulary size**: Start ~50 words → Goal: 300+ words
- **Average coverage**: Start ~10% → Goal: 60%+  
- **Unknown word reduction**: Start 90% unknown → Goal: <40%
- **Folios translated**: Start 1 → Goal: 50+

## 📚 Next Steps

1. **Week 1**: Focus on herbal section (q01, q02)
   - Well-illustrated, easier to validate
   - Build core vocabulary

2. **Week 2**: Expand to astronomical (q04)
   - Test polysemy
   - Add star-related terms

3. **Week 3**: Pharmaceutical & biological (q03, q05)
   - More specialized vocabulary
   - Complex compounds

4. **Week 4**: Validate and refine
   - Re-translate early folios
   - Check consistency
   - Document patterns

## 🤝 Collaboration

This system is designed for human-AI collaboration:

- **Scripts**: Automate repetitive tasks
- **Human**: Pattern recognition, visual analysis, validation
- **AI**: Suggestions, research, cross-referencing

Together, we can systematically decode the Voynich manuscript!

---

**Ready to start?** Run:
```bash
python download_folios.py --section q02 --start 1 --end 10
python translate_folio.py --section q02 --start 1 --end 10
python analyze_gaps.py
```

Then share the results with me for collaborative analysis! 🚀

