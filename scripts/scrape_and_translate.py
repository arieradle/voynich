#!/usr/bin/env python3
"""
Automated workflow: Scrape quire(s) and batch translate them

This script automates the complete workflow:
1. Scrape quire from voynich.nu
2. Convert to standard format
3. Update metadata
4. Batch translate all folios

Usage:
    python scripts/scrape_and_translate.py --quire q07
    python scripts/scrape_and_translate.py --quire q07 q08 q09
    python scripts/scrape_and_translate.py --quire q07 --force  # Force re-translation
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import argparse


class QuireWorkflow:
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.scraped_dir = self.base_dir / "data" / "scraped"
        self.folios_dir = self.base_dir / "data" / "folios"
        self.metadata_file = self.folios_dir / "metadata.json"
        
    def load_metadata(self):
        """Load existing metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_metadata(self, metadata):
        """Save updated metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def scrape_quire(self, quire: str) -> bool:
        """Step 1: Scrape quire from voynich.nu"""
        print(f"\n{'='*70}")
        print(f"📥 STEP 1: Scraping {quire.upper()}")
        print(f"{'='*70}\n")
        
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.base_dir / "scrape_voynich_nu.py"),
                    "--quire", quire,
                    "--output-dir", str(self.scraped_dir)
                ],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error scraping {quire}: {e.stderr}")
            return False
    
    def convert_to_standard_format(self, quire: str) -> int:
        """Step 2: Convert scraped files to standard format"""
        print(f"\n{'='*70}")
        print(f"🔄 STEP 2: Converting {quire.upper()} to standard format")
        print(f"{'='*70}\n")
        
        scraped_quire_dir = self.scraped_dir / quire
        if not scraped_quire_dir.exists():
            print(f"❌ Scraped directory not found: {scraped_quire_dir}")
            return 0
        
        # Create quire directory in folios
        quire_folios_dir = self.folios_dir / quire
        quire_folios_dir.mkdir(exist_ok=True)
        
        # Convert files
        converted = 0
        for scraped_file in sorted(scraped_quire_dir.glob("f*_tr.txt")):
            # Extract folio name (e.g., f049r from f049r_tr.txt)
            folio_name = scraped_file.stem.replace("_tr", "")
            
            # Target file: data/folios/q07/f049r.txt
            target_file = quire_folios_dir / f"{folio_name}.txt"
            
            # Copy content
            target_file.write_text(scraped_file.read_text())
            print(f"  ✓ Converted: {folio_name}.txt")
            converted += 1
        
        print(f"\n✅ Converted {converted} folios to {quire_folios_dir}")
        return converted
    
    def update_metadata(self, quire: str) -> int:
        """Step 3: Update metadata.json with new folios"""
        print(f"\n{'='*70}")
        print(f"📝 STEP 3: Updating metadata for {quire.upper()}")
        print(f"{'='*70}\n")
        
        metadata = self.load_metadata()
        quire_dir = self.folios_dir / quire
        
        if not quire_dir.exists():
            print(f"❌ Quire directory not found: {quire_dir}")
            return 0
        
        added = 0
        for folio_file in sorted(quire_dir.glob("f*.txt")):
            folio_id = folio_file.stem[1:]  # Remove 'f' prefix (e.g., '049r')
            key = f"{quire}_f{folio_id}"
            
            if key not in metadata:
                metadata[key] = {
                    "file": str(folio_file),
                    "section": quire,
                    "folio_id": folio_id,
                    "downloaded_at": datetime.now().isoformat()
                }
                print(f"  ✓ Added: {key}")
                added += 1
            else:
                print(f"  ⚠ Already exists: {key}")
        
        self.save_metadata(metadata)
        print(f"\n✅ Metadata updated: {added} new entries")
        return added
    
    def batch_translate(self, quire: str, force: bool = False) -> bool:
        """Step 4: Batch translate all folios in quire"""
        print(f"\n{'='*70}")
        print(f"🌍 STEP 4: Batch translating {quire.upper()}")
        print(f"{'='*70}\n")
        
        # Extract quire number (e.g., "07" from "q07")
        quire_num = quire[1:]  # Remove 'q' prefix
        
        # Find start and end folio numbers
        quire_dir = self.folios_dir / quire
        folios = sorted(quire_dir.glob("f*.txt"))
        
        if not folios:
            print(f"❌ No folios found in {quire_dir}")
            return False
        
        # Extract folio numbers
        folio_numbers = []
        for f in folios:
            # Extract number from filename (e.g., "049" from "f049r.txt")
            num = f.stem[1:4]  # Characters 1-3 (skip 'f', take 3 digits)
            folio_numbers.append(num)
        
        start_num = min(folio_numbers)
        end_num = max(folio_numbers)
        
        print(f"Translating folios {start_num} to {end_num}...")
        
        # Build command
        cmd = [
            sys.executable,
            str(self.base_dir / "translate_folio.py"),
            "--section", quire,
            "--start", start_num,
            "--end", end_num
        ]
        
        if force:
            cmd.append("--force")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error translating: {e.stderr}")
            print(e.stdout)
            return False
    
    def process_quire(self, quire: str, force: bool = False) -> bool:
        """Complete workflow for a single quire"""
        print(f"\n{'#'*70}")
        print(f"# Processing {quire.upper()}")
        print(f"{'#'*70}")
        
        # Step 1: Scrape
        if not self.scrape_quire(quire):
            return False
        
        # Step 2: Convert
        converted = self.convert_to_standard_format(quire)
        if converted == 0:
            return False
        
        # Step 3: Update metadata
        added = self.update_metadata(quire)
        
        # Step 4: Translate
        if not self.batch_translate(quire, force):
            return False
        
        print(f"\n{'='*70}")
        print(f"✅ {quire.upper()} COMPLETE!")
        print(f"{'='*70}")
        print(f"  Folios converted: {converted}")
        print(f"  Metadata entries: {added}")
        print(f"  Translations: data/translations/{quire}_*.json")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Scrape and translate Voynich quires automatically",
        epilog="""
Examples:
  # Scrape and translate a single quire
  python scripts/scrape_and_translate.py --quire q07
  
  # Scrape and translate multiple quires
  python scripts/scrape_and_translate.py --quire q07 q08 q09
  
  # Force re-translation of existing translations
  python scripts/scrape_and_translate.py --quire q07 --force
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--quire",
        nargs="+",
        required=True,
        help="Quire(s) to process (e.g., q07 q08 q09)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-translation even if translations exist"
    )
    
    args = parser.parse_args()
    
    # Process each quire
    workflow = QuireWorkflow()
    success_count = 0
    fail_count = 0
    
    for quire in args.quire:
        if workflow.process_quire(quire, args.force):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 WORKFLOW SUMMARY")
    print(f"{'='*70}")
    print(f"  ✅ Successful: {success_count}")
    print(f"  ❌ Failed: {fail_count}")
    print(f"  Total: {len(args.quire)}")
    print(f"{'='*70}\n")
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

