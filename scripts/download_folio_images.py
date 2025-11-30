#!/usr/bin/env python3
"""
Download folio illustration images from voynich.nu

This script downloads high-quality images of Voynich manuscript folios
for visual correlation analysis with translations.

Source: https://voynich.nu/ - Direct card image URLs
Format: https://voynich.nu/{quire}/f{folio_id}_crd.jpg
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List
import requests


class FolioImageDownloader:
    """Download folio images from voynich.nu using card image URLs"""
    
    # Voynich.nu direct image pattern
    BASE_URL = "https://voynich.nu"
    # Format: https://voynich.nu/q02/f014r_crd.jpg
    
    def __init__(self, output_dir: str = "data/folio_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Manifest to track downloads
        self.manifest_path = self.output_dir / "image_manifest.json"
        self.manifest = self.load_manifest()
        
        # Headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://voynich.nu/'
        }
    
    def load_manifest(self) -> Dict:
        """Load existing download manifest"""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        return {"downloaded": {}, "failed": [], "metadata": {}}
    
    def save_manifest(self):
        """Save download manifest"""
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def get_quire_from_folio(self, folio_id: str) -> str:
        """
        Determine quire from folio number
        
        Examples:
          f014r -> q02 (folio 14 is in quire 2)
          f085r1 -> q14 (folio 85 is in quire 14)
        """
        # Extract folio number
        import re
        match = re.search(r'(\d+)', folio_id)
        if not match:
            return 'q00'
        
        folio_num = int(match.group(1))
        
        # Quire mapping based on voynich.nu structure
        # Note: Quires don't follow strict sequential numbering
        if 1 <= folio_num <= 8:
            return 'q01'
        elif 9 <= folio_num <= 24:
            return 'q02'
        elif 25 <= folio_num <= 40:
            return 'q03'
        elif 41 <= folio_num <= 56:
            return 'q04'
        elif 57 <= folio_num <= 64:
            return 'q05'
        elif 65 <= folio_num <= 72:
            return 'q06'
        elif 73 <= folio_num <= 80:
            return 'q07'
        elif 81 <= folio_num <= 84:
            return 'q08'
        elif 85 <= folio_num <= 86:
            return 'q14'  # Q14 is special (f085-f086)
        elif 87 <= folio_num <= 92:
            return 'q15'
        elif 93 <= folio_num <= 100:
            return 'q16'
        elif 101 <= folio_num <= 108:
            return 'q17'
        elif 109 <= folio_num <= 116:
            return 'q18'
        else:
            return 'q00'  # Unknown
    
    def get_folio_image_url(self, folio_id: str, quire: str = None) -> str:
        """
        Construct direct image URL using voynich.nu card format
        
        Format: https://voynich.nu/{quire}/f{folio_id}_crd.jpg
        
        Examples:
          f014r -> https://voynich.nu/q02/f014r_crd.jpg
          f085r1 -> https://voynich.nu/q14/f085r1_crd.jpg
        """
        # Normalize folio ID
        folio = folio_id.lower()
        if not folio.startswith('f'):
            folio = 'f' + folio
        
        # Determine quire if not provided
        if quire is None:
            quire = self.get_quire_from_folio(folio)
        
        return f"{self.BASE_URL}/{quire}/{folio}_crd.jpg"
    
    def download_image(self, url: str, output_path: Path) -> bool:
        """Download a single image with validation"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check if it's actually an image (not HTML error page)
            content_type = response.headers.get('Content-Type', '')
            if 'image' not in content_type:
                return False
            
            # Download
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify file size
            file_size = output_path.stat().st_size
            if file_size < 1000:  # Less than 1KB is probably an error
                output_path.unlink()
                return False
            
            return True
        
        except requests.RequestException:
            return False
    
    def download_folio_images(self, folio_id: str, quire: str = None, force: bool = False) -> Dict:
        """
        Download image for a specific folio
        
        Args:
            folio_id: Folio identifier (e.g., 'f014r', 'f085r1')
            quire: Optional quire identifier (auto-detected if not provided)
            force: Re-download even if already downloaded
        
        Returns:
            Dict with download results
        """
        # Check if already downloaded
        if folio_id in self.manifest['downloaded'] and not force:
            print(f"✓ {folio_id} already downloaded (use --force to re-download)")
            return self.manifest['downloaded'][folio_id]
        
        print(f"\n📥 Downloading image for {folio_id}...")
        
        # Create folio directory
        folio_dir = self.output_dir / folio_id
        folio_dir.mkdir(parents=True, exist_ok=True)
        
        # Get image URL
        if quire is None:
            quire = self.get_quire_from_folio(folio_id)
        
        image_url = self.get_folio_image_url(folio_id, quire)
        output_path = folio_dir / f"{folio_id}.jpg"
        
        print(f"   🔗 {image_url}")
        print(f"   📥 Downloading...", end=' ')
        
        # Download
        if output_path.exists() and not force:
            print("(cached)")
            success = True
            cached = True
        else:
            if self.download_image(image_url, output_path):
                file_size = output_path.stat().st_size / 1024  # KB
                print(f"✓ ({file_size:.1f} KB)")
                success = True
                cached = False
            else:
                print("✗")
                success = False
                cached = False
        
        # Save to manifest
        if success:
            result = {
                'folio_id': folio_id,
                'quire': quire,
                'image_url': image_url,
                'local_path': str(output_path),
                'file_size_kb': output_path.stat().st_size / 1024 if output_path.exists() else 0,
                'status': 'success',
                'cached': cached
            }
            
            self.manifest['downloaded'][folio_id] = result
            print(f"   ✅ Saved to {output_path}")
        else:
            if folio_id not in self.manifest['failed']:
                self.manifest['failed'].append(folio_id)
            result = {
                'folio_id': folio_id,
                'quire': quire,
                'status': 'failed',
                'error': 'Download failed or invalid image'
            }
            print(f"   ❌ Download failed")
        
        self.save_manifest()
        return result
    
    def download_quire_images(self, quire: str, force: bool = False) -> List[Dict]:
        """
        Download images for all folios in a quire
        
        Args:
            quire: Quire identifier (e.g., 'q02', 'q14')
            force: Re-download even if already downloaded
        
        Returns:
            List of download results
        """
        print(f"\n📚 Downloading images for {quire.upper()}...")
        
        # Get list of folios in this quire from existing transcriptions
        folios_dir = Path(f"data/folios/{quire}")
        
        if not folios_dir.exists():
            print(f"❌ No folios found in {folios_dir}")
            print(f"   Run scraping first: python scrape_voynich_nu.py --quire {quire}")
            return []
        
        # Find all .txt files
        folio_files = sorted(folios_dir.glob("f*.txt"))
        
        if not folio_files:
            print(f"⚠️  No folio files found in {folios_dir}")
            return []
        
        # Extract folio IDs
        folio_ids = [f.stem for f in folio_files]
        
        print(f"   📄 Found {len(folio_ids)} folios in {quire}")
        
        # Download images for each folio
        results = []
        for folio_id in folio_ids:
            result = self.download_folio_images(folio_id, quire=quire, force=force)
            results.append(result)
            
            # Rate limiting
            time.sleep(0.5)
        
        # Summary
        successful = [r for r in results if r.get('status') == 'success']
        failed = len(results) - len(successful)
        total_size = sum(r.get('file_size_kb', 0) for r in successful)
        
        print(f"\n✅ {quire.upper()} Complete:")
        print(f"   • Folios processed: {len(results)}")
        print(f"   • Successful: {len(successful)}")
        print(f"   • Failed: {failed}")
        print(f"   • Total size: {total_size:.1f} KB ({total_size/1024:.1f} MB)")
        
        return results
    
    def list_downloaded(self) -> Dict:
        """List all downloaded folio images"""
        if not self.manifest['downloaded']:
            print("\n📭 No images downloaded yet.")
            return {}
        
        print(f"\n📊 Downloaded Folio Images ({len(self.manifest['downloaded'])} folios):\n")
        
        total_size = 0
        for folio_id, data in sorted(self.manifest['downloaded'].items()):
            size_kb = data.get('file_size_kb', 0)
            total_size += size_kb
            
            print(f"  {folio_id} ({data.get('quire', '?')}):")
            print(f"    • Size: {size_kb:.1f} KB")
            print(f"    • Path: {data.get('local_path', 'N/A')}")
        
        total_mb = total_size / 1024
        print(f"\n📦 Total: {len(self.manifest['downloaded'])} images, {total_size:.1f} KB ({total_mb:.1f} MB)")
        
        if self.manifest['failed']:
            print(f"\n❌ Failed downloads ({len(self.manifest['failed'])}):")
            for folio_id in self.manifest['failed']:
                print(f"  • {folio_id}")
        
        return self.manifest


def main():
    parser = argparse.ArgumentParser(
        description="Download Voynich folio illustration images from voynich.nu",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download image for a single folio
  python scripts/download_folio_images.py --folio f014r
  
  # Download images for multiple folios
  python scripts/download_folio_images.py --folio f014r f014v f015r
  
  # Download images for entire quire
  python scripts/download_folio_images.py --quire q02
  
  # Download for multiple quires
  python scripts/download_folio_images.py --quire q02 q03 q04
  
  # Force re-download
  python scripts/download_folio_images.py --folio f014r --force
  
  # List downloaded images
  python scripts/download_folio_images.py --list

Source: https://voynich.nu/ (card images with _crd.jpg suffix)
        """
    )
    
    parser.add_argument(
        '--folio',
        nargs='+',
        help='Folio ID(s) to download (e.g., f014r, f085r1)'
    )
    
    parser.add_argument(
        '--quire',
        nargs='+',
        help='Quire(s) to download all folios from (e.g., q02, q14)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all downloaded images'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-download even if images already exist'
    )
    
    parser.add_argument(
        '--output-dir',
        default='data/folio_images',
        help='Output directory for images (default: data/folio_images)'
    )
    
    args = parser.parse_args()
    
    # Create downloader
    downloader = FolioImageDownloader(output_dir=args.output_dir)
    
    # List downloaded
    if args.list:
        downloader.list_downloaded()
        return
    
    # Download folios
    if args.folio:
        for folio_id in args.folio:
            downloader.download_folio_images(folio_id, force=args.force)
    
    # Download quires
    if args.quire:
        for quire in args.quire:
            downloader.download_quire_images(quire, force=args.force)
    
    # Show help if no action specified
    if not (args.folio or args.quire or args.list):
        parser.print_help()


if __name__ == '__main__':
    main()

