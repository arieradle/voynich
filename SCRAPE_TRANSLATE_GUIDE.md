# Quick Scrape & Translate Guide

## ✨ NEW: One-Command Workflow!

### Simple Usage

```bash
# Scrape and translate a single quire
python scripts/scrape_and_translate.py --quire q07

# Scrape and translate multiple quires at once
python scripts/scrape_and_translate.py --quire q07 q08 q09

# Force re-translation (even if already translated)
python scripts/scrape_and_translate.py --quire q07 --force
```

## What It Does Automatically

1. **📥 Scrapes** the quire from voynich.nu
2. **🔄 Converts** files to standard format
3. **📝 Updates** metadata.json
4. **🌍 Translates** all folios in batch
5. **✅ Reports** complete statistics

## Example Output

```
######################################################################
# Processing Q08
######################################################################

======================================================================
📥 STEP 1: Scraping Q08
======================================================================
✓ Found: f057r, f057v, f058r, f058v, f065r, f065v, f066r, f066v
✅ 8/8 downloaded

======================================================================
🔄 STEP 2: Converting Q08 to standard format
======================================================================
✓ Converted: f057r.txt ... (8 folios)
✅ Converted 8 folios

======================================================================
📝 STEP 3: Updating metadata for Q08
======================================================================
✓ Added: q08_f057r ... (8 entries)
✅ Metadata updated: 8 new entries

======================================================================
🌍 STEP 4: Batch translating Q08
======================================================================
Translating folios 057 to 066...
✅ Batch complete: Average coverage: 55.7%

======================================================================
✅ Q08 COMPLETE!
======================================================================
  Folios converted: 8
  Metadata entries: 8
  Translations: data/translations/q08_*.json
```

## Results

- **Translations saved to:** `data/translations/qXX_fXXXr_translation.json`
- **Folios saved to:** `data/folios/qXX/fXXXr.txt`
- **Metadata updated:** `data/folios/metadata.json`

## Available Quires

Currently supported on voynich.nu:
- q01 through q20 (approximately)
- Some quires may have gaps in folio numbers
- Script handles this automatically

## Old Workflow (No Longer Needed!)

~~1. Scrape with `scrape_voynich_nu.py`~~
~~2. Parse with `parse_transcriptions.py`~~
~~3. Convert file formats manually~~
~~4. Update metadata manually~~
~~5. Translate with `translate_folio.py`~~

**Now just:** `python scripts/scrape_and_translate.py --quire qXX` 🎉

---

## Advanced: Manual Steps (If Needed)

### Individual Commands

```bash
# 1. Scrape only
python scrape_voynich_nu.py --quire q07

# 2. Translate only (if already scraped)
python translate_folio.py --section q07 --start 49 --end 56

# 3. Check metadata
jq 'keys | length' data/folios/metadata.json
```

### Troubleshooting

**"Folio not found":**
- Run: `python scripts/scrape_and_translate.py --quire qXX`
- This will re-scrape and update metadata

**"Already translated":**
- Use `--force` flag to re-translate
- Or delete translation files manually

**Missing quire:**
- Some quires may not exist on voynich.nu
- Check: https://www.voynich.nu/

---

**Status:** ✅ Automated workflow operational!
**Created:** November 28, 2025
**Script:** `scripts/scrape_and_translate.py`

