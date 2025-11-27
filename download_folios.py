#!/usr/bin/env python3
"""
Download and cache Voynich manuscript folios from voynich.nu
"""

import asyncio
import httpx
import re
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime


# Section mapping from URL path to manuscript section
SECTION_MAP = {
    "q01": "Herbal A",
    "q02": "Herbal B", 
    "q03": "Biological",
    "q04": "Astrological",
    "q05": "Pharmaceutical",
    "q13": "Stars",
    "q20": "Text-only",
}

# Actual folio ranges per section available on voynich.nu
# Format: (start_folio, end_folio) - inclusive
# Note: voynich.nu has limited EVA transcriptions, not all folios are available
SECTION_FOLIOS = {
    "q01": (1, 8),       # Herbal A: f001r-f008v (8 folios, 16 pages)
    "q02": (14, 16),     # Herbal B: f014r-f016v (3 folios, 6 pages)
    # Other sections (q03-biological, q04-astrological, q05-pharmaceutical, 
    # q13-stars, q20-text) do not appear to have transcriptions on voynich.nu
    # For full manuscript access, use other sources like:
    # - Yale Beinecke Library: https://brbl-dl.library.yale.edu/vufind/Record/3519597
    # - Voynich.nu main site may have other formats
}

# Base URL for voynich.nu transcriptions
BASE_URL = "https://www.voynich.nu"


class FolioDownloader:
    """Download and manage Voynich manuscript folios"""
    
    def __init__(self, cache_dir: str = "data/folios"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load cached metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save metadata to disk"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    async def fetch_folio_text(self, url: str) -> Optional[str]:
        """Fetch a single folio text from URL"""
        # Use verify=False to avoid SSL certificate issues on some systems
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.RequestError as exc:
                print(f"❌ Error requesting {url}: {exc}")
                return None
            except httpx.HTTPStatusError as exc:
                print(f"❌ HTTP {exc.response.status_code} for {url}")
                return None
    
    def parse_folio_text(self, text: str, url: str) -> Dict:
        """Parse EVA transcription and extract metadata"""
        # Extract folio ID from URL
        match_page = re.search(r'f(\d{3}[rv]\d?)', url)
        folio_id = match_page.group(1) if match_page else "unknown"
        
        # Extract section from URL path
        match_section = re.search(r'voynich\.nu/([a-z0-9]+)/', url)
        folder = match_section.group(1) if match_section else "unknown"
        section = SECTION_MAP.get(folder, folder)
        
        # Parse lines
        lines = []
        voynich_words = []
        
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Keep original line
            lines.append(line)
            
            # Extract Voynichese if it's a transcription line
            if line.startswith('<f'):
                parts = line.split('>')
                if len(parts) >= 2:
                    prefix = parts[0] + '>'
                    text_part = parts[1]
                    
                    # Clean up: remove annotations, hyphens, etc.
                    words = text_part.split('.')
                    cleaned_words = []
                    for word in words:
                        # Remove anything in curly braces first
                        cleaned = re.sub(r'\{[^}]*\}', '', word)
                        # Remove ampersands (alternate readings)
                        cleaned = re.sub(r'&', '', cleaned)
                        # Remove excessive markers at start (!!!!!!)
                        cleaned = re.sub(r'^[!*%]{3,}', '', cleaned)
                        # Remove trailing markers (!, =, -, *)
                        cleaned = re.sub(r'[!*=\-]+$', '', cleaned)
                        # Remove internal markers but keep letters
                        # Replace ! * , in middle with nothing (uncertain chars and transcriber disagreement markers)
                        cleaned = re.sub(r'[!*,]', '', cleaned)
                        # Remove internal hyphens
                        cleaned = re.sub(r'-', '', cleaned)
                        # Remove parentheses
                        cleaned = re.sub(r'[()]', '', cleaned)
                        # Strip whitespace
                        cleaned = cleaned.strip()
                        # Skip if empty, too short, or is a separator line
                        if cleaned and len(cleaned) > 1 and not cleaned.startswith('%'):
                            # Skip pure marker sequences
                            if not all(c in '!*%=-' for c in cleaned):
                                cleaned_words.append(cleaned)
                                voynich_words.append(cleaned)
        
        return {
            "folio_id": folio_id,
            "section": section,
            "url": url,
            "raw_lines": lines,
            "voynich_words": voynich_words,
            "word_count": len(voynich_words),
            "downloaded_at": datetime.now().isoformat()
        }
    
    async def download_folio(self, section: str, folio_id: str, force: bool = False) -> Optional[Dict]:
        """
        Download a specific folio
        
        Args:
            section: Section code (q01, q02, etc.)
            folio_id: Folio ID (e.g., '001r', '014v')
            force: Re-download even if cached
        """
        # Construct URL
        url = f"{BASE_URL}/{section}/f{folio_id}_tr.txt"
        cache_key = f"{section}_f{folio_id}"
        cache_file = self.cache_dir / f"{cache_key}.txt"
        
        # Check cache
        if not force and cache_file.exists():
            print(f"✓ Using cached folio: {cache_key}")
            with open(cache_file, 'r') as f:
                text = f.read()
        else:
            print(f"⬇️  Downloading: {url}")
            text = await self.fetch_folio_text(url)
            if not text:
                return None
            
            # Save to cache
            with open(cache_file, 'w') as f:
                f.write(text)
            print(f"✓ Cached: {cache_key}")
        
        # Parse and store metadata
        data = self.parse_folio_text(text, url)
        self.metadata[cache_key] = {
            "folio_id": data["folio_id"],
            "section": data["section"],
            "word_count": data["word_count"],
            "downloaded_at": data["downloaded_at"],
            "file": str(cache_file)
        }
        self._save_metadata()
        
        return data
    
    async def download_section(self, section: str, start: int = None, end: int = None, force: bool = False):
        """
        Download multiple folios from a section
        
        Args:
            section: Section code (q01, q02, etc.)
            start: Starting folio number (defaults to section's natural start)
            end: Ending folio number (defaults to section's natural end)
            force: Re-download even if cached
        """
        # Use section-specific defaults if not specified
        if start is None or end is None:
            if section in SECTION_FOLIOS:
                default_start, default_end = SECTION_FOLIOS[section]
                start = start or default_start
                end = end or default_end
            else:
                start = start or 1
                end = end or 50
        
        print(f"\n📥 Downloading {SECTION_MAP.get(section, section)} folios (f{start:03d}-f{end:03d})")
        
        tasks = []
        for i in range(start, end + 1):
            for side in ['r', 'v']:
                folio_id = f"{i:03d}{side}"
                tasks.append(self.download_folio(section, folio_id, force))
        
        results = await asyncio.gather(*tasks)
        successful = [r for r in results if r is not None]
        
        print(f"\n✓ Downloaded {len(successful)} folios")
        return successful
    
    async def download_all_sections(self, force: bool = False):
        """Download all available sections using their default folio ranges"""
        all_results = []
        for section in SECTION_FOLIOS.keys():
            results = await self.download_section(section, force=force)
            all_results.extend(results)
        return all_results
    
    def list_cached_folios(self) -> List[Dict]:
        """List all cached folios"""
        return [
            {"key": key, **meta} 
            for key, meta in self.metadata.items()
        ]
    
    def get_folio_path(self, section: str, folio_id: str) -> Optional[Path]:
        """Get path to cached folio"""
        cache_key = f"{section}_f{folio_id}"
        if cache_key in self.metadata:
            return Path(self.metadata[cache_key]["file"])
        return None


async def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download Voynich manuscript folios",
        epilog="Examples:\n"
               "  python download_folios.py --section q04  # Downloads all Astrological folios\n"
               "  python download_folios.py --section q03 --start 75 --end 78  # Custom range\n"
               "  python download_folios.py --all-sections  # Download everything!\n"
               "  python download_folios.py --list  # Show what's cached",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--section", help="Section code (q01, q02, q03, q04, q05, q13, q20)")
    parser.add_argument("--start", type=int, help="Start folio number (defaults to section's natural range)")
    parser.add_argument("--end", type=int, help="End folio number (defaults to section's natural range)")
    parser.add_argument("--all-sections", action="store_true", help="Download all sections with their default ranges")
    parser.add_argument("--force", action="store_true", help="Force re-download")
    parser.add_argument("--list", action="store_true", help="List cached folios")
    
    args = parser.parse_args()
    
    downloader = FolioDownloader()
    
    if args.list:
        print("\n📚 Cached folios:")
        folios_by_section = {}
        for folio in downloader.list_cached_folios():
            section = folio['section']
            if section not in folios_by_section:
                folios_by_section[section] = []
            folios_by_section[section].append(folio)
        
        for section in sorted(folios_by_section.keys()):
            folios = folios_by_section[section]
            print(f"\n  {section}:")
            for folio in sorted(folios, key=lambda x: x['key']):
                print(f"    • {folio['key']:20s} ({folio['word_count']} words)")
        
        total = sum(len(v) for v in folios_by_section.values())
        print(f"\n  Total: {total} folios cached")
    
    elif args.all_sections:
        print("\n🌍 Downloading ALL sections...")
        await downloader.download_all_sections(args.force)
    
    elif args.section:
        await downloader.download_section(
            args.section, 
            args.start, 
            args.end,
            args.force
        )
    else:
        parser.print_help()
        print("\n⚠️  Please specify --section, --all-sections, or --list")


if __name__ == "__main__":
    asyncio.run(main())

