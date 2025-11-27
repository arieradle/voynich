# Scraper Implementation Notes

## ✅ File Management

### No Temp Files
The `scrape_voynich_nu.py` script:
- ✅ **Creates NO temporary files**
- ✅ All downloads are saved directly to final locations
- ✅ No cleanup required after scraping
- ✅ Safe for interruption (resume-friendly)

### Output Structure
```
data/scraped/
├── q03/
│   ├── f017r_tr.txt  ← Raw EVA format (permanent)
│   ├── f017v_tr.txt
│   └── ...
├── q04/
└── scrape_manifest.json  ← Metadata (permanent)
```

## 📁 File Flow

### What Gets Created

1. **During Scraping**
   - `data/scraped/{quire}/*.txt` - Downloaded transcriptions
   - `data/scraped/scrape_manifest.json` - Download metadata

2. **For Translation** (manual copy)
   - `data/folios/q03_f*.txt` - Working copies in flat structure
   - `data/folios/metadata.json` - Updated with new entries

3. **After Translation**
   - `data/translations/q03_f*_translation.json` - Translation results

### What NOT to Create

❌ **Do NOT create subdirectories in data/folios/**
- Wrong: `data/folios/q03/f017r.txt`
- Right: `data/folios/q03_f017r.txt`

❌ **Do NOT use parsed/cleaned text files**
- The translator needs raw EVA format with headers
- Skip `parse_transcriptions.py` for translation workflow

## 🗑️ What Can Be Deleted

### After Successful Translation

**Keep:**
- ✅ `data/scraped/` - Source files for reference
- ✅ `data/folios/q03_*.txt` - Working files for translation
- ✅ `data/translations/` - Translation results
- ✅ `data/folios/metadata.json` - Required for translation

**Can Delete (if needed to save space):**
- `data/scraped/{quire}/` - After copying to folios directory
- But recommended to keep for re-downloading if files get corrupted

## 🔄 Resume-Friendly Design

The scraper automatically:
- Skips already-downloaded files
- Can be interrupted and restarted
- No partial downloads (writes complete file at once)
- No file locks or temp states

```bash
# Safe to interrupt and restart
python scrape_voynich_nu.py --quire q03
# Ctrl+C
python scrape_voynich_nu.py --quire q03  # Resumes, skips existing
```

## 📝 Best Practices

### 1. Keep Scraped Files
Recommended to keep `data/scraped/` as a cache:
- Faster re-copying if needed
- Reference for original transcriptions
- No need to re-download from voynich.nu

### 2. Flat Folios Structure
Always maintain flat structure in `data/folios/`:
```bash
# Correct
data/folios/q03_f017r.txt
data/folios/q03_f017v.txt

# Wrong (translator won't find these)
data/folios/q03/f017r.txt
```

### 3. Metadata Sync
After adding new folios:
```python
# Always update metadata.json
# Use the script from SECTION_EXPANSION_GUIDE.md
```

## 🐛 Troubleshooting

### Issue: Files in subdirectories not found
**Symptom:** `FileNotFoundError: Folio not found: q03/f017r`

**Cause:** Files in `data/folios/q03/` instead of `data/folios/`

**Fix:**
```bash
cd data/folios
rm -rf q03/  # Remove subdirectory
# Re-copy from scraped with correct naming
```

### Issue: Parsed files not working
**Symptom:** `Total words: 0` or translation errors

**Cause:** Using cleaned text instead of raw EVA format

**Fix:**
```bash
# Use raw files from data/scraped/, not parse_transcriptions.py output
cp data/scraped/q03/f017r_tr.txt data/folios/q03_f017r.txt
```

## 📊 Storage Requirements

Per quire (approximate):
- Scraped files: ~100-200 KB
- Working files (folios): ~100-200 KB (duplicate)
- Translation results: ~500 KB - 2 MB (JSON with full word list)

**Total for all ~16 quires:** < 50 MB

---

**Created:** November 27, 2025  
**Status:** ✅ Production-ready, no cleanup needed  
**Maintenance:** None required

