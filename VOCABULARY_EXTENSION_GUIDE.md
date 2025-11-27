# Vocabulary Extension Guide
# Linguistic Methodology for Voynich Translation

This guide explains the systematic approach to extending the Voynich vocabulary through morphological analysis, pattern recognition, and context validation.

---

## 🎯 Core Philosophy

### The Morphological Hypothesis

The Voynich system appears to use **systematic morphology**:
- **Prefixes** modify or intensify meaning
- **Roots** carry core meaning
- **Suffixes** indicate grammar or state

**Example:**
- `qokedy` = `qo` (intensifier) + `kedy` (makes) → "valde facit" (makes strongly/grows)
- `daiin` = `da` (gives) + `aiin` (is/state) → "ad" (to/toward)
- `chol` = `ch` (botanical) + `ol` (place) → "caulis" (stem/stalk)

This systematic nature allows us to:
1. Decompose unknown compounds
2. Generate word families
3. Predict meanings with confidence

---

## 📚 Morphological Components

### Prefix Catalog

#### High-Confidence Prefixes (Use liberally)

**`qo-`** (Intensifier/Emphasis)
- **Meaning:** valde (very, greatly)
- **Confidence:** 0.9
- **Usage:** Verb intensification
- **Examples:**
  - `qokedy` → valde crescit (grows strongly)
  - `qokaiin` → valde terra (very much earth)
  - `qokchor` → valde ramulus (very branching)
- **Pattern:** Most reliable prefix; appears frequently

**`ot-`** (Source/Origin)
- **Meaning:** ex (from, out of)
- **Confidence:** 0.8
- **Usage:** Indicates source or origin
- **Examples:**
  - `otaiin` → ex erat (from was/existed)
  - `otchy` → ex in (from within)
  - `otchol` → ex caule (from the stem)
- **Pattern:** Often followed by location or state markers

**`sh-`** (Location/Demonstrative)
- **Meaning:** hic (here, this)
- **Confidence:** 0.8
- **Usage:** Spatial reference
- **Examples:**
  - `shy` → hic (here)
  - `shol` → hic locus (here place)
  - `shody` → hic movet (here moves)
- **Pattern:** Common in descriptive passages

**`ch-`** (Botanical/Herbal)
- **Meaning:** herba/planta (plant-related)
- **Confidence:** 0.7 (herbal sections)
- **Usage:** Plant-related terms
- **Examples:**
  - `chol` → caulis (stem)
  - `chor` → ramus (branch)
  - `chy` → in plantam (in/to plant)
- **Pattern:** Primarily in herbal folios

#### Medium-Confidence Prefixes (Use with care)

**`dy-`** (Conjunction)
- **Meaning:** et (and)
- **Confidence:** 0.6
- **Usage:** Connects concepts
- **Examples:**
  - `dychy` → et in (and in)
  - `dyar` → et et (and also)
- **Note:** Sometimes hard to distinguish from root starting with 'dy'

**`y-`** (Direction)
- **Meaning:** ad (to, toward)
- **Confidence:** 0.6
- **Usage:** Directional
- **Examples:**
  - `ydain` → ad versus (toward)
  - `ykal` → altus (tall/toward height)
- **Note:** Can be ambiguous; check context

**`d-`** (Giving/Action)
- **Meaning:** dat (gives)
- **Confidence:** 0.5
- **Usage:** Action marker
- **Examples:**
  - `daiin` → ad (to/direction)
  - `dol` → de (from/of)
- **Note:** Very short; often unclear

### Suffix Catalog

#### High-Confidence Suffixes (Use liberally)

**`-aiin`** (State of Being)
- **Meaning:** est/erat (is/was)
- **Confidence:** 0.9
- **Usage:** State marker, present/past
- **Examples:**
  - `daiin` → ad (direction + state = to)
  - `okaiin` → ponit (places/puts)
  - `kokaiin` → maturat (ripens)
- **Pattern:** Very reliable; marks states and existence

**`-edy`** (Action/Movement)
- **Meaning:** movet (moves, acts)
- **Confidence:** 0.8
- **Usage:** Action verbs
- **Examples:**
  - `qokedy` → crescit (grows)
  - `okedy` → extendit (extends)
  - `chody` → movetur (moves)
- **Pattern:** Common in action descriptions

**`-ain`** (Past State)
- **Meaning:** erat (was)
- **Confidence:** 0.7
- **Usage:** Past tense/state
- **Examples:**
  - `dain` → ad erat (toward was)
  - `kain` → erat (was)
- **Pattern:** Shorter variant of -aiin

#### Medium-Confidence Suffixes (Use with care)

**`-ar`** (Conjunction/Connection)
- **Meaning:** et (and)
- **Confidence:** 0.6
- **Usage:** Connective suffix
- **Examples:**
  - `ar` → et (and)
  - `char` → planta et (plant and)
- **Pattern:** Common in lists or connections

**`-ol`** (Place/Location)
- **Meaning:** locus (place)
- **Confidence:** 0.6
- **Usage:** Location marker
- **Examples:**
  - `chol` → caulis (stem/stalk)
  - `shol` → hic locus (here place)
- **Pattern:** Often botanical parts in herbal context

**`-or`** (Order/Arrangement)
- **Meaning:** ordo (order)
- **Confidence:** 0.5
- **Usage:** Arrangement/structure
- **Examples:**
  - `chor` → ramus (branch - ordered growth)
  - `tor` → tangit ordo (touches order)
- **Pattern:** Sometimes just part of root

### Root Identification

**How to find roots:**

1. **Remove known prefixes and suffixes**
   - Example: `qokaiin` → remove `qo-` and `-aiin` → `ka` (unlikely root)
   - Better: `qokaiin` → `ko` + `kaiin` → find `kaiin` pattern

2. **Look for 3+ letter sequences in dictionary**
   - Example: `otchody` contains `chod` (presents)
   - Plausible: `ot-` + `chod` + `-y`

3. **Check frequency of potential root**
   - If proposed root appears alone or in other compounds, more likely real
   - Example: `chol` appears standalone and in `okchol`, `otchol`

4. **Validate against context**
   - Does proposed meaning fit where word appears?
   - Botanical context → botanical root
   - Astronomical context → astronomical root

---

## 🔍 Decomposition Strategies

### Strategy 1: Greedy Matching (Most Common)

**Approach:** Match longest known prefix, then longest suffix, check if middle is known root

**Algorithm:**
```
1. Try each prefix (longest first)
2. If prefix matches:
   a. Try each suffix on remainder (longest first)
   b. If suffix matches:
      i. Check if middle part is in dictionary
      ii. If yes → found valid decomposition!
3. Record all valid decompositions
4. Rank by confidence
```

**Example: `qotchedy`**
```
Try qo- : matches! Remainder: tchedy
  Try -edy : matches! Root candidate: tch
    tch not in dictionary ✗

Try qo- : matches! Remainder: tchedy
  Try -y : matches! Root candidate: tched
    tched not in dictionary ✗

Try ot- : matches! Remainder: chedy
  Try -edy : matches! Root candidate: ch
    ch not in dictionary ✗
  Try -y : matches! Root candidate: ched
    ched not in dictionary ✗

Conclusion: No clean decomposition found. Try other strategies.
```

### Strategy 2: Embedded Root Search

**Approach:** Find known roots anywhere in the word

**Algorithm:**
```
1. For each dictionary word of length ≥ 3:
   2. If that word appears in unknown word:
      a. Mark position
      b. Note what's before and after
      c. Check if before/after match prefix/suffix patterns
```

**Example: `kokaiin`**
```
Check all 3+ letter dictionary entries:
- "kok" - not in dictionary
- "aiin" - YES! It's in dictionary (est/erat)
- Position: at end

Structure: kok + aiin
- "aiin" (state marker) ✓
- "kok" - similar to "kedy" (makes)?
- Hypothesis: kok (makes) + aiin (is) = "makes be" = ripens

Confidence: 0.7 (embedded known suffix, plausible root)
```

### Strategy 3: Systematic Generation

**Approach:** Generate all possible prefix+root+suffix combinations, check which exist

**Algorithm:**
```
1. For each known root R:
   2. For each prefix P:
      3. For each suffix S:
         4. Generate P+R+S
         5. Check if it appears in unknown words
         6. If yes → propose addition
```

**Example: Root `chol` (stem)**
```
Generate variations:
- qo + chol = qochol (not found)
- qo + chol + ar = qocholar (not found)
- qo + chol + aiin = qocholaiin (not found)
- ok + chol = okchol (FOUND 3x!) ✓
  → Propose: okchol = "caulem facit" (makes stem)

- ot + chol = otchol (FOUND 2x!) ✓
  → Propose: otchol = "ex caule" (from stem)
```

### Strategy 4: Context-Based Hypothesis

**Approach:** Use where word appears to guess meaning

**Algorithm:**
```
1. Find all occurrences of unknown word
2. Note what's in the same sentence/line
3. Note what's illustrated (if botanical)
4. Propose meaning based on context
5. Try to find morphological support
```

**Example: `pchor` (appears 8x in herbal section)**
```
Context analysis:
- Appears near: fachys (leaf), chol (stem), fchor (fruit)
- Visual: appears in descriptions near plant parts
- Frequency: 8x, all botanical

Hypothesis: plant material/substance

Morphological check:
- p- prefix: "planta" (plant-related) ✓
- -or: "ordo" or just part of "chor" root?
- Similar to "chor" (ramus/branch)

Proposed: pchor = "resina" (resin - plant material)
Confidence: 0.6 (context + weak morphology)

Validation: Needs human review of folio images
```

---

## 💡 Finding New Words: Systematic Approach

### Step-by-Step Method

#### 1. Start with High-Frequency Unknowns

**Why:** Maximum impact per word added

**How:**
```bash
python scripts/word_frequency.py --min-freq 15 --top 20
```

**Focus on:**
- Frequency ≥ 20: Critical priorities
- Frequency 15-19: High priorities
- Frequency 10-14: Medium priorities

#### 2. Group by Structural Similarity

**Why:** Patterns emerge across similar words

**How:** Manually group words by:
- Same prefix (all qo- words)
- Same suffix (all -aiin words)
- Same length (all 6-letter words)
- Similar appearance

**Example grouping:**
```
qo- words:
- qotchedy (16x)
- qokchor (16x)
- qotchey (16x)
- qoy (16x)

Pattern: All high-frequency, probably verbs
Strategy: Decompose as qo- + [base]
```

#### 3. Analyze Each Group

**For prefix groups:**
```bash
python scripts/morphology_analyzer.py --word qotchedy
python scripts/morphology_analyzer.py --word qokchor
# Compare decompositions
```

**Look for:**
- Consistent decomposition pattern
- Known roots appearing
- Similar contexts

#### 4. Generate Word Families

**When you have solid root:**
```bash
python scripts/morphology_analyzer.py --generate-family [root]
```

**Example: Root `chol` (stem)**
```
Generated family:
- qochol (not found - skip)
- otchol (found!) - propose: "ex caule" (from stem)
- shochol (not found - skip)
- choledy (not found - skip)
- cholar (found!) - propose: "caulis et" (stem and)
- cholol (not found - skip)
```

**Batch add:** Only generate forms that actually appear in text

#### 5. Context Validation

**For each proposal:**
1. Find where word appears
2. Check surrounding words
3. Verify proposed meaning fits
4. Check visual evidence (botanical terms)
5. Assign confidence score

#### 6. Propose in Batches

**Batch size:** 5-10 words per iteration

**Why:**
- Easier to validate
- Test impact before continuing
- Catch errors early
- Manageable workload

---

## 🎨 Context-Specific Translation

### Herbal Sections (q01, q02)

**Vocabulary priorities:**
- Plant parts: root, stem, leaf, flower, fruit, seed
- Growth verbs: grows, extends, produces, ripens
- Descriptors: tall, small, dry, green
- Locations: here, from, to, in, around

**Latin preferences:**
- Botanical terms: herba, planta, flos, folium, radix
- Classical forms: caulis, ramus, fructus, semen

**Context clues:**
- Near illustrations of plants
- Grouped with other botanical terms
- Repeated in similar structural positions

**Example translations:**
```
fachys → folium (leaf)
chol → caulis (stem)
chor → ramus (branch)
fchey → petala (petals)
qokedy → crescit (grows)
```

### Astronomical Sections (q13, etc.)

**Vocabulary priorities:**
- Celestial objects: star, moon, planet, sun
- Movements: shines, rises, sets, moves
- Durations: long, when, again
- Positions: above, around, between

**Latin preferences:**
- Astronomical terms: stella, luna, sol, planeta
- Movement verbs: lucet, ascendit, descendit

**Context clues:**
- Near star diagrams
- In circular/radial layouts
- With temporal markers

**Example translations:**
```
okeey → quando (when)
qoke → ascendit (rises)
cthar → caelum (sky)
qokar → planeta (planet)
```

### Biological Sections (q20, etc.)

**Vocabulary priorities:**
- Water terms: flows, pool, channel
- Body parts: body, tube, organ
- Movements: flows, extends, exits
- Containers: pool, vessel, reservoir

**Latin preferences:**
- Fluid terms: aqua, humor, fluit
- Anatomical: corpus, canalis, ductus

**Example translations:**
```
cphy → piscina (pool)
shey → exit (goes out)
qokaiin → canalis (channel)
```

---

## 📊 Confidence Scoring System

### Assigning Confidence Levels

**0.9-1.0 (Certain):**
- Exact match to known pattern
- Frequency ≥ 20
- Clear morphological decomposition
- Context strongly confirms
- Multiple evidence sources agree

**Example:** `ar` → "et" (and)
- Frequency: 500+
- Length: 2 (typical function word)
- Appears between nouns consistently
- Matches Latin grammar patterns

**0.7-0.8 (Very Confident):**
- Good morphological decomposition
- Frequency ≥ 10
- Context supports meaning
- Similar to known words

**Example:** `kokaiin` → "maturat" (ripens)
- Frequency: 20
- Decomposition: kok + aiin (makes + is)
- Context: near fruit descriptions
- Plausible meaning synthesis

**0.5-0.6 (Moderate Confidence):**
- Weak morphological support
- Frequency ≥ 5
- Context somewhat supports
- Requires validation

**Example:** `schy` → "hic tangit" (here touches)
- Frequency: 19
- Possible decomposition: s + chy
- Context: descriptive passages
- Needs visual confirmation

**0.3-0.4 (Low Confidence):**
- Unclear morphology
- Low frequency
- Weak context support
- Multiple interpretations possible

**< 0.3 (Very Uncertain):**
- No morphological support
- Very low frequency
- No context clues
- Pure speculation

**Action by confidence:**
- ≥ 0.8: Propose for addition
- 0.6-0.7: Propose with caveats
- 0.4-0.5: Mark for further research
- < 0.4: Skip for now

---

## ✅ Quality Control Checklist

Before proposing any word for addition, verify:

### Morphological Validation
- [ ] Clear decomposition into known components
- [ ] Decomposition confidence ≥ 0.6
- [ ] Pattern matches existing entries
- [ ] No contradictions with similar words

### Frequency Validation
- [ ] Appears ≥ 5 times (absolute minimum)
- [ ] Preferably ≥ 10 times
- [ ] Checked across multiple folios
- [ ] Not a transcription artifact

### Context Validation
- [ ] Meaning fits where word appears
- [ ] Consistent across all occurrences
- [ ] Matches section type (herbal/astro/bio)
- [ ] Visual evidence supports (if applicable)

### Dictionary Validation
- [ ] Not already in dictionary
- [ ] Not duplicate of existing entry
- [ ] Latin translation appropriate
- [ ] Description explains reasoning

### Format Validation
- [ ] Word is lowercase
- [ ] Latin translation is reasonable length
- [ ] Description is clear and informative
- [ ] All required fields present

---

## 🔬 Advanced Techniques

### Polysemy Detection and Handling

**When to suspect polysemy:**
- Word appears in 2+ different section types
- Frequency distribution uneven across sections
- Context suggests different meanings
- Morphology could support multiple interpretations

**Investigation process:**
```bash
# Find where word appears
grep -r "wordhere" data/folios/

# Check different sections
# q01 (Herbal A), q02 (Herbal B), q13 (Astro), q20 (Bio)
```

**Example: `shol`**
```
Analysis:
- Herbal sections: near plant locations → "locus" (place)
- Astronomical: in spatial contexts → "spatium" (space)
- Frequency: 15x herbal, 8x astronomical

Decision: Create polysemous entry

Entry format:
- word: shol
  meanings:
    - latin: locus
      context: herbal section, plant locations
    - latin: spatium  
      context: astronomical section, celestial space
  base: locus
```

### Compound Word Generation

**When useful:**
- Known productive roots
- Clear prefix/suffix patterns
- Want to batch-add related words

**Process:**
1. Identify productive root (appears in multiple compounds)
2. Generate all prefix + root combinations
3. Generate all root + suffix combinations
4. Cross-reference with actual unknowns
5. Only add combinations that exist in text

**Example:**
```python
root = "chol" (stem)
prefixes = ["qo", "ot", "sh", "dy"]
suffixes = ["aiin", "edy", "ar", "y"]

# Generate combinations
for prefix in prefixes:
    word = prefix + root
    if word_appears_in_unknowns(word):
        propose_addition(word, synthesize_meaning(prefix, root))

# Results:
# okchol (found) → propose
# otchol (found) → propose
# qochol (not found) → skip
```

### Pattern-Based Discovery

**Use pattern detection to find:**
- Formulaic phrases (whole phrase might have special meaning)
- Word pairs (collocations suggest meaning)
- Positional patterns (word always appears in same position → grammatical role)

**Example:**
```bash
python scripts/pattern_detector.py --pattern-type pairs --min-occurrences 5

# Find: "daiin shy" appears 15x
# Pattern: [word] daiin shy [word]
# Interpretation: "to here" = location formula
# Don't add "daiin shy" as single word, but note pattern
```

---

## 📖 Worked Example: Complete Analysis

### Unknown Word: `qotchedy` (16 occurrences)

#### Step 1: Initial Analysis
```bash
python scripts/word_frequency.py --min-freq 1
# Output: qotchedy: 16x, appears in q01, q02
```

**Observation:** High frequency, appears in herbal sections

#### Step 2: Morphological Decomposition
```bash
python scripts/morphology_analyzer.py --word qotchedy
```

**Result:**
```
Possible decompositions:
1. qo + tchedy (confidence: 0.3)
   - qo = valde (intensifier) ✓
   - tchedy = unknown root ✗

2. qot + chedy (confidence: 0.4)
   - qot = unknown
   - chedy = in (herbal direction) ✓

3. qo + tch + edy (confidence: 0.5)
   - qo = valde ✓
   - tch = touches? (related to tchy?)
   - edy = movet (action) ✓
```

**Best hypothesis:** qo + tch + edy

#### Step 3: Check Related Words
```bash
grep -r "tch" data/folios/
```

**Found:**
- otchy (ex in)
- tchy (touches)
- tchey (touches element)

**Pattern:** tch- family related to touching/contact

#### Step 4: Context Analysis

Check occurrences in translations:
- Appears in plant description passages
- Near words about plant parts and growth
- Not near specific botanical terms

#### Step 5: Synthesize Meaning

**Morphology:** qo (very) + tch (touches) + edy (moves/acts)
**Context:** Plant descriptions, growth passages
**Proposed meaning:** "grows extensively" or "extends greatly"

**Latin options:**
- "valde extendit" (very much extends)
- "valde crescit" (grows greatly)

**Choose:** "valde extendit" (more specific to movement)

#### Step 6: Confidence Assessment

- Frequency: 16 ✓ (HIGH)
- Morphology: 0.5 (moderate - tch- pattern exists but not solid)
- Context: botanical growth ✓
- Overall confidence: **0.65** (MEDIUM)

#### Step 7: Proposal

```yaml
- word: qotchedy
  latin: valde extendit
  description: "qo- intensifier + tch (touches) + -edy (action); describes extensive growth/extension in botanical context"
```

#### Step 8: Validation Gate

**Present to human:**
```
Propose adding: qotchedy → "valde extendit" (extends greatly)

Frequency: 16x (high priority)
Confidence: 0.65 (medium - requires review)

Reasoning:
- Morphology: qo- (intensifier) + tch (touch/contact) + -edy (action)
- Context: Botanical descriptions of plant growth
- Related words: tchy, tchey, otchy (touch family)

Caveats:
- tch- pattern not fully established
- Could also mean "grows greatly" (valde crescit)
- Recommend visual validation with folio images

Approve for addition? [yes/no/modify]
```

---

## 🎓 Learning from Examples

### Success Case: `kokaiin`

**Why it worked:**
- Very high frequency (20x)
- Clear embedded suffix (-aiin)
- Context strongly supported (fruits)
- Morphology made sense (kok + aiin = makes + is = ripens)
- Coverage improved after addition

**Lessons:**
- High frequency words are safest bets
- Embedded known components boost confidence
- Context validation is critical

### Failure Case: `pcho!daiin`

**Why it failed:**
- Appears to be formulaic phrase, not single word
- Exclamation mark suggests special notation
- Adding it didn't improve coverage
- May be abbreviation or title

**Lessons:**
- Not every unknown is a vocabulary word
- Special characters suggest special handling
- Check if "word" is actually a phrase
- Some unknowns may require different approach

---

## 🚀 Best Practices Summary

1. **Start with high-frequency words** (≥15 occurrences)
2. **Use morphological decomposition** as primary method
3. **Validate with context** - meaning must fit where used
4. **Check visual evidence** for botanical terms
5. **Be consistent** - similar words should have similar patterns
6. **Document reasoning** - explain why you think X means Y
7. **Assign honest confidence** - don't overestimate
8. **Batch similar words** - handle word families together
9. **Request validation** - when uncertain, ask human
10. **Track what works** - learn from successes and failures

---

**Remember:** Vocabulary extension is science, not guesswork. Every addition should have clear morphological, contextual, or frequency-based justification. When in doubt, mark for review rather than adding blindly.

Good luck with your research! 📚🔬

