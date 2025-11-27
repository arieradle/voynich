# Master Index
# Complete Navigation for Voynich Translation System

This document provides comprehensive navigation for all resources in the Voynich Translation System.

---

## 🎯 Quick Start by Role

### For AI Agents

**Start with these 3 documents in order:**

1. [AI_RESEARCH_GUIDE.md](AI_RESEARCH_GUIDE.md) - Your mission, capabilities, and decision framework
2. [WORKFLOW_INSTRUCTIONS.md](WORKFLOW_INSTRUCTIONS.md) - Complete step-by-step workflow  
3. [VOCABULARY_EXTENSION_GUIDE.md](VOCABULARY_EXTENSION_GUIDE.md) - Linguistic methodology

**Configuration files:**
- [agent_config.yaml](agent_config.yaml) - Your behavior parameters
- [research_workflow.yaml](research_workflow.yaml) - Workflow definition
- [vocabulary_rules.yaml](vocabulary_rules.yaml) - Morphological rules

**Run your first iteration:**
```bash
python scripts/iteration_orchestrator.py --validation-gates
```

### For Developers & Users

**Essential guides:**

1. [README.md](README.md) - Project overview and quick start
2. [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Complete usage guide
3. [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - Technical architecture

**Then:**
- Try translating: `python translate_folio.py --section q02 --folio 014r`
- Analyze gaps: `python analyze_gaps.py --min-freq 5`
- Update dictionary: `python scripts/batch_dictionary_updater.py --interactive`

### For Researchers

**Key documents:**

1. [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md) - Performance metrics and analysis
2. [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - Technical foundation
3. [voynich.md](voynich.md) - Complete decipherment framework (1000+ lines)

**Historical reports:**
- See [docs/archive/](docs/archive/) for 12 archived reports

---

## 📚 Documentation Categories

### 1. AI Agent Instructions

Primary documents for AI agents conducting research:

| Document | Purpose | Priority |
|----------|---------|----------|
| [AI_RESEARCH_GUIDE.md](AI_RESEARCH_GUIDE.md) | **START HERE** - Complete agent instructions, decision framework, examples | ⭐⭐⭐⭐⭐ |
| [WORKFLOW_INSTRUCTIONS.md](WORKFLOW_INSTRUCTIONS.md) | Step-by-step workflow for each iteration phase | ⭐⭐⭐⭐⭐ |
| [VOCABULARY_EXTENSION_GUIDE.md](VOCABULARY_EXTENSION_GUIDE.md) | Linguistic methodology, morphological patterns, worked examples | ⭐⭐⭐⭐⭐ |

### 2. System Documentation

Technical and operational documentation:

| Document | Purpose | Priority |
|----------|---------|----------|
| [README.md](README.md) | Project overview, quick start, navigation | ⭐⭐⭐⭐⭐ |
| [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) | Complete usage guide with all commands | ⭐⭐⭐⭐⭐ |
| [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) | Technical architecture, components, design | ⭐⭐⭐⭐ |
| [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md) | Performance metrics, coherency analysis | ⭐⭐⭐⭐ |
| [MASTER_INDEX.md](MASTER_INDEX.md) | This file - navigation hub | ⭐⭐⭐ |

### 3. Research Foundation

Detailed research materials:

| Document | Purpose | Priority |
|----------|---------|----------|
| [voynich.md](voynich.md) | Complete 1000+ line decipherment framework | ⭐⭐⭐⭐ |
| [docs/archive/](docs/archive/) | 12 historical reports (detailed session logs) | ⭐⭐⭐ |

### 4. Configuration Files

System configuration in YAML format:

| File | Purpose | Priority |
|------|---------|----------|
| [voynich.yaml](voynich.yaml) | Master dictionary - 708 words with descriptions | ⭐⭐⭐⭐⭐ |
| [agent_config.yaml](agent_config.yaml) | AI agent behavior and parameters | ⭐⭐⭐⭐ |
| [research_workflow.yaml](research_workflow.yaml) | Complete 6-phase workflow definition | ⭐⭐⭐⭐ |
| [vocabulary_rules.yaml](vocabulary_rules.yaml) | Morphological and linguistic rules | ⭐⭐⭐⭐ |

---

## 🛠️ Tools & Scripts

### Core Scripts (Root Directory)

| Script | Purpose | Quick Example |
|--------|---------|---------------|
| [download_folios.py](download_folios.py) | Download folios from voynich.nu | `python download_folios.py --section q02` |
| [translator.py](translator.py) | Core translation engine (library) | Used by other scripts |
| [translate_folio.py](translate_folio.py) | CLI for translation | `python translate_folio.py --section q02 --folio 014r` |
| [analyze_gaps.py](analyze_gaps.py) | Gap analysis tool | `python analyze_gaps.py --min-freq 5` |
| [review_and_update.py](review_and_update.py) | Legacy dictionary updater | `python review_and_update.py --interactive` |

### Helper Scripts (scripts/ Directory)

| Script | Purpose | Quick Example |
|--------|---------|---------------|
| [word_frequency.py](scripts/word_frequency.py) | Frequency analysis | `python scripts/word_frequency.py --min-freq 10` |
| [morphology_analyzer.py](scripts/morphology_analyzer.py) | Morphological decomposition | `python scripts/morphology_analyzer.py --word kokaiin` |
| [pattern_detector.py](scripts/pattern_detector.py) | Pattern & formula detection | `python scripts/pattern_detector.py --pattern-type all` |
| [compound_decomposer.py](scripts/compound_decomposer.py) | Compound word analysis | `python scripts/compound_decomposer.py --word qotchedy` |
| [batch_dictionary_updater.py](scripts/batch_dictionary_updater.py) | Dictionary management | `python scripts/batch_dictionary_updater.py --interactive` |
| [validation_checker.py](scripts/validation_checker.py) | System integrity checks | `python scripts/validation_checker.py --check-type all` |
| [iteration_orchestrator.py](scripts/iteration_orchestrator.py) | Full workflow automation | `python scripts/iteration_orchestrator.py --validation-gates` |

---

## 📊 Data Files

### Input Data

| Location | Contents | Purpose |
|----------|----------|---------|
| `data/folios/*.txt` | Downloaded folio transcriptions (EVA format) | Source text |
| `data/folios/metadata.json` | Folio metadata (word counts, sections) | Organization |

### Output Data

| Location | Contents | Purpose |
|----------|----------|---------|
| `data/translations/*.json` | Translation outputs (Voynich, Latin, English) | Results |
| `data/dictionary_suggestions.json` | Gap analysis output | Vocabulary priorities |
| `data/unknown_ranked.json` | Frequency-ranked unknown words | Analysis |
| `data/patterns_detected.json` | Detected patterns | Pattern analysis |
| `data/morphology_analysis.json` | Morphological decompositions | Linguistic analysis |

### Reports

| Location | Contents | Purpose |
|----------|----------|---------|
| `reports/` | Iteration reports | Track progress |
| `docs/archive/` | Historical session reports | Reference |

---

## 🔍 Finding What You Need

### "I want to..."

#### ...understand the system
- Start: [README.md](README.md)
- Deep dive: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- Research: [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md)

#### ...translate a folio
- Guide: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → Translation Commands
- Script: `python translate_folio.py --section q02 --folio 014r`

#### ...extend vocabulary
- AI Agent: [VOCABULARY_EXTENSION_GUIDE.md](VOCABULARY_EXTENSION_GUIDE.md)
- Developer: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → Phase 4: Update Dictionary
- Script: `python scripts/batch_dictionary_updater.py --interactive`

#### ...analyze unknown words
- Guide: [WORKFLOW_INSTRUCTIONS.md](WORKFLOW_INSTRUCTIONS.md) → Phase 2: Analyze Patterns
- Scripts:
  - `python scripts/word_frequency.py --min-freq 5`
  - `python analyze_gaps.py --min-freq 5`

#### ...decompose a compound word
- Guide: [VOCABULARY_EXTENSION_GUIDE.md](VOCABULARY_EXTENSION_GUIDE.md) → Decomposition Strategies
- Scripts:
  - `python scripts/morphology_analyzer.py --word kokaiin`
  - `python scripts/compound_decomposer.py --word qotchedy`

#### ...validate the system
- Script: `python scripts/validation_checker.py --check-type all`
- Reference: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) → Quality Control

#### ...run a complete iteration
- AI Agent: [WORKFLOW_INSTRUCTIONS.md](WORKFLOW_INSTRUCTIONS.md)
- Script: `python scripts/iteration_orchestrator.py --validation-gates`

#### ...understand performance
- Results: [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md)
- Metrics: [README.md](README.md) → Performance section

#### ...configure AI agent behavior
- File: [agent_config.yaml](agent_config.yaml)
- Reference: [AI_RESEARCH_GUIDE.md](AI_RESEARCH_GUIDE.md) → Configuration section

---

## 📖 Reading Paths

### Path 1: Quick Start (30 minutes)

1. [README.md](README.md) - Overview (10 min)
2. [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Quick Start section (5 min)
3. Try commands (15 min):
   - Validate: `python scripts/validation_checker.py --check-type all`
   - Translate: `python translate_folio.py --section q02 --folio 014r`
   - View: `python translate_folio.py --section q02 --show 014r`

### Path 2: AI Agent Onboarding (2 hours)

1. [AI_RESEARCH_GUIDE.md](AI_RESEARCH_GUIDE.md) - Complete read (45 min)
2. [WORKFLOW_INSTRUCTIONS.md](WORKFLOW_INSTRUCTIONS.md) - Complete read (45 min)
3. [VOCABULARY_EXTENSION_GUIDE.md](VOCABULARY_EXTENSION_GUIDE.md) - Skim patterns (30 min)
4. Run: `python scripts/iteration_orchestrator.py --validation-gates`

### Path 3: Developer Deep Dive (4 hours)

1. [README.md](README.md) - Overview (15 min)
2. [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - Complete read (60 min)
3. [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Complete read (45 min)
4. [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md) - Review metrics (30 min)
5. Explore code:
   - `translator.py` - Core engine
   - `scripts/morphology_analyzer.py` - Linguistic logic
6. Run experiments (90 min)

### Path 4: Research Review (3 hours)

1. [README.md](README.md) - Context (15 min)
2. [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md) - Complete read (60 min)
3. [voynich.md](voynich.md) - Skim sections (60 min)
4. [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - Methodology section (30 min)
5. [docs/archive/](docs/archive/) - Browse reports (15 min)

---

## 🎯 Task-Specific Quick Links

### For Translation

**Guides:**
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → Translation Commands
- [WORKFLOW_INSTRUCTIONS.md](WORKFLOW_INSTRUCTIONS.md) → Phase 5: Test

**Scripts:**
- Single: `translate_folio.py --section q02 --folio 014r`
- Batch: `translate_folio.py --section q02 --start 14 --end 16`
- View: `translate_folio.py --section q02 --show 014r`

### For Vocabulary Extension

**Guides:**
- [AI_RESEARCH_GUIDE.md](AI_RESEARCH_GUIDE.md) → Decision Framework
- [VOCABULARY_EXTENSION_GUIDE.md](VOCABULARY_EXTENSION_GUIDE.md) → Finding New Words
- [WORKFLOW_INSTRUCTIONS.md](WORKFLOW_INSTRUCTIONS.md) → Phase 2: Propose

**Scripts:**
- Analyze: `analyze_gaps.py --min-freq 5`
- Frequency: `scripts/word_frequency.py --min-freq 10`
- Morphology: `scripts/morphology_analyzer.py --word WORD`
- Update: `scripts/batch_dictionary_updater.py --interactive`

### For Pattern Analysis

**Guides:**
- [VOCABULARY_EXTENSION_GUIDE.md](VOCABULARY_EXTENSION_GUIDE.md) → Decomposition Strategies
- [WORKFLOW_INSTRUCTIONS.md](WORKFLOW_INSTRUCTIONS.md) → Phase 2.4: Detect Patterns

**Scripts:**
- Patterns: `scripts/pattern_detector.py --pattern-type all`
- Morphology: `scripts/morphology_analyzer.py --batch-file words.txt`
- Compounds: `scripts/compound_decomposer.py --word WORD --strategy all`

### For Quality Control

**Guides:**
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) → Quality Control
- [WORKFLOW_INSTRUCTIONS.md](WORKFLOW_INSTRUCTIONS.md) → Validation Gates

**Scripts:**
- Validate: `scripts/validation_checker.py --check-type all`
- Check dictionary: `scripts/validation_checker.py --check-type dictionary`
- Check translations: `scripts/validation_checker.py --check-type translations`

---

## 📂 File Organization

### Root Directory

```
voynich/
├── README.md                        ⭐⭐⭐⭐⭐ Start here
├── MASTER_INDEX.md                  ⭐⭐⭐ This file
├── AI_RESEARCH_GUIDE.md             ⭐⭐⭐⭐⭐ For AI agents
├── WORKFLOW_INSTRUCTIONS.md         ⭐⭐⭐⭐⭐ Step-by-step
├── VOCABULARY_EXTENSION_GUIDE.md    ⭐⭐⭐⭐⭐ Linguistic guide
├── DEVELOPMENT_GUIDE.md             ⭐⭐⭐⭐ Usage guide
├── SYSTEM_ARCHITECTURE.md           ⭐⭐⭐⭐ Technical docs
├── RESEARCH_RESULTS.md              ⭐⭐⭐⭐ Performance
├── voynich.md                       ⭐⭐⭐⭐ Full framework
├── voynich.yaml                     ⭐⭐⭐⭐⭐ Dictionary
├── agent_config.yaml                ⭐⭐⭐⭐ AI config
├── research_workflow.yaml           ⭐⭐⭐⭐ Workflow
├── vocabulary_rules.yaml            ⭐⭐⭐⭐ Rules
├── Core scripts (download, translate, analyze)
└── LICENSE
```

### Subdirectories

```
scripts/                             ⭐⭐⭐⭐ Helper tools
├── word_frequency.py
├── morphology_analyzer.py
├── pattern_detector.py
├── compound_decomposer.py
├── batch_dictionary_updater.py
├── validation_checker.py
└── iteration_orchestrator.py

data/                                ⭐⭐⭐ Data files
├── folios/                          Transcriptions
├── translations/                    Outputs
├── dictionary_suggestions.json      Gap analysis
└── [other analysis files]

docs/                                ⭐⭐⭐ Documentation
└── archive/                         Historical reports

reports/                             ⭐⭐ Iteration logs
└── iteration_*.md
```

---

## 🚀 Command Quick Reference

### Essential Commands

```bash
# Validate system
python scripts/validation_checker.py --check-type all

# Translate folio
python translate_folio.py --section q02 --folio 014r

# View translation
python translate_folio.py --section q02 --show 014r

# Analyze gaps
python analyze_gaps.py --min-freq 5

# Word frequency
python scripts/word_frequency.py --min-freq 10 --top 20

# Morphology
python scripts/morphology_analyzer.py --word kokaiin

# Update dictionary
python scripts/batch_dictionary_updater.py --interactive --backup

# Full iteration
python scripts/iteration_orchestrator.py --validation-gates
```

### Advanced Commands

See [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → Complete Command Reference

---

## 📊 Current System State

**As of November 27, 2025:**

- **Dictionary**: 708 words
- **Coverage**: 56.6% average (Herbal B: 67.0%, Herbal A: 52.8%)
- **Best Folio**: 73.1% (q02_f014r)
- **Coherency**: 7.0/10 (GOOD)
- **System Status**: ✅ OPERATIONAL & PRODUCTION-READY

**Next Target**: 62-65% combined coverage (3-4 iterations)

---

## 🎓 Learning Resources

### Internal

- **Complete Framework**: [voynich.md](voynich.md)
- **Architecture**: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- **Methodology**: [VOCABULARY_EXTENSION_GUIDE.md](VOCABULARY_EXTENSION_GUIDE.md)
- **Historical Reports**: [docs/archive/](docs/archive/)

### External

- **voynich.nu**: EVA transcriptions and folio images
- **Wikipedia**: Voynich Manuscript overview
- **Yale Beinecke**: High-resolution manuscript scans
- **EVA Standard**: European Voynich Alphabet documentation

---

## 📝 Document Summaries

### One-Sentence Summaries

| Document | Summary |
|----------|---------|
| **README.md** | Project overview with quick start and navigation |
| **AI_RESEARCH_GUIDE.md** | Complete AI agent instructions with decision framework and examples |
| **WORKFLOW_INSTRUCTIONS.md** | Detailed step-by-step workflow for each iteration phase |
| **VOCABULARY_EXTENSION_GUIDE.md** | Linguistic methodology and morphological analysis techniques |
| **DEVELOPMENT_GUIDE.md** | Complete usage guide with all commands and examples |
| **SYSTEM_ARCHITECTURE.md** | Technical architecture, components, and design principles |
| **RESEARCH_RESULTS.md** | Performance metrics, coherency analysis, and achievements |
| **MASTER_INDEX.md** | Comprehensive navigation hub (this document) |
| **voynich.md** | Complete 1000+ line decipherment framework |

---

## 🔗 External Links

### Project Resources

- **Repository**: (local project)
- **Data Source**: https://voynich.nu
- **Folio Images**: https://voynich.nu/q[section]/f[folio].jpg
- **Yale Collection**: https://brbl-dl.library.yale.edu/vufind/Record/3519597

### Related Research

- **EVA Transcription**: Standard Voynich alphabet system
- **Voynich Manuscript (Wikipedia)**: Historical background
- **Medieval Latin Resources**: For translation validation

---

## ✅ Navigation Checklist

**New to the project?**
- [ ] Read [README.md](README.md)
- [ ] Choose your path (AI Agent / Developer / Researcher)
- [ ] Read relevant guides
- [ ] Run validation: `python scripts/validation_checker.py --check-type all`
- [ ] Try a translation: `python translate_folio.py --section q02 --folio 014r`

**AI Agent starting research?**
- [ ] Read [AI_RESEARCH_GUIDE.md](AI_RESEARCH_GUIDE.md)
- [ ] Study [WORKFLOW_INSTRUCTIONS.md](WORKFLOW_INSTRUCTIONS.md)
- [ ] Review [VOCABULARY_EXTENSION_GUIDE.md](VOCABULARY_EXTENSION_GUIDE.md)
- [ ] Check [agent_config.yaml](agent_config.yaml)
- [ ] Run: `python scripts/iteration_orchestrator.py --validation-gates`

**Developer integrating?**
- [ ] Review [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- [ ] Read [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- [ ] Explore code in `scripts/`
- [ ] Check [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md)
- [ ] Run tests: `python scripts/validation_checker.py --check-type all`

**Researcher evaluating?**
- [ ] Check [README.md](README.md) performance metrics
- [ ] Read [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md) 
- [ ] Review [voynich.md](voynich.md) methodology
- [ ] Browse [docs/archive/](docs/archive/) for history
- [ ] Examine [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) technical details

---

**Last Updated**: November 27, 2025  
**System Version**: 5.0 (AI Agent System)  
**Status**: ✅ OPERATIONAL

**Need help finding something? Check the relevant section above or start with [README.md](README.md)!**

