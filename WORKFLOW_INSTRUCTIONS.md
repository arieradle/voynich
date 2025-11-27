# Workflow Instructions
# Step-by-Step Research Iteration Guide

This document provides detailed, actionable instructions for conducting a complete research iteration on the Voynich manuscript translation system.

---

## 📋 Pre-Iteration Checklist

Before starting any iteration, ensure:

- [ ] Dictionary is valid (no syntax errors)
- [ ] All translations are up to date
- [ ] Backup of `voynich.yaml` exists
- [ ] You understand current coverage baseline
- [ ] You have reviewed previous iteration results (if any)

**Validation Command:**
```bash
python scripts/validation_checker.py --check-type all
```

Expected output: "✅ VALIDATION PASSED"

---

## 🔄 Complete Iteration Workflow

### Phase 1: ANALYZE

**Objective:** Understand current state and identify improvement opportunities

#### Step 1.1: Validate System State (5 minutes)

```bash
# Check dictionary integrity
python scripts/validation_checker.py --check-type all

# Expected: No errors, all checks pass
# If fails: Fix errors before proceeding
```

**What to check:**
- YAML syntax valid
- No duplicate entries
- All required fields present
- Polysemy entries well-formed

**If validation fails:**
1. Review error messages
2. Fix issues manually or restore from backup
3. Re-run validation
4. Do not proceed until validation passes

#### Step 1.2: Calculate Current Coverage (5 minutes)

```bash
# Re-translate to get fresh metrics (if needed)
python translate_folio.py --section q01 --start 1 --end 8
python translate_folio.py --section q02 --start 14 --end 16

# View specific folio
python translate_folio.py --section q02 --show 014r
```

**Record baseline metrics:**
- Overall coverage: ____%
- Herbal A coverage: ____%
- Herbal B coverage: ____%
- Total unique unknowns: _____

**Where to find:**
- Individual folio coverage in JSON files: `data/translations/*.json`
- Look for `"statistics": {"coverage": 0.XX}`

#### Step 1.3: Identify Unknown Words (10 minutes)

```bash
# Analyze unknown word frequency
python scripts/word_frequency.py --min-freq 5 --format json --output data/unknown_ranked.json

# Generate Markdown report for easier reading
python scripts/word_frequency.py --min-freq 5 --format md --output data/frequency_report.md
```

**Review the output:**
- Open `data/frequency_report.md`
- Note the top 20 unknown words
- Pay attention to:
  - Words with frequency ≥ 15 (HIGH PRIORITY)
  - Words appearing in multiple sections
  - Short words (3-4 letters, likely function words)

**Document your observations:**
```
Top priorities this iteration:
1. [word] - [frequency]x - [observations]
2. [word] - [frequency]x - [observations]
3. ...
```

#### Step 1.4: Detect Patterns (10 minutes)

```bash
# Run pattern detection
python scripts/pattern_detector.py --pattern-type all --min-occurrences 3 --output data/patterns_detected.json

# For specific analysis
python scripts/pattern_detector.py --pattern-type formulaic --min-occurrences 5
```

**Look for:**
- Repeated 3+ word sequences (formulaic phrases)
- Common word pairs (grammatical constructions)
- Section-specific patterns

**Document discoveries:**
```
Pattern insights:
- [pattern] appears [N]x - may indicate [meaning/grammar]
- [word pair] suggests [relationship]
```

#### Step 1.5: Run Gap Analysis (5 minutes)

```bash
# Comprehensive gap analysis
python analyze_gaps.py --min-freq 5 --max-suggestions 50

# Output: data/dictionary_suggestions.json
```

**Review suggestions:**
- Open `data/dictionary_suggestions.json`
- Check proposed reasoning for top candidates
- Note which have morphological support

### 🚦 Validation Gate 1: Analysis Review

**STOP and review:**
1. Unknown word frequency report
2. Pattern detection results
3. Gap analysis suggestions

**Ask yourself:**
- Do I see clear patterns?
- Are there obvious high-priority candidates?
- Do I understand why these words are unknown?

**Decision:**
- [ ] Proceed to proposal phase
- [ ] Re-analyze with different parameters
- [ ] Abort iteration (explain why)

---

### Phase 2: PROPOSE

**Objective:** Generate well-reasoned vocabulary entry proposals

#### Step 2.1: Morphological Analysis (15 minutes)

For each high-priority word, analyze morphology:

```bash
# Single word analysis
python scripts/morphology_analyzer.py --word kokaiin

# Batch analysis (if you have a list)
python scripts/morphology_analyzer.py --batch-file data/priority_words.txt --output data/morphology_analysis.json
```

**For each word, document:**
```
Word: [word]
Frequency: [N]
Morphological breakdown: [prefix]+[root]+[suffix]
Confidence: [0.0-1.0]
Reasoning: [explanation]
Proposed Latin: [translation]
```

**Red flags to watch for:**
- Confidence < 0.6
- No clear decomposition
- Multiple contradictory decompositions
- Word appears to be transcription error

#### Step 2.2: Compound Decomposition (15 minutes)

For longer words or unclear morphology:

```bash
# Try all strategies
python scripts/compound_decomposer.py --word qotchedy --strategy all

# Heuristic strategy (usually best)
python scripts/compound_decomposer.py --word qotchedy --strategy heuristic
```

**Compare results:**
- Do different strategies agree?
- Is there a clear high-confidence decomposition?
- Does it fit the context?

#### Step 2.3: Generate Word Families (Optional, 10 minutes)

If you've identified a productive root:

```bash
# Generate systematic variations
python scripts/morphology_analyzer.py --generate-family chol

# Output: Systematic prefix/suffix combinations
```

**Use case:**
- When you have a solid root (confidence ≥ 0.8)
- To batch-generate related words
- To identify which variations actually appear in text

#### Step 2.4: Rank and Select Candidates (15 minutes)

**Selection criteria:**

**Tier 1 (Definitely add):**
- Frequency ≥ 15
- Confidence ≥ 0.8
- Clear morphological pattern
- Fits context

**Tier 2 (Probably add):**
- Frequency ≥ 10
- Confidence ≥ 0.7
- Reasonable morphology
- Context supports

**Tier 3 (Maybe add):**
- Frequency ≥ 5
- Confidence ≥ 0.6
- Weak but plausible morphology
- Needs visual confirmation

**Do not add:**
- Frequency < 5
- Confidence < 0.6
- No morphological support
- Contradicts patterns

**Create proposal file:**

Create `data/vocabulary_proposals.json`:
```json
{
  "iteration": 1,
  "date": "2025-11-27",
  "proposals": [
    {
      "word": "kokaiin",
      "latin": "maturat",
      "description": "appears near fruits/seeds; kok + aiin compound",
      "frequency": 20,
      "confidence": 0.75,
      "reasoning": "Compound of kok (related to kedy=makes) + aiin (state marker). Context: fruit ripening in botanical folios.",
      "tier": 1
    }
  ]
}
```

### 🚦 Validation Gate 2: Vocabulary Proposal

**STOP and review proposals:**

**Present to human:**
```
VOCABULARY PROPOSALS FOR ITERATION [N]

Tier 1 (High confidence): [N] words
Tier 2 (Medium confidence): [N] words
Tier 3 (Low confidence): [N] words

Top 5 proposals:
1. [word] ([freq]x) → [latin]
   Reasoning: [brief explanation]
   Confidence: [score]

2. ...

Estimated coverage improvement: +[X]%

Approve all Tier 1? 
Review Tier 2/3 individually?
```

**Options:**
- Approve all
- Approve subset
- Modify proposals
- Reject and rework

**Action:** Create approved list in `data/approved_words.json`

---

### Phase 3: VALIDATE

**Objective:** Verify proposals before implementation

#### Step 3.1: Consistency Check (5 minutes)

```bash
# Check proposals don't contradict dictionary
python scripts/validation_checker.py --check-type consistency
```

**Manual checks:**
- Do any proposals duplicate existing entries?
- Are translations consistent with morphological patterns?
- Do polysemous candidates appear in multiple contexts?

#### Step 3.2: Visual Context Check (Optional, 15 minutes)

For botanical terms, cross-reference with folio images:

1. Open folio image: https://voynich.nu/q01/f001r.jpg (replace with relevant folio)
2. Locate the word in transcription
3. Check if proposed translation matches illustrated plant features

**Example:**
- Proposed: "fchey" → "petala" (petals)
- Check: Do illustrations near "fchey" show petal-like structures?
- Result: ✓ Confirms / ✗ Contradicts / ? Unclear

#### Step 3.3: Polysemy Detection (5 minutes)

For words appearing in multiple sections:

```bash
# Check where word appears
grep -r "word" data/folios/
```

**If appears in 2+ different sections:**
- Check if meaning seems consistent
- If not, mark for polysemous entry
- Document context-specific meanings

### 🚦 Validation Gate 3: Dictionary Update Approval

**STOP - This is critical:**

**Final review before modifying dictionary:**
```
READY TO UPDATE DICTIONARY

Words to add: [N]
- [list of words]

Polysemy entries to add: [N]
- [list if any]

Estimated coverage improvement: +[X]%

Backup will be created: voynich.yaml.backup-[timestamp]

⚠️  This will modify the dictionary file.

APPROVE? (yes/no)
```

**If no:** Revise proposals and re-validate

**If yes:** Proceed to implementation

---

### Phase 4: IMPLEMENT

**Objective:** Update dictionary with approved words

#### Step 4.1: Create Backup (CRITICAL)

```bash
# Manual backup
cp voynich.yaml voynich.yaml.backup-$(date +%Y%m%d-%H%M%S)

# Verify backup created
ls -lh voynich.yaml.backup-*
```

**NEVER skip this step!**

#### Step 4.2: Update Dictionary (15 minutes)

**Interactive mode (recommended for small batches):**
```bash
python scripts/batch_dictionary_updater.py --interactive --backup

# Follow prompts:
# Format: word|latin|description
# Example: kokaiin|maturat|appears near fruits/seeds; kok + aiin compound
```

**Batch mode (for larger updates):**
```bash
python scripts/batch_dictionary_updater.py --import-file data/approved_words.json --backup
```

**Important:**
- Review each addition carefully
- Check for typos
- Verify format before saving
- Confirm when prompted

#### Step 4.3: Validate Updated Dictionary (5 minutes)

```bash
# Immediately validate after update
python scripts/validation_checker.py --check-type all

# MUST pass all checks
# If fails: Restore from backup and fix issues
```

**If validation fails:**
```bash
# Restore backup
cp voynich.yaml.backup-[latest] voynich.yaml

# Fix issues
# Try again
```

#### Step 4.4: Add Polysemy Entries (If needed, 10 minutes)

If polysemous words were identified:

1. Open `voynich.yaml` in editor
2. Locate `polysemy:` section
3. Add entry following this format:

```yaml
- word: example
  meanings:
    - latin: translation1
      context: herbal section, near plants
    - latin: translation2
      context: astronomical section, near stars
  base: most_common_translation
```

4. Save and validate again

### 🚦 Validation Gate 4: Implementation Verification

**Verify implementation:**

```
DICTIONARY UPDATED

Words added: [N]
Dictionary size: [old] → [new]
Validation: PASSED ✓
Backup: [filename]

Changes look correct?
Proceed to testing phase?
```

**Decision:**
- [ ] Proceed to testing
- [ ] Review changes manually
- [ ] Rollback and revise

---

### Phase 5: TEST

**Objective:** Re-translate and measure improvement

#### Step 5.1: Clear Translation Cache (1 minute)

```bash
# Clear any cached data
rm -f data/.unknown_cache.json
```

#### Step 5.2: Re-translate All Folios (10 minutes)

```bash
# Re-translate with updated dictionary
python translate_folio.py --section q01 --start 1 --end 8 --force
python translate_folio.py --section q02 --start 14 --end 16 --force

# --force flag ensures re-translation even if files exist
```

**Monitor output:**
- Check for errors
- Note coverage changes
- Watch for warnings

#### Step 5.3: Calculate New Coverage (5 minutes)

```bash
# Run gap analysis to see new metrics
python analyze_gaps.py --min-freq 5 --max-suggestions 20
```

**Record new metrics:**
- Overall coverage: ____%  (was: ___%)
- Herbal A coverage: ____%  (was: ___%)
- Herbal B coverage: ____%  (was: ___%)
- Total unique unknowns: _____  (was: _____)

**Calculate improvements:**
- Overall: +____%
- Herbal A: +____%
- Herbal B: +____%
- Unknowns reduced by: _____

#### Step 5.4: Quality Check (5 minutes)

**Review sample translations:**
```bash
# Check a few specific folios
python translate_folio.py --section q01 --show 001r
python translate_folio.py --section q02 --show 014r
```

**Look for:**
- Do new translations make sense?
- Is Latin grammatically reasonable?
- Does English read better?
- Any obvious errors?

### 🚦 Validation Gate 5: Translation Review

**Review results:**

```
RE-TRANSLATION COMPLETE

Coverage Improvement:
- Overall: [old]% → [new]% (+[delta]%)
- Herbal A: [old]% → [new]% (+[delta]%)
- Herbal B: [old]% → [new]% (+[delta]%)

Unknown Words: [old] → [new] ([delta])

Words resolved this iteration: [N]

Success criteria:
- Improvement ≥ 3%: [✓/✗]
- No coverage regression: [✓/✗]
- Dictionary valid: [✓/✗]

Proceed to reporting?
```

**If improvement < 3%:**
- Analyze why
- Consider different approach next iteration
- May need morphological parser enhancement

**If coverage decreased:**
- ⚠️  CRITICAL - Review additions
- Some translations may be incorrect
- Consider rollback

**Decision:**
- [ ] Proceed to report
- [ ] Review specific folios
- [ ] Rollback iteration

---

### Phase 6: REPORT

**Objective:** Document iteration and plan next steps

#### Step 6.1: Generate Iteration Report (10 minutes)

Create `reports/iteration_[N]_report.md`:

```markdown
# Iteration [N] Report
**Date:** [YYYY-MM-DD]
**Researcher:** [Your name or agent ID]

## Summary
- Words added: [N]
- Coverage improvement: +[X]%
- Dictionary size: [old] → [new]

## Words Added
| Word | Latin | Frequency | Confidence | Reasoning |
|------|-------|-----------|------------|-----------|
| word1 | latin1 | 20 | 0.80 | explanation |
| ... |

## Coverage Results
| Section | Before | After | Improvement |
|---------|--------|-------|-------------|
| Overall | XX% | YY% | +Z% |
| Herbal A | XX% | YY% | +Z% |
| Herbal B | XX% | YY% | +Z% |

## Unknown Words Remaining
- Total: [N]
- High priority (freq ≥ 10): [N]
- Top 10 priorities for next iteration: [list]

## Insights Discovered
- [Pattern or insight discovered]
- [Morphological finding]
- [Context observation]

## Next Iteration Recommendations
1. [Recommendation]
2. [Recommendation]
3. [Recommendation]

## Challenges Encountered
- [Challenge and how resolved]

## Notes
[Any additional observations]
```

#### Step 6.2: Update Metrics Tracking (5 minutes)

Update `data/metrics_history.json`:

```json
{
  "iterations": [
    {
      "number": 1,
      "date": "2025-11-27",
      "words_added": 10,
      "coverage_before": 0.556,
      "coverage_after": 0.591,
      "improvement": 0.035,
      "dictionary_size": 718,
      "unknown_count": 1025
    }
  ]
}
```

#### Step 6.3: Evaluate Stopping Criteria (5 minutes)

**Should we stop?**

Check against stopping criteria:

- [ ] Target coverage reached (≥ 65%)
- [ ] No high-priority unknowns remaining
- [ ] Improvement < 2% for 3 consecutive iterations
- [ ] Max iterations reached
- [ ] Human requests pause

**Should we continue?**

- [ ] Significant improvement made (≥ 3%)
- [ ] High-priority unknowns remain
- [ ] New patterns discovered
- [ ] Target not yet reached

#### Step 6.4: Prepare Next Iteration (Optional, 5 minutes)

If continuing:

```bash
# Quick preview of next priorities
python scripts/word_frequency.py --min-freq 10 --top 20

# Preliminary morphological scan
python scripts/morphology_analyzer.py --batch-file data/top_priorities.txt
```

**Set parameters for next iteration:**
- Target coverage: ____%
- Word addition goal: _____
- Focus area: [Herbal A / Herbal B / Patterns / Morphology]

### 🚦 Validation Gate 6: Iteration Completion

**Final review:**

```
ITERATION [N] COMPLETE

Summary:
- Words added: [N]
- Coverage improvement: +[X]%
- Current overall coverage: [Y]%
- High-priority unknowns remaining: [Z]
- Time taken: [HH:MM]

Success: [✓/✗]

Recommended next step: [recommendation]

What would you like to do?
1. Start next iteration
2. Review results in detail
3. Pause research
4. Change strategy
```

**Decision:**
- [ ] Start iteration [N+1]
- [ ] Pause for review
- [ ] Modify approach
- [ ] End session

---

## 🔄 Quick Reference: Complete Workflow

**30-Minute Quick Iteration (Experienced users):**

```bash
# 1. Validate (2 min)
python scripts/validation_checker.py --check-type all

# 2. Analyze (5 min)
python scripts/word_frequency.py --min-freq 10 --top 10
python scripts/morphology_analyzer.py --word [top_word]

# 3. Propose (5 min)
# Document 3-5 high-confidence words

# 4. Implement (5 min)
python scripts/batch_dictionary_updater.py --interactive --backup

# 5. Test (10 min)
python translate_folio.py --section q01 --start 1 --end 8 --force
python translate_folio.py --section q02 --start 14 --end 16 --force

# 6. Report (3 min)
# Note coverage improvement and next priorities
```

---

## 🆘 Troubleshooting

### Validation Fails
**Problem:** Dictionary validation errors

**Solution:**
1. Read error messages carefully
2. Check for syntax errors, duplicates
3. Restore from backup if corrupted
4. Fix issues manually
5. Re-validate

### Coverage Decreased
**Problem:** Coverage went down after additions

**Solution:**
1. Check if new words conflict with existing translations
2. Review validation checker output
3. Consider rolling back
4. Investigate which folios lost coverage
5. May need to remove problematic additions

### No Improvement
**Problem:** Coverage improvement < 2%

**Solution:**
1. Added words may be low-frequency
2. Focus on higher-frequency unknowns
3. Try morphological decomposition approach
4. Look for systematic word families
5. Review patterns more carefully

### Script Errors
**Problem:** Helper script crashes or errors

**Solution:**
1. Check if all dependencies installed
2. Verify file paths are correct
3. Check input file formats
4. Read error traceback
5. Try with simpler parameters first

---

## ✅ Success Checklist

After each iteration, verify:

- [ ] Dictionary validated successfully
- [ ] Backup created before changes
- [ ] All additions have descriptions
- [ ] No duplicates introduced
- [ ] Coverage improved (or documented why not)
- [ ] Iteration report generated
- [ ] Metrics tracked
- [ ] Next steps identified
- [ ] Ready for next iteration or pause

---

**Remember:** Slow and steady wins the race. One good iteration beats three rushed ones. When in doubt, validate!

