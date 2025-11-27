#!/usr/bin/env python3
"""
Parse EVA transcription files from voynich.nu
Converts interlinear transcriptions to clean folio text format
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
import json


class TranscriptionParser:
    """Parse EVA transcription files into clean text"""
    
    def __init__(self):
        self.folio_metadata = {}
    
    def extract_metadata(self, lines: List[str]) -> Dict[str, str]:
        """Extract metadata from header comments"""
        metadata = {
            'title': '',
            'page': '',
            'folio': '',
            'quire': '',
            'language': '',
            'hand': '',
            'subject': '',
            'colors': '',
            'description': ''
        }
        
        in_description = False
        description_lines = []
        
        for line in lines:
            if not line.startswith('#'):
                break
            
            # Remove leading '# ' and whitespace
            clean_line = line.lstrip('#').strip()
            
            if not clean_line:
                continue
            
            # Extract specific fields
            if 'Title:' in clean_line:
                metadata['title'] = clean_line.split('Title:', 1)[1].strip(' "')
            elif 'Page:' in clean_line:
                metadata['page'] = clean_line.split('Page:', 1)[1].strip()
            elif 'Folio:' in clean_line:
                metadata['folio'] = clean_line.split('Folio:', 1)[1].strip()
            elif 'Quire:' in clean_line:
                metadata['quire'] = clean_line.split('Quire:', 1)[1].strip()
            elif 'Language:' in clean_line:
                metadata['language'] = clean_line.split('Language:', 1)[1].strip()
            elif 'Hand:' in clean_line:
                metadata['hand'] = clean_line.split('Hand:', 1)[1].strip()
            elif 'Subject:' in clean_line:
                metadata['subject'] = clean_line.split('Subject:', 1)[1].strip()
            elif 'Colors:' in clean_line:
                metadata['colors'] = clean_line.split('Colors:', 1)[1].strip()
            elif 'Description:' in clean_line:
                in_description = True
            elif in_description and clean_line:
                description_lines.append(clean_line)
        
        if description_lines:
            metadata['description'] = ' '.join(description_lines)
        
        return metadata
    
    def parse_transcription_line(self, line: str) -> Tuple[str, str]:
        """
        Parse a single transcription line
        Returns (line_id, text)
        """
        # Skip comments and empty lines
        if line.startswith('#') or not line.strip():
            return None, None
        
        # Lines have format: <f17r.P.1;U>  text...
        match = re.match(r'<([^>]+)>\s+(.+)', line)
        if not match:
            return None, None
        
        line_id = match.group(1)
        text = match.group(2)
        
        # We want the 'U' transcription (Unified/standard)
        # or 'F' (First transcriber) if U not available
        if ';U>' not in line and ';F>' not in line:
            return None, None
        
        return line_id, text
    
    def clean_text(self, text: str) -> str:
        """Clean transcription text to standard format"""
        # Remove markup
        text = re.sub(r'\{[^}]+\}', '', text)  # Remove {plant}, {&S}, etc.
        text = re.sub(r'<[^>]+>', '', text)     # Remove <tags>
        text = re.sub(r'\[[^\]]+\]', '', text)  # Remove [notes]
        
        # Remove uncertain character markers
        text = re.sub(r'[!*,]', '', text)       # !, *, , are uncertainty markers
        
        # Remove line continuation markers
        text = text.rstrip('-=')
        
        # Normalize spacing
        text = re.sub(r'\.+', ' ', text)        # Dots are word separators
        text = re.sub(r'\s+', ' ', text)        # Normalize whitespace
        
        return text.strip()
    
    def parse_file(self, file_path: Path) -> Dict:
        """Parse a single transcription file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Extract metadata
        metadata = self.extract_metadata(lines)
        
        # Parse transcription lines
        text_lines = []
        for line in lines:
            line_id, text = self.parse_transcription_line(line)
            if line_id and text:
                cleaned = self.clean_text(text)
                if cleaned:  # Only add non-empty lines
                    text_lines.append(cleaned)
        
        # Combine all text
        full_text = ' '.join(text_lines)
        
        # Extract folio ID from filename (e.g., f017r_tr.txt -> f017r)
        folio_id = file_path.stem.replace('_tr', '')
        
        return {
            'folio_id': folio_id,
            'metadata': metadata,
            'text': full_text,
            'line_count': len(text_lines),
            'source_file': str(file_path)
        }
    
    def parse_quire(self, quire_dir: Path) -> List[Dict]:
        """Parse all transcription files in a quire directory"""
        results = []
        
        transcription_files = sorted(quire_dir.glob('*_tr.txt'))
        
        for file_path in transcription_files:
            try:
                result = self.parse_file(file_path)
                results.append(result)
                print(f"  ✓ Parsed {result['folio_id']}: {result['line_count']} lines, "
                      f"{len(result['text'].split())} words")
            except Exception as e:
                print(f"  ❌ Error parsing {file_path}: {e}")
        
        return results
    
    def save_folio_text(self, folio_data: Dict, output_dir: Path):
        """Save parsed folio as clean text file"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        folio_id = folio_data['folio_id']
        output_file = output_dir / f"{folio_id}.txt"
        
        # Write clean text
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(folio_data['text'])
        
        # Also save metadata as JSON
        metadata_file = output_dir / f"{folio_id}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'folio_id': folio_id,
                'metadata': folio_data['metadata'],
                'line_count': folio_data['line_count'],
                'word_count': len(folio_data['text'].split()),
                'source_file': folio_data['source_file']
            }, f, indent=2)
    
    def process_scraped_data(self, scraped_dir: Path, output_dir: Path):
        """Process all scraped transcription files"""
        print(f"\n{'='*70}")
        print(f"📖 Processing transcription files from {scraped_dir}")
        print(f"{'='*70}\n")
        
        # Process each quire directory
        quire_dirs = sorted([d for d in scraped_dir.iterdir() if d.is_dir()])
        
        all_results = {}
        
        for quire_dir in quire_dirs:
            quire = quire_dir.name
            print(f"\n📂 Processing {quire.upper()}...")
            
            results = self.parse_quire(quire_dir)
            
            if results:
                # Save each folio
                quire_output_dir = output_dir / quire
                for folio_data in results:
                    self.save_folio_text(folio_data, quire_output_dir)
                
                all_results[quire] = results
                print(f"✅ {quire.upper()}: {len(results)} folios processed")
            else:
                print(f"⚠️  {quire.upper()}: No files processed")
        
        # Save summary
        summary = {
            'total_quires': len(all_results),
            'total_folios': sum(len(folios) for folios in all_results.values()),
            'quires': {
                quire: {
                    'folio_count': len(folios),
                    'folios': [f['folio_id'] for f in folios]
                }
                for quire, folios in all_results.items()
            }
        }
        
        summary_file = output_dir / 'parsing_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"✅ PARSING COMPLETE")
        print(f"{'='*70}")
        print(f"Quires processed: {summary['total_quires']}")
        print(f"Folios processed: {summary['total_folios']}")
        print(f"Output directory: {output_dir.absolute()}")
        print(f"Summary: {summary_file}")
        print(f"{'='*70}\n")
        
        return summary


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Parse EVA transcription files into clean folio text',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Parse all scraped transcriptions
  %(prog)s
  
  # Parse from custom scraped directory
  %(prog)s --scraped-dir my_transcriptions
  
  # Parse to custom output directory
  %(prog)s --output-dir data/folios_extended
        '''
    )
    
    parser.add_argument('--scraped-dir', default='data/scraped',
                       help='Directory containing scraped transcription files')
    parser.add_argument('--output-dir', default='data/folios_parsed',
                       help='Output directory for parsed folio text files')
    
    args = parser.parse_args()
    
    scraped_dir = Path(args.scraped_dir)
    output_dir = Path(args.output_dir)
    
    if not scraped_dir.exists():
        print(f"❌ Scraped directory not found: {scraped_dir}")
        print(f"💡 Run scrape_voynich_nu.py first to download transcriptions")
        return
    
    parser_obj = TranscriptionParser()
    summary = parser_obj.process_scraped_data(scraped_dir, output_dir)
    
    print(f"✨ Ready for translation! Use these folios with translate_folio.py")


if __name__ == "__main__":
    main()

