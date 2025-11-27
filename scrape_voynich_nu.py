#!/usr/bin/env python3
"""
Voynich.nu Transcription Scraper
Scrapes EVA transcription files from voynich.nu for all quires/sections
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from pathlib import Path
from typing import List, Dict, Tuple
import json


class VoynichNuScraper:
    """Scrape EVA transcriptions from voynich.nu"""
    
    BASE_URL = "https://www.voynich.nu"
    
    # All known quires in the manuscript
    QUIRES = {
        'q01': {'name': 'Quire 1', 'folios': 'f1-f8', 'section': 'Herbal A'},
        'q02': {'name': 'Quire 2', 'folios': 'f9-f16', 'section': 'Herbal A'},
        'q03': {'name': 'Quire 3', 'folios': 'f17-f24', 'section': 'Herbal A'},
        'q04': {'name': 'Quire 4', 'folios': 'f25-f32', 'section': 'Herbal A'},
        'q05': {'name': 'Quire 5', 'folios': 'f33-f40', 'section': 'Herbal A'},
        'q06': {'name': 'Quire 6', 'folios': 'f41-f48', 'section': 'Herbal A'},
        'q07': {'name': 'Quire 7', 'folios': 'f49-f56', 'section': 'Herbal A'},
        'q08': {'name': 'Quire 8', 'folios': 'f57-f65', 'section': 'Herbal B'},
        'q09': {'name': 'Quire 9', 'folios': 'f66-f73', 'section': 'Herbal B'},
        'q10': {'name': 'Quire 10', 'folios': 'f75-f84', 'section': 'Herbal B/Pharmaceutical'},
        'q11': {'name': 'Quire 11', 'folios': 'f85-f86', 'section': 'Pharmaceutical'},
        'q13': {'name': 'Quire 13', 'folios': 'f87-f90', 'section': 'Pharmaceutical'},
        'q14': {'name': 'Quire 14', 'folios': 'f103-f116', 'section': 'Text only (Recipes?)'},
        'q15': {'name': 'Quire 15', 'folios': 'f67-f70+89', 'section': 'Astronomical/Astrological'},
        'q20': {'name': 'Quire 20', 'folios': 'f1-f24', 'section': 'Stars/Cosmological'},
    }
    
    def __init__(self, output_dir: str = "data/scraped"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Voynich Research Bot)'
        })
    
    def get_quire_index_url(self, quire: str) -> str:
        """Get the URL for a quire's index page"""
        return f"{self.BASE_URL}/{quire}/index.html"
    
    def scrape_quire_links(self, quire: str) -> List[Dict[str, str]]:
        """
        Scrape all transliteration file links from a quire index page
        Returns list of dicts with folio info and URLs
        """
        url = self.get_quire_index_url(quire)
        print(f"\n📂 Scraping {quire} index: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        # Find all links to _tr.txt files (transliteration files)
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '_tr.txt' in href:
                # Extract folio ID from filename (e.g., f017r_tr.txt -> f017r)
                match = re.search(r'f(\d+[rv])_tr\.txt', href)
                if match:
                    folio_id = f"f{match.group(1)}"
                    full_url = f"{self.BASE_URL}/{quire}/{href}"
                    
                    links.append({
                        'quire': quire,
                        'folio_id': folio_id,
                        'filename': href,
                        'url': full_url
                    })
                    print(f"  ✓ Found: {folio_id}")
        
        return links
    
    def download_transcription(self, folio_info: Dict[str, str]) -> bool:
        """Download a single transcription file"""
        url = folio_info['url']
        quire = folio_info['quire']
        filename = folio_info['filename']
        
        # Create quire subdirectory
        quire_dir = self.output_dir / quire
        quire_dir.mkdir(exist_ok=True)
        
        output_path = quire_dir / filename
        
        # Skip if already downloaded
        if output_path.exists():
            print(f"  ⏭️  Skipping {filename} (already exists)")
            return True
        
        try:
            print(f"  ⬇️  Downloading {filename}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Save the file
            output_path.write_text(response.text, encoding='utf-8')
            print(f"  ✅ Saved to {output_path}")
            
            # Be polite - don't hammer the server
            time.sleep(0.5)
            return True
            
        except requests.RequestException as e:
            print(f"  ❌ Error downloading {url}: {e}")
            return False
    
    def scrape_quire(self, quire: str) -> Dict:
        """Scrape all transcriptions for a single quire"""
        print(f"\n{'='*70}")
        print(f"🔍 Processing {quire.upper()}: {self.QUIRES.get(quire, {}).get('name', 'Unknown')}")
        print(f"{'='*70}")
        
        # Get all links
        links = self.scrape_quire_links(quire)
        
        if not links:
            print(f"⚠️  No transliteration files found for {quire}")
            return {'quire': quire, 'success': 0, 'failed': 0, 'skipped': 0}
        
        print(f"\n📥 Found {len(links)} transliteration files")
        
        # Download each file
        success = 0
        failed = 0
        
        for folio_info in links:
            if self.download_transcription(folio_info):
                success += 1
            else:
                failed += 1
        
        result = {
            'quire': quire,
            'success': success,
            'failed': failed,
            'total': len(links)
        }
        
        print(f"\n✅ {quire.upper()} complete: {success}/{len(links)} downloaded")
        return result
    
    def scrape_all_quires(self, quires: List[str] = None) -> Dict:
        """Scrape all specified quires (or all if None)"""
        if quires is None:
            quires = list(self.QUIRES.keys())
        
        print(f"\n{'='*70}")
        print(f"🚀 Starting scrape of {len(quires)} quires from voynich.nu")
        print(f"{'='*70}")
        
        results = []
        for quire in quires:
            if quire not in self.QUIRES:
                print(f"⚠️  Unknown quire: {quire}")
                continue
            
            result = self.scrape_quire(quire)
            results.append(result)
        
        # Summary
        total_success = sum(r['success'] for r in results)
        total_failed = sum(r['failed'] for r in results)
        total_files = sum(r['total'] for r in results)
        
        print(f"\n{'='*70}")
        print(f"📊 SCRAPING COMPLETE")
        print(f"{'='*70}")
        print(f"Total files: {total_files}")
        print(f"Downloaded: {total_success}")
        print(f"Failed: {total_failed}")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"{'='*70}\n")
        
        return {
            'results': results,
            'summary': {
                'total': total_files,
                'success': total_success,
                'failed': total_failed
            }
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scrape EVA transcriptions from voynich.nu',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Scrape a single quire
  %(prog)s --quire q03
  
  # Scrape multiple quires
  %(prog)s --quire q03 q04 q05
  
  # Scrape all quires
  %(prog)s --all
  
  # Scrape all astronomical/cosmological sections
  %(prog)s --quire q15 q20
  
  # Scrape with custom output directory
  %(prog)s --quire q13 --output-dir my_transcriptions
        '''
    )
    
    parser.add_argument('--quire', nargs='+', 
                       help='Specific quire(s) to scrape (e.g., q03 q04)')
    parser.add_argument('--all', action='store_true',
                       help='Scrape all available quires')
    parser.add_argument('--output-dir', default='data/scraped',
                       help='Output directory for downloaded files')
    parser.add_argument('--list-quires', action='store_true',
                       help='List all available quires and exit')
    
    args = parser.parse_args()
    
    scraper = VoynichNuScraper(output_dir=args.output_dir)
    
    # List quires if requested
    if args.list_quires:
        print("\n📚 Available Quires:\n")
        print(f"{'Quire':<8} {'Name':<15} {'Folios':<15} {'Section':<30}")
        print("="*70)
        for quire, info in sorted(scraper.QUIRES.items()):
            print(f"{quire:<8} {info['name']:<15} {info['folios']:<15} {info['section']:<30}")
        print()
        return
    
    # Determine which quires to scrape
    if args.all:
        quires = None  # Scrape all
    elif args.quire:
        quires = args.quire
    else:
        # Default: just show help
        parser.print_help()
        print("\n💡 Tip: Use --list-quires to see all available sections")
        return
    
    # Run the scraper
    results = scraper.scrape_all_quires(quires)
    
    # Save results manifest
    manifest_path = scraper.output_dir / 'scrape_manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📄 Manifest saved to: {manifest_path}")


if __name__ == "__main__":
    main()

