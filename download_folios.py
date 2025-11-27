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
        async with httpx.AsyncClient(timeout=30.0) as client:
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
                        # Remove trailing markers (!, =, -)
                        cleaned = re.sub(r'[{!=-]+$', '', word)
                        # Remove anything in curly braces
                        cleaned = re.sub(r'\{.*?\}', '', cleaned)
                        # Remove internal hyphens
                        cleaned = re.sub(r'-', '', cleaned)
                        # Strip whitespace
                        cleaned = cleaned.strip()
                        if cleaned:
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
    
    async def download_section(self, section: str, start: int = 1, end: int = 50, force: bool = False):
        """Download multiple folios from a section"""
        print(f"\n📥 Downloading {SECTION_MAP.get(section, section)} folios ({start}-{end})")
        
        tasks = []
        for i in range(start, end + 1):
            for side in ['r', 'v']:
                folio_id = f"{i:03d}{side}"
                tasks.append(self.download_folio(section, folio_id, force))
        
        results = await asyncio.gather(*tasks)
        successful = [r for r in results if r is not None]
        
        print(f"\n✓ Downloaded {len(successful)} folios")
        return successful
    
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
    
    parser = argparse.ArgumentParser(description="Download Voynich manuscript folios")
    parser.add_argument("--section", default="q02", help="Section code (q01, q02, etc.)")
    parser.add_argument("--start", type=int, default=1, help="Start folio number")
    parser.add_argument("--end", type=int, default=20, help="End folio number")
    parser.add_argument("--force", action="store_true", help="Force re-download")
    parser.add_argument("--list", action="store_true", help="List cached folios")
    
    args = parser.parse_args()
    
    downloader = FolioDownloader()
    
    if args.list:
        print("\n📚 Cached folios:")
        for folio in downloader.list_cached_folios():
            print(f"  • {folio['key']:20s} - {folio['section']:20s} ({folio['word_count']} words)")
    else:
        await downloader.download_section(
            args.section, 
            args.start, 
            args.end,
            args.force
        )


if __name__ == "__main__":
    asyncio.run(main())

