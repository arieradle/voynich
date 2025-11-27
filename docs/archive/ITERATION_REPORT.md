# Voynich Translation System - Iteration Report
**Date:** November 27, 2025  
**Task:** Fix Section Fetching + Complete Translation Analysis

---

## ✅ What Was Accomplished

### 1. Fixed Download System ✓
**Problem:** `download_folios.py` assumed all sections had sequential numbering starting from 001, but the Voynich manuscript has different folio ranges per section.

**Solution Implemented:**
- Added `SECTION_FOLIOS` mapping with section-specific folio ranges
- Modified `download_section()` to auto-detect appropriate ranges
- Added `--all-sections` flag for bulk downloading
- Improved CLI with better help text and organized folio listing
- Fixed SSL certificate issue for macOS compatibility

**Discovery:** Only **2 sections** are available on voynich.nu:
- `q01` (Herbal A): f001r-f008v (8 folios, 16 pages)
- `q02` (Herbal B): f014r-f016v (3 folios, 6 pages)
- Other sections (q03-q20) have no EVA transcriptions available

### 2. Translated All Available Folios ✓
- **22 folios** (16 Herbal A + 6 Herbal B) fully translated
- All translations saved with 3-text format (Voynich/Latin/English)
- Coverage statistics generated for each folio

### 3. Comprehensive Gap Analysis ✓
- Identified **1,192 unique unknown words**
- Analyzed frequency patterns across sections
- Generated prioritized suggestions for dictionary expansion
- Exported detailed analysis to `dictionary_suggestions.json`

---

## 📊 Current System Performance

### Overall Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Total Folios** | 22 | ✅ All available |
| **Dictionary Size** | 708 words | 📚 Comprehensive |
| **Average Coverage** | 55.6% | 🎯 Good baseline |
| **Herbal A Coverage** | 52.0% | ⭐⭐⭐⭐ |
| **Herbal B Coverage** | 65.2% | ⭐⭐⭐⭐⭐ |
| **Unknown Words** | 1,192 unique | 📈 Room for growth |

### Coverage by Folio (Sorted by Performance)

#### Top Performers (60%+)
1. **q02_f014r**: 79.6% ⭐⭐⭐⭐⭐ (172/216 words)
2. **q02_f015v**: 73.6% ⭐⭐⭐⭐⭐ (204/277 words)
3. **q02_f014v**: 67.0% ⭐⭐⭐⭐⭐ (179/267 words)
4. **q01_f006r**: 61.6% ⭐⭐⭐⭐ (141/229 words)
5. **q02_f016v**: 61.0% ⭐⭐⭐⭐ (133/218 words)
6. **q01_f005r**: 60.4% ⭐⭐⭐⭐ (99/164 words)

#### Good Performance (50-60%)
7. **q01_f001r**: 58.1% (638/1099 words) - Largest folio
8. **q01_f005v**: 58.2% (106/182 words)
9. **q01_f004r**: 56.9% (111/195 words)
10. **q02_f016r**: 55.5% (127/229 words)
11. **q02_f015r**: 54.3% (158/291 words)
12. **q01_f007v**: 54.1% (145/268 words)
13. **q01_f006v**: 53.7% (260/484 words)
14. **q01_f003r**: 52.1% (174/334 words)
15. **q01_f008v**: 51.6% (188/364 words)
16. **q01_f001v**: 51.6% (111/215 words)
17. **q01_f004v**: 50.2% (154/307 words)

#### Needs Improvement (<50%)
18. **q01_f002r**: 47.9% (104/217 words)
19. **q01_f002v**: 54.1% (125/231 words)
20. **q01_f003v**: 42.9% (154/359 words)
21. **q01_f008r**: 43.3% (151/349 words)
22. **q01_f007r**: 35.0% ⚠️ (56/160 words) - Lowest coverage

---

## 🔍 Key Findings

### 1. Section Performance Gap
**Herbal B outperforms Herbal A by 13.2%**
- Herbal B (q02): 65.2% average coverage
- Herbal A (q01): 52.0% average coverage

**Possible Reasons:**
- Herbal B folios may use more consistent vocabulary
- Dictionary may be biased toward Herbal B patterns
- q01_f001r is an outlier (1099 words - much larger than average)

### 2. High-Frequency Unknown Words

**Top 10 Missing Words (appearing 16-22 times):**

| Word | Frequency | Sections | Pattern Analysis |
|------|-----------|----------|------------------|
| `o` | 22x | Both | Single char - likely function word |
| `*` | 19x | Both | Transcription artifact (needs cleaning) |
| `otchody` | 18x | Both | Compound: ot + chod + y suffix |
| `dan` | 17x | Both | Short - preposition or article? |
| `qokchor` | 16x | Both | qo- prefix + kchor (intensifier) |
| `qotchey` | 16x | Both | qo- prefix + tchey (touch/element) |
| `qoy` | 16x | Both | qo- prefix + y (very + motion?) |
| `yty` | 16x | Both | Repeated y-t pattern |
| `!!!!!!!!odar` | 16x | A only | Transcription error (excess markers) |
| `!!!!!!!!ydain` | 16x | A only | Transcription error (excess markers) |

### 3. Data Quality Issues

**Critical:** Many "unknown words" are actually transcription artifacts:
- `*` (19x) - asterisk marker
- `!!!!!!!!odar` (16x) - excess exclamation marks
- `%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%` (multiple) - separator lines
- `o` (22x) - possibly null glyph 'o' not being stripped correctly

**Impact:** Fixing these artifacts could **immediately improve coverage by 3-5%**

### 4. Pattern Insights

**qo- Prefix Family** (highly productive):
- `qokchor` (16x)
- `qotchey` (16x)
- `qoy` (16x)
- All need systematic dictionary entries

**Compound Words** (many unknowns are known roots combined):
- `otchody` = ot + chod + y (components exist)
- Need better morphological parsing

---

## 🎯 Next Iteration Recommendations

### Phase 1: Data Cleaning (Immediate - 1 hour)
**Priority: HIGH** | **Impact: +3-5% coverage**

1. **Fix transcription artifact handling:**
   - Strip excessive markers (`!!!!`, `%%%%`, etc.)
   - Handle `*` as unknown glyph marker, not a word
   - Improve null glyph 'o' detection
   - Clean folio files or update parser

2. **Update parser in `download_folios.py`:**
   ```python
   # Remove excessive markers
   cleaned = re.sub(r'^[!%*]{5,}', '', word)
   # Skip separator lines
   if cleaned.startswith('%%%') or len(cleaned) > 50:
       continue
   ```

3. **Re-translate all folios** after cleaning

**Expected Result:** Coverage jumps to 58-61% average

---

### Phase 2: Dictionary Expansion (Medium term - 2-3 hours)
**Priority: HIGH** | **Impact: +5-10% coverage**

#### A. Add High-Frequency Missing Words (Top 20)

Focus on words appearing 10+ times:

| Word | Suggested Latin | Reasoning |
|------|----------------|-----------|
| `otchody` | crescit ad | ot (extends) + chod (varies) + y suffix |
| `dan` | de | preposition - "from/of" |
| `qokchor` | valde ramulus | qo + kchor (very + branch) |
| `qotchey` | valde tangit | qo + tchey (very touches) |
| `qoy` | valde ad | qo + y (very to/toward) |
| `yty` | transit | y-t-y pattern (movement) |

**Process:**
1. Read raw folio text for context
2. Look at surrounding known words
3. Check visual context from folio images
4. Add to `voynich.yaml` with notes
5. Re-translate and validate

#### B. Expand Systematic Word Families

Based on productive patterns:

**qo- prefix family** (20+ new entries):
- qo + all known verb roots
- Format: "valde + [base verb]"

**-ody suffix family** (15+ new entries):
- All known roots + ody
- Format: "[base] + growth/action"

**Compound families:**
- ot- + known verbs
- dy- + known nouns
- ch- + additional compounds

**Expected Result:** Coverage reaches 60-65% average

---

### Phase 3: Morphological Parser (Long term - 4-6 hours)
**Priority: MEDIUM** | **Impact: +10-15% coverage**

**Goal:** Automatically decompose unknown compounds into known roots

**Implementation:**
1. Create `morphology.py` module
2. Add component detection:
   ```python
   def decompose_word(word, dictionary):
       # Try known prefixes: qo-, ot-, dy-, ch-
       # Try known suffixes: -ain, -aiin, -edy, -ody, -idy
       # Try known roots in middle
       # Return: [prefix, root, suffix] + confidence
   ```
3. Integrate into `translator.py`
4. Generate translations from components
5. Track confidence scores

**Example:**
- Input: `otchody`
- Decompose: `ot` (extends) + `chod` (varies) + `y` (action marker)
- Output: "extends variation" → Latin: "variat extensum"

**Expected Result:** Coverage reaches 70-75% average

---

### Phase 4: Context-Aware Translation (Advanced - 8+ hours)
**Priority: LOW** | **Impact: +5-10% coverage + quality**

**Goal:** Use surrounding words and visual context for better translations

**Features:**
1. **Sentence-level analysis:**
   - Track word co-occurrence patterns
   - Use context window (±3 words)
   - Prefer translations that create coherent sentences

2. **Visual context integration:**
   - Download folio images programmatically
   - Manual tagging: "near roots", "near flowers", "near diagram"
   - Use tags to disambiguate polysemous words

3. **Section-specific refinement:**
   - Build separate sub-dictionaries per section
   - Track which words are unique to Herbal A vs B
   - Adjust polysemy based on actual usage

4. **Confidence scoring improvements:**
   - Factor in morphological decomposition confidence
   - Factor in sentence coherence
   - Factor in visual context matches

**Expected Result:** Coverage reaches 75-80% with improved quality

---

## 🚀 Recommended Action Plan

### Week 1: Quick Wins
- [ ] **Day 1:** Data cleaning (Phase 1)
- [ ] **Day 2:** Add top 20 high-frequency words (Phase 2A)
- [ ] **Day 3:** Test and validate improvements
- [ ] **Target:** 60% average coverage

### Week 2: Systematic Expansion
- [ ] **Days 4-6:** Expand word families (Phase 2B)
- [ ] **Day 7:** Re-translate and analyze
- [ ] **Target:** 65% average coverage

### Month 2: Advanced Features
- [ ] **Week 1:** Build morphological parser (Phase 3)
- [ ] **Week 2:** Integrate and test
- [ ] **Week 3-4:** Context-aware features (Phase 4)
- [ ] **Target:** 70-75% average coverage

---

## 📁 Files Modified This Session

1. **`download_folios.py`** 
   - Added `SECTION_FOLIOS` mapping
   - Updated `download_section()` with auto-ranges
   - Added `download_all_sections()` method
   - Improved CLI interface
   - Fixed SSL certificate issue

2. **Generated/Updated:**
   - `data/translations/*.json` (all 22 folios re-translated)
   - `data/dictionary_suggestions.json` (975 candidates)
   - `ITERATION_REPORT.md` (this file)

---

## 💡 Key Insights for Future Work

### 1. Limited Dataset
- Only 22 folios available (16 Herbal A + 6 Herbal B)
- Need alternative sources for other sections:
  - Consider other transcription databases
  - Manual transcription from Yale Beinecke images
  - Community transcription projects

### 2. Data Quality Critical
- Transcription artifacts are inflating unknown word counts
- Clean data = better metrics + easier analysis
- Consider pre-processing pipeline before translation

### 3. Morphology is Key
- Many "unknown" words are compounds of known roots
- Systematic morphological decomposition could unlock 10-15% more coverage
- This is the next major breakthrough opportunity

### 4. Herbal B Success Model
- 65.2% coverage shows the system works well when vocabulary matches
- Study what makes Herbal B successful
- Apply those patterns to improve Herbal A

### 5. Coverage Ceiling
- With current approach, realistic ceiling is ~80-85%
- Remaining 15-20% likely requires:
  - Linguistic expertise (medieval Latin/Romance languages)
  - Visual context integration
  - Statistical/ML approaches for rare words
  - Collaboration with Voynich research community

---

## 🎓 Lessons Learned

1. **Always validate data sources** - Assumed all sections existed on voynich.nu
2. **Clean data first** - Artifacts waste analysis time
3. **Incremental progress works** - 55% coverage is solid progress
4. **Patterns are powerful** - qo- prefix family is highly productive
5. **Context matters** - Herbal B's success shows domain vocabulary importance

---

## ✅ Summary

**What Works:**
- ✅ Automated pipeline for download → translate → analyze
- ✅ Deterministic dictionary-based translation
- ✅ 708-word dictionary with good herbal vocabulary
- ✅ 65% coverage on Herbal B (excellent!)
- ✅ Systematic gap analysis and prioritization

**What Needs Work:**
- ⚠️ Data cleaning (transcription artifacts)
- ⚠️ Morphological decomposition of compounds
- ⚠️ Herbal A vocabulary gaps
- ⚠️ Limited dataset (only 2 sections)

**Next Steps:**
1. **Immediate:** Clean transcription artifacts (+3-5%)
2. **Short-term:** Add top 20 missing words (+5-10%)
3. **Medium-term:** Build morphological parser (+10-15%)
4. **Long-term:** Context-aware translation (+5-10%)

**Projected Outcome:**
- Current: 55.6% average
- After cleanup: ~60%
- After expansion: ~65%
- After morphology: ~72%
- After context: ~80%

---

**Ready for next iteration! 🚀**

