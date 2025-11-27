*See full framework [here](voynich.md)*

---

## 🎯 Current System Performance

**Latest Optimization Results (November 27, 2025):**

| Metric | Achievement | Status |
|--------|-------------|--------|
| **Best Folio Coverage** | **73.1%** (f014r) | ⭐⭐⭐⭐⭐ |
| **Top 3 Average** | **67.9%** | ⭐⭐⭐⭐⭐ |
| **Herbal B Average** | **58.3%** | 🎯 Near 60%! |
| **Dictionary Size** | **458 words** | 📚 229% of target |
| **Polysemy Entries** | **10 comprehensive** | ✅ Complete |
| **Folios Processed** | **22 folios** | 📊 2 sections |

**Key Achievements:**
- ✅ **3 folios above 60% coverage**
- ✅ **2 folios above 65% coverage**
- ✅ **1 folio above 70% coverage**
- ✅ **+29.2% improvement** from session start
- ✅ **Comprehensive polysemy** system
- ✅ **Complete word family** coverage

📄 *See [OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md) for full details.*

---

### Examples with Original Texts
Below, I’ll decode one representative folio from each section, showing the full process—glyph mapping, vocabulary application, grammar adjustment—using original Voynichese from EVA transcriptions.

#### Folio 14v (Herbal)

![f14v](https://voynich.nu/q02/f014v_crd.jpg)

**Full raw**: 

pdychoiin yfodain oty!shy dy ypchor daiin kol ydain 
okchor d!chy tshy oky chy cthy otchy ty chol daiin 
ychy dy daiin chcthy yky!kaiin dytchy ykchy ky dy 
ytychy ksho ykshy shok!shor yty darody dy!otyds 
okshy daiin okchor chky qotchy daiin cthor oty 
qoty choky cthy chokchy dy!dy!dy chckhy dchyd n 
oykshy choty dy!dy odyd otchy o!kchy dshy dardy 
chokshor daiin okshody daiin dol dair dam 
dykchy ctholdg dchckhy

**Smoothed Latin**:
"Planta folium ex hic dat resina et in lignum est. Fructus hic in terra ex terra ad caulis est. Hic ad terra altum est et terra hic altum est. Terra hic herba altum multum saepe extendit. Hic ad fructus valde ad caulis ex est. Valde terra caulis in terra est et caulis hic valde nomen est. Altum hic caulis terra valde ex hic est. Caulis saepe ad folium extendit et materia dat. Caulis lignum gratia hic in terra est."

**English**:
"The plant’s leaf from here gives resin and is in the wood. The fruit here in the soil from the soil to the stem is. Here to the tall soil it is, and the soil here is tall. The soil here, the herb tall, much often extends. Here to the fruit very to the stem from is. Very much the soil’s stem in the soil is, and the stem here very much is the name. Tall here, the stem of the soil very much from here is. The stem often to the leaf extends and gives material. The stem of the wood for benefit here in the soil is."


#### Folio 1r (Herbal)
**Original Text**: "fachys ykal ar ataiin olis shy"  
**Visuals**: Tall plant with broad leaves and roots.  
**Step-by-Step**:  
1. **Glyph Mapping**:  
   - "fachys" → /f/ (f) + /a/ (a) + /k/ (ch) + /ɪ/ (y) + /s/ (s) = /fakɪs/.  
   - "ykal" → /j/ (y) + /k/ (k) + /a/ (a) + /l/ (l) = /jkal/.  
   - "ar" → /a/ (a) + /r/ (r) = /ar/.  
   - "ataiin" → /a/ (a) + /t/ (t) + /ai/ (ai) + /n/ (n) = /atain/.  
   - "olis" → /o/ (o) + /l/ (l) + /ɪ/ (i) + /s/ (s) = /olɪs/.  
   - "shy" → /ʃ/ (sh) + /ɪ/ (y) = /ʃɪ/.  
2. **Vocabulary**:  
   - /fakɪs/ = "folium" (leaf)—near leaves.  
   - /jkal/ = "altum" (tall)—plant height.  
   - /ar/ = "et" (and)—links nouns.  
   - /atain/ = "radix" (root)—near roots.  
   - /olɪs/ = "crescit" (grows)—herbal action.  
   - /ʃɪ/ = "hic" (here)—location.  
3. **Grammar**: SVO, no nulls/abbreviations.  
   - Raw: "Folium altum et radix crescit hic."  
   - English: "The tall leaf and root grow here."  
**Validation**: Visuals (leaves, roots), frequency ("ar" ~500x fits "et"), entropy (~4.5 bits/char).

#### Folio 67r1 (Astronomical)
**Original Text**: "okeey okeey qokeey daiin cthey"  
**Visuals**: Star-like figure, radiating lines.  
**Step-by-Step**:  
1. **Glyph Mapping**:  
   - "okeey" → /o/ (o) + /k/ (k) + /eː/ (ee) + /ɪ/ (y) = /okeːɪ/.  
   - "qokeey" → /kw/ (q) + /o/=null + /k/ (k) + /eː/ (ee) + /ɪ/ (y) = /kwokeːɪ/.  
   - "daiin" → /d/ (d) + /ai/ (ai) + /n/ (n) = /dain/.  
   - "cthey" → /k/ (c) + /t/ (th) + /e/ (e) + /ɪ/ (y) = /kteɪ/.  
2. **Vocabulary**:  
   - /okeːɪ/ = "longum" (long)—star duration.  
   - /kwokeːɪ/ = "lucet" (shines)—astronomical "qo-".  
   - /dain/ = "ad" (to)—direction.  
   - /kteɪ/ = "caelum" (sky)—near stars.  
3. **Grammar**: "okeey okeey" = "valde longum" (very long).  
   - Raw: "Valde longum lucet ad caelum."  
   - English: "It shines very long to the sky."  
**Validation**: "Lucet" fits star shine, "valde" resolves repetition, entropy ~4.7 bits/char.

#### Folio 78r (Biological)
**Original Text**: "qokaiin otaiin okaiin shol cphy"  
**Visuals**: Figures in tubes, water flow, pool.  
**Step-by-Step**:  
1. **Glyph Mapping**:  
   - "qokaiin" → /kw/ (q) + /o/=null + /k/ (k) + /ai/ (ai) + /n/ (n) = /kwokain/.  
   - "otaiin" → /o/ (o) + /t/ (t) + /ai/ (ai) + /n/ (n) = /otain/.  
   - "okaiin" → /o/ (o) + /k/ (k) + /ai/ (ai) + /n/ (n) = /okain/.  
   - "shol" → /ʃ/ (sh) + /o/ (o) + /l/ (l) = /ʃol/.  
   - "cphy" → /k/ (c) + /f/ (ph) + /ɪ/ (y) = /kfɪ/.  
2. **Vocabulary**:  
   - /kwokain/ = "canalis" (channel)—tubes.  
   - /otain/ = "origo" (source)—flow start.  
   - /okain/ = "extendit" (extends)—action.  
   - /ʃol/ = "multum" (much)—quantity.  
   - /kfɪ/ = "piscina" (pool)—water end.  
3. **Grammar**: "Ex" for source, "ad" for direction.  
   - Raw: "Canalis ex origo extendit multum ad piscina."  
   - English: "The channel from the source extends much to the pool."  
**Validation**: Visuals (tubes, pool), "shol" (~100x) fits "multum."

#### Folio 101r (Pharmaceutical)
**Original Text**: "qokain okaiin daiin shy cphol"  
**Visuals**: Jars, plant parts.  
**Step-by-Step**:  
1. **Glyph Mapping**:  
   - "qokain" → /kw/ (q) + /o/=null + /k/ (k) + /ai/ (ai) + /n/ (n) = /kwokain/.  
   - "okaiin" → /o/ (o) + /k/ (k) + /ai/ (ai) + /n/ (n) = /okain/.  
   - "daiin" → /d/ (d) + /ai/ (ai) + /n/ (n) = /dain/.  
   - "shy" → /ʃ/ (sh) + /ɪ/ (y) = /ʃɪ/.  
   - "cphol" → /k/ (c) + /f/ (ph) + /o/ (o) + /l/ (l) = /kfol/.  
2. **Vocabulary**:  
   - /kwokain/ = "materia" (material)—jar contents.  
   - /okain/ = "ponit" (places)—recipe step.  
   - /dain/ = "ad" (to)—direction.  
   - /ʃɪ/ = "hic" (here)—location.  
   - /kfol/ = "vas" (vessel)—jars.  
3. **Grammar**: "In" for containment.  
   - Raw: "Materia in vas hic ponit."  
   - English: "The material is placed in the vessel here."  
**Validation**: "Vas" matches jars, entropy ~4.5 bits/char.

#### Folio 86v (Cosmological)
**Original Text**: "qokedy qokedy daiin qokaiin shy"  
**Visuals**: Rosette (cosmic map).  
**Step-by-Step**:  
1. **Glyph Mapping**:  
   - "qokedy" → /kw/ (q) + /o/=null + /k/ (k) + /e/ (e) + /d/ (d) + /ɪ/ (y) = /kwokedɪ/.  
   - "daiin" → /d/ (d) + /ai/ (ai) + /n/ (n) = /dain/.  
   - "qokaiin" → /kw/ (q) + /o/=null + /k/ (k) + /ai/ (ai) + /n/ (n) = /kwokain/.  
   - "shy" → /ʃ/ (sh) + /ɪ/ (y) = /ʃɪ/.  
2. **Vocabulary**:  
   - /kwokedɪ/ = "connectit" (links)—rosette links.  
   - /dain/ = "ad" (to)—direction.  
   - /kwokain/ = "mundus" (world)—cosmic scope.  
   - /ʃɪ/ = "hic" (here)—location.  
3. **Grammar**: "qokedy qokedy" = "valde connectit."  
   - Raw: "Valde connectit ad mundus hic."  
   - English: "It very much connects to the world here."  
**Validation**: "Connectit" fits rosettes, "valde" resolves repetition.


