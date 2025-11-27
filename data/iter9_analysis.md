# Iteration 9: Analysis of Top Unknown Words
## Target: Folios with Highest Unknown Counts

### Top 15 Folios by Unknown Count:
1. q01_f001r - 357 unknowns (65.4% coverage) - 126 unique
2. q01_f006v - 205 unknowns (54.2% coverage) - 80 unique
3. q01_f008r - 185 unknowns (46.2% coverage) - 84 unique
4. q01_f003v - 182 unknowns (47.2% coverage) - 61 unique
5. q03_f017v - 169 unknowns (57.4% coverage) - 69 unique

### Top 4 High-Frequency Unknown Words:

#### 1. `ctho` (14 occurrences)
- **Frequency**: 14x across 4 section types
- **Sections**: Pharmaceutical, Herbal A, Astrological, Biological
- **Neighbors**: daiin (9x), sho (4x), chees (3x), shy (3x)
- **Example contexts**:
  - "cthy ctho qotaiincthey"
  - "otam ctho mdy lorchor"
  - "cholal ctho cthey shol"
- **Analysis**:
  - Appears near known words: `cthy` (earth), `sho` (here makes), `shy` (here)
  - Similar to `cho` (facit) but with 't' insertion
  - Pattern suggests: c-t-ho structure
  - Hypothesis: ct- prefix + ho → possibly "touches/tangit" + "facit"
  - **Proposed**: tangit (touches) - confidence 0.65
  
#### 2. `cheol` (12 occurrences)
- **Frequency**: 12x across 4 section types
- **Neighbors**: chol (15x), dol (4x), dy (4x), ykaiin (4x)
- **Example contexts**:
  - "choies cheol dol cthey"
  - "chor cheol chol dolody"
- **Analysis**:
  - Very strongly associated with `chol` (pars/caulis - plant part)
  - Pattern: che + ol
  - Similar to `cheor` (variat), `cheod` (pars variat)
  - All `che-` words relate to botanical variation/elements
  - Strong botanical context
  - **Proposed**: folium variat (leaf varies) OR folia (leaves) - confidence 0.70

#### 3. `chan` (11 occurrences)
- **Frequency**: 11x across 4 section types
- **Neighbors**: dor (6x), otchor (4x), daiin (4x), okain (4x)
- **Example contexts**:
  - "otochor alshodaiinchol chan otochor"
  - "otchor chan dor chol"
- **Analysis**:
  - Appears in formulaic contexts with `dor`, `otchor`, `daiin`
  - ch- prefix (botanical) + an suffix
  - Similar pattern to `chai` (alius - other)
  - Could be related to `chol` family
  - **Proposed**: planta (plant) OR herba - confidence 0.65

#### 4. `she` (10 occurrences)
- **Frequency**: 10x
- **Neighbors**: shol (4x), kodshey (4x), sheaiin (4x), cthey (3x)
- **Example contexts**:
  - "cthey she oldain shoy"
  - "shol she kodshey cphealy"
- **Analysis**:
  - Strongly associated with `sh-` location words: `sho`, `shy`, `shol`
  - Dictionary has: `shy` (hic), `sho` (hic facit)
  - Pattern: she = sh- + e (element marker?)
  - Very similar to `shy` but with 'e' instead of 'y'
  - **Proposed**: hic est (here is) OR iste (this) - confidence 0.75

### Morphological Insights:
- `ch-` prefix = botanical (confirmed from 29 ch- words in dictionary)
- `sh-` prefix = location/demonstrative (confirmed: shy, sho, shol)
- `-ol` suffix = location/part (confirmed: chol, dol, olol)
- `-eo-` infix = variation (confirmed: cheor, cheod)
- Short 3-4 letter words are often function words

### Confidence Assessments:
- **Tier 1** (Confidence ≥ 0.7): `she` (0.75), `cheol` (0.70)
- **Tier 2** (Confidence 0.6-0.7): `ctho` (0.65), `chan` (0.65)

### Recommendations:
1. Add Tier 1 words first (`she`, `cheol`) - 22 occurrences
2. Consider Tier 2 after human review - 25 occurrences
3. Total potential impact: 47 word instances resolved
4. Estimated coverage improvement: +1.5% to +2.0%
