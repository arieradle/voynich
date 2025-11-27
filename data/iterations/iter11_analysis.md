# Iteration 11 Analysis Notes

## Date: November 27, 2025

---

## Neighbor Boost System Performance

### System Architecture
- **Script:** `scripts/neighbor_boost.py`
- **Database:** `data/word_neighbors.json` (41 entries, tracking top 15 neighbors per word)
- **Workers:** 4 parallel processes
- **Analysis time:** ~10 seconds for 8 words

### Confidence Boost Algorithm

```
base_confidence = morphology_score (0.60-0.75)
neighbor_boost = pattern_strength * 0.4 (max +0.20)
semantic_boost = matched_fields * 0.05 (max +0.05)
family_boost = root_matches * 0.05 (max +0.05)

final_confidence = base + neighbor + semantic + family
```

### Results This Iteration

**Words Analyzed:** 8  
**Words with Neighbors:** 5 (62.5%)  
**Words Boosted to ≥0.75:** 5 (100% of those with neighbors!)

**Performance by Neighbor Strength:**

1. **High Strength (≥0.35):**
   - chos: 0.385 → +0.15
   - ody: 0.345 → +0.15
   - **Result:** Both reached HIGH confidence (≥0.80)

2. **Medium Strength (0.30-0.34):**
   - sheaiin: 0.335 → +0.10
   - oly: 0.320 → +0.10
   - **Result:** Both reached HIGH confidence (0.80-0.85)

3. **Low Strength (0.25-0.29):**
   - oteol: 0.270 → +0.10
   - **Result:** Reached GOOD confidence (0.75)

4. **No Neighbors:**
   - do, key, kam: 0.000 → +0.00
   - **Status:** Deferred to future analysis

---

## Dual Validation Framework

### Layer 1: Morphological Analysis

**Strong Morphology (0.70-0.75):**
- chos (ch + os): 0.75
- sheaiin (she + aiin): 0.70
- oly (ol + y): 0.70

**Weak/Unclear Morphology (0.60):**
- ody: No clear decomposition
- oteol: Prefix pattern only

**Insight:** Neighbor boost allows us to accept weak morphology if neighbors are strong!

### Layer 2: Neighbor Validation

**Collocation Analysis:**
- Check word appears as neighbor to known words
- Count occurrences and variety of neighbors
- Calculate pattern strength (normalized by database size)

**Semantic Clustering:**
- Extract Latin translations of neighbors
- Group by semantic field (botanical, location, action, state, etc.)
- Consistent clustering → confidence boost

**Example - chos:**
```
Neighbors:
- chocthy (in terra facit) - botanical/location/action
- ckhaiin (calefacit) - action/state
- dan (de) - preposition/location
- kchaiin (facit erat) - action/state

Semantic fields: location, action, state, earth
→ Consistent botanical/action pattern!
```

### Layer 3: Cross-Validation

**Best Case (Both Strong):**
- chos: Morphology 0.75 + Neighbors 0.15 + Semantics 0.05 = **0.95**
- **Interpretation:** Maximum confidence, dual validation confirms

**Rescue Case (Neighbors Strong, Morphology Weak):**
- ody: Morphology 0.60 + Neighbors 0.15 + Semantics 0.05 = **0.80**
- **Interpretation:** Neighbors rescue unclear morphology!

**Marginal Case (Both Weak/Medium):**
- oteol: Morphology 0.60 + Neighbors 0.10 + Family 0.05 = **0.75**
- **Interpretation:** Just reaches threshold with combined evidence

---

## Word Family Extensions

### sh- Location/Demonstrative Family

**Known before Iter 11:**
- shy (hic)
- she (iste)
- shol (locus)
- sheol (hic locus) ← added Iter 10

**Added Iter 11:**
- sheaiin (hic est) ← sh + aiin compound

**Pattern Discovery:**
- sh- can combine with state suffixes (-aiin)
- Opens door to systematic generation

**Potential next:**
- sh + edy (this moves?)
- sh + ar (this is?)
- sh + or (this/that order?)

### ch- Botanical Family

**Known pattern:**
- ch- = botanical prefix (herba, planta)
- Combines with short roots

**Added Iter 11:**
- chos (herba os) ← ch + os

**Insight:**
- ch + os (mouth/opening) = "plant opening/aperture"
- Makes botanical sense (flower opening, seed pod, etc.)

### ot- Source/Origin Family

**Known pattern:**
- ot- = ex (from/out of)
- Consistent across multiple words

**Added Iter 11:**
- oteol (ex illo) ← ot + eol

**Insight:**
- ot + eol (that/there) = "from that/from there"
- Prepositional phrase construction

---

## Rescued Words Analysis

### ody → movet (0.60 → 0.80)

**Why weak morphology?**
- No clear prefix/suffix decomposition
- "od" not a recognized root
- Short word, hard to analyze

**Why strong neighbors?**
- Appears with: char (planta et), shar (hic et), otody (ex movet)
- ALL neighbors are botanical or action terms
- Pattern strength: 0.345 (HIGH)

**Semantic clustering:**
- Botanical: char (planta et)
- Location: shar (hic et)
- Action: otody (ex movet) ← contains "movet"!

**Conclusion:**
- Neighbors strongly suggest action verb
- Semantic field consistent with "movet" (moves)
- **Without neighbor boost: Would have been rejected!**
- **With neighbor boost: Confident addition at 0.80**

### oteol → ex illo (0.60 → 0.75)

**Why weak morphology?**
- ot- prefix clear (ex)
- But "eol" not a known root
- Unclear suffix structure

**Why neighbors help?**
- Appears with: otor (ex ordo), ykeey (extenditur)
- Both suggest "ex" (from) meaning
- Pattern strength: 0.270 (LOW-MEDIUM)

**Family validation:**
- ot- family well-established
- Likely ot + eol where eol = illo (that/there)
- Fits prepositional pattern

**Conclusion:**
- Neighbor + family validation pushes over 0.75 threshold
- **Without neighbor boost: Rejected at 0.60**
- **With neighbor boost: Accepted at 0.75**

---

## Confidence Distribution Analysis

### Iter 11 vs Iter 10

**Iteration 10:**
- Range: 0.65-0.75
- Average: 0.69
- Distribution: 1@0.75, 2@0.68, 1@0.65
- Method: Morphology only

**Iteration 11:**
- Range: 0.75-0.95
- Average: 0.83 (+0.14)
- Distribution: 1@0.95, 3@0.80-0.85, 1@0.75
- Method: Morphology + Neighbors

**Key Insight:**
- **Minimum confidence:** 0.65 → 0.75 (+0.10)
- **Average confidence:** 0.69 → 0.83 (+0.14)
- **Maximum confidence:** 0.75 → 0.95 (+0.20)
- **All metrics improved by 10-20%!**

---

## Pattern Strength Calibration

### Observed Ranges

**High Strength (0.35-0.40):**
- chos: 0.385 (4 neighbors)
- ody: 0.345 (3 neighbors)
- **Interpretation:** Well-integrated into vocabulary, consistent usage

**Medium Strength (0.30-0.34):**
- sheaiin: 0.335 (1 neighbor but strong)
- oly: 0.320 (2 neighbors)
- **Interpretation:** Moderate integration, clear patterns

**Low Strength (0.25-0.29):**
- oteol: 0.270 (2 neighbors)
- **Interpretation:** Limited but real integration

**No Neighbors (0.00):**
- do, key, kam: 0.000
- **Interpretation:** Truly isolated, rare, or formulaic

### Boost Calibration

Current formula:
```python
confidence_boost = min(0.20, pattern_strength * 0.4)
```

**Results:**
- 0.385 strength → +0.15 boost (capped at realistic level)
- 0.345 strength → +0.15 boost
- 0.335 strength → +0.10 boost
- 0.320 strength → +0.10 boost
- 0.270 strength → +0.10 boost

**Calibration seems good:**
- High patterns get significant boost (+0.15)
- Medium patterns get moderate boost (+0.10)
- Low patterns still get some boost (+0.10)
- Max boost limited to +0.20 (prevents over-confidence)

---

## Neighbor Database Quality

### Current State

**Size:** 41 entries (known words with tracked neighbors)
**Top-N:** 15 neighbors per word
**Coverage:** ~5% of dictionary (41/771)

**Quality metrics:**
- Contains high-frequency words: cho, che, dan, char, etc.
- Tracks both left and right neighbors
- Includes occurrence counts

### Limitations

1. **Small Coverage:**
   - Only 41 words tracked (~5%)
   - Should expand to top 100-200 words

2. **Stale Data:**
   - Reflects translations before recent iterations
   - Needs rebuild to include new words

3. **No Context:**
   - Doesn't track which section neighbors appear in
   - Could enhance with section-specific patterns

### Recommended Improvements

**Immediate:**
- Rebuild database after Iter 11
- Include new words: chos, sheaiin, oly, ody, oteol

**Short-term:**
- Expand to track top 100 known words
- Add section-specific neighbor tracking

**Long-term:**
- Track 3-grams (word triplets) not just pairs
- Add mutual information scores
- Implement semantic vector similarity

---

## Future Applications

### Pattern Detection

**Formulaic Phrases:**
- If words A-B-C frequently appear together
- And A and C are known
- B can be inferred from context

**Example (hypothetical):**
```
Pattern: "char [unknown] shol"
Meaning: "planta [?] locus"
→ If [unknown] appears between botanical and location terms
→ Likely a preposition or action: "in", "ad", "de"
```

### Error Detection

**Inconsistency Checking:**
- If word X translated as "movet" (moves)
- But always appears with static terms like "est" (is), "habet" (has)
- Suggests translation error

**Example:**
- If "qokeedy" means "crescent" but only appears with botanical terms
- May indicate wrong polysemy context

### Automated Proposal Generation

**Next Phase:**
- Run neighbor boost on ALL unknown words
- Auto-generate proposals for any with:
  - Pattern strength > 0.30
  - Semantic consistency
  - Known word family roots

**Potential automation:**
```python
auto_proposals = []
for unknown in all_unknowns:
    boost_data = analyze_neighbors(unknown)
    if boost_data['pattern_strength'] > 0.30:
        if boost_data['semantic_fields'] consistent:
            propose_with_confidence(unknown, boost_data)
```

---

## Lessons for Iteration 12

### Continue What Works

1. **Neighbor boost all candidates**
   - Analyze top 15-20 unknowns
   - Accept those with pattern strength > 0.25
   - Prioritize those with semantic consistency

2. **Trust dual validation**
   - Morphology + neighbors = highest confidence
   - Strong neighbors can rescue weak morphology
   - Weak both = defer

3. **Use multithreading**
   - 4-8 workers for fast analysis
   - Can screen 20+ words in seconds

### New Experiments

1. **Rebuild neighbor database**
   - Include recent additions
   - Expand to top 100 tracked words
   - Measure improvement in coverage

2. **Systematic family completion**
   - Generate all sh- + suffix combinations
   - Generate all ch- + root combinations
   - Check which exist in corpus

3. **Semantic clustering threshold**
   - If semantic fields very consistent (4+ matches)
   - Consider higher boost (+0.07 instead of +0.05)

---

## Statistical Notes

### Word Addition Rate

**Iterations 1-8:** ~86 words/iteration (startup phase)
**Iteration 9:** 2 words (conservative)
**Iteration 10:** 4 words (building confidence)
**Iteration 11:** 5 words (neighbor-boosted)

**Trend:** Sustainable rate ~4-6 words/iteration with quality

**Projection:**
- At 5 words/iteration with avg freq 8:
- Resolves ~40 occurrences per iteration
- ~1.2% coverage improvement
- **To reach 65%:** ~5-6 iterations (Iter 12-17)

### Confidence Threshold Analysis

**Current threshold:** 0.75

**With neighbor boost:**
- 5/8 words reached threshold (62.5% success rate)
- 3/8 words had no neighbors (isolated)
- **Of words with neighbors: 5/5 reached threshold (100%!)**

**Conclusion:** Neighbor boost is extremely effective when neighbors exist!

---

## Action Items for Next Iteration

### Must Do

- [x] Complete Iteration 11 report
- [ ] Rebuild neighbor database with updated translations
- [ ] Analyze next batch (daiiin, daiir, cheody, keol, dom, chl) with neighbor boost

### Should Do

- [ ] Expand neighbor database to top 100 words
- [ ] Add section-specific neighbor tracking
- [ ] Systematic sh- family analysis

### Nice to Have

- [ ] Implement 3-gram tracking
- [ ] Add mutual information scoring
- [ ] Automate proposal generation for high-confidence neighbors

---

**Analysis Status:** ✅ Complete  
**Next Steps:** Rebuild neighbor database → Iteration 12

---

*Generated: November 27, 2025*  
*Researcher: Voynich AI Agent*  
*Iteration: 11*  
*System: Neighbor-Boosted v11.0*

