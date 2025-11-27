#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes unknown words across all translations and ranks them by priority
"""

import json
import argparse
import csv
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple


class WordFrequencyAnalyzer:
    """Analyze word frequency across translations"""
    
    def __init__(self, translations_dir: str = "data/translations"):
        self.translations_dir = Path(translations_dir)
        self.unknown_words = Counter()
        self.word_by_section = defaultdict(Counter)
        self.word_by_folio = defaultdict(Counter)
        self.word_contexts = defaultdict(set)
        self.translations = []
    
    def load_translations(self, section_filter: str = None):
        """Load translation files"""
        if not self.translations_dir.exists():
            print(f"❌ Translations directory not found: {self.translations_dir}")
            return False
        
        pattern = "*_translation.json"
        if section_filter:
            pattern = f"{section_filter}_*_translation.json"
        
        for file_path in self.translations_dir.glob(pattern):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.translations.append(data)
                    
                    # Extract unknown words
                    unknown = data.get("unknown_words", [])
                    section = data.get("section", "unknown")
                    folio_id = data.get("folio_id", "unknown")
                    context = data.get("context", "unknown")
                    
                    for word in unknown:
                        self.unknown_words[word] += 1
                        self.word_by_section[section][word] += 1
                        self.word_by_folio[folio_id][word] += 1
                        self.word_contexts[word].add(context)
            except Exception as e:
                print(f"⚠️  Error loading {file_path.name}: {e}")
        
        print(f"✓ Loaded {len(self.translations)} translation files")
        print(f"✓ Found {len(self.unknown_words)} unique unknown words")
        return True
    
    def calculate_priority_score(self, word: str, frequency: int) -> float:
        """
        Calculate priority score for a word
        Higher score = higher priority
        """
        score = 0.0
        
        # Frequency is most important (weight: 10)
        score += frequency * 10
        
        # Cross-section appearance (weight: 5 per section)
        num_sections = len([s for s in self.word_by_section if word in self.word_by_section[s]])
        score += num_sections * 5
        
        # Multiple contexts (weight: 3 per context)
        num_contexts = len(self.word_contexts[word])
        score += num_contexts * 3
        
        # Short words bonus (likely function words) (weight: 2)
        if len(word) <= 3:
            score += 2
        
        # Long words penalty (less reliable)
        if len(word) > 10:
            score -= 5
        
        return score
    
    def analyze(self, min_frequency: int = 1) -> List[Dict]:
        """Analyze and rank unknown words"""
        results = []
        
        for word, freq in self.unknown_words.items():
            if freq < min_frequency:
                continue
            
            # Calculate priority
            priority = self.calculate_priority_score(word, freq)
            
            # Collect sections where it appears
            sections = [s for s in self.word_by_section if word in self.word_by_section[s]]
            
            # Collect contexts
            contexts = list(self.word_contexts[word])
            
            results.append({
                "word": word,
                "frequency": freq,
                "priority_score": priority,
                "sections": sections,
                "contexts": contexts,
                "length": len(word)
            })
        
        # Sort by priority score
        results.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return results
    
    def export_json(self, results: List[Dict], output_file: str):
        """Export results as JSON"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Exported to {output_path}")
    
    def export_csv(self, results: List[Dict], output_file: str):
        """Export results as CSV"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'word', 'frequency', 'priority_score', 'sections', 
                'contexts', 'length'
            ])
            writer.writeheader()
            
            for row in results:
                row_copy = row.copy()
                row_copy['sections'] = ','.join(row['sections'])
                row_copy['contexts'] = ','.join(row['contexts'])
                writer.writerow(row_copy)
        
        print(f"✓ Exported to {output_path}")
    
    def export_markdown(self, results: List[Dict], output_file: str):
        """Export results as Markdown"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("# Word Frequency Analysis\n\n")
            f.write(f"**Total unknown words:** {len(self.unknown_words)}\n\n")
            f.write(f"**Words analyzed:** {len(results)}\n\n")
            
            f.write("## Top Unknown Words\n\n")
            f.write("| Rank | Word | Frequency | Priority | Sections | Contexts |\n")
            f.write("|------|------|-----------|----------|----------|----------|\n")
            
            for i, item in enumerate(results[:50], 1):  # Top 50
                sections = ', '.join(item['sections'][:2])
                if len(item['sections']) > 2:
                    sections += f" +{len(item['sections'])-2}"
                contexts = ', '.join(item['contexts'])
                
                f.write(f"| {i} | `{item['word']}` | {item['frequency']} | "
                       f"{item['priority_score']:.1f} | {sections} | {contexts} |\n")
        
        print(f"✓ Exported to {output_path}")
    
    def print_summary(self, results: List[Dict], top_n: int = 20):
        """Print analysis summary"""
        print("\n" + "="*70)
        print("📊 WORD FREQUENCY ANALYSIS")
        print("="*70)
        
        print(f"\n📈 Statistics:")
        print(f"   • Total unique unknown words: {len(self.unknown_words)}")
        print(f"   • Total occurrences: {sum(self.unknown_words.values())}")
        print(f"   • Translations analyzed: {len(self.translations)}")
        
        # Section breakdown
        print(f"\n📚 By Section:")
        for section in sorted(self.word_by_section.keys()):
            count = len(self.word_by_section[section])
            total = sum(self.word_by_section[section].values())
            print(f"   • {section}: {count} unique words ({total} occurrences)")
        
        # Top words
        print(f"\n🎯 Top {top_n} Unknown Words:")
        print(f"\n{'Rank':<6} {'Word':<15} {'Freq':<6} {'Priority':<10} {'Sections'}")
        print("-" * 70)
        
        for i, item in enumerate(results[:top_n], 1):
            sections = ', '.join(item['sections'][:3])
            if len(item['sections']) > 3:
                sections += f" +{len(item['sections'])-3}"
            
            print(f"{i:<6} {item['word']:<15} {item['frequency']:<6} "
                  f"{item['priority_score']:<10.1f} {sections}")
        
        print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze word frequency in translations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all words appearing 5+ times
  %(prog)s --min-freq 5
  
  # Analyze specific section and export to CSV
  %(prog)s --section q01 --format csv --output data/q01_frequency.csv
  
  # Get top 10 priorities in JSON
  %(prog)s --min-freq 10 --top 10 --format json
        """
    )
    
    parser.add_argument("--section", help="Filter by section (q01, q02, etc.)")
    parser.add_argument("--min-freq", type=int, default=3,
                       help="Minimum word frequency (default: 3)")
    parser.add_argument("--top", type=int, default=50,
                       help="Show top N words in summary (default: 50)")
    parser.add_argument("--output", default="data/word_frequency.json",
                       help="Output file path")
    parser.add_argument("--format", choices=['json', 'csv', 'md'],
                       default='json', help="Output format (default: json)")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress summary output")
    
    args = parser.parse_args()
    
    # Run analysis
    analyzer = WordFrequencyAnalyzer()
    
    if not analyzer.load_translations(args.section):
        return 1
    
    results = analyzer.analyze(args.min_freq)
    
    # Export
    if args.format == 'json':
        analyzer.export_json(results, args.output)
    elif args.format == 'csv':
        analyzer.export_csv(results, args.output)
    elif args.format == 'md':
        analyzer.export_markdown(results, args.output)
    
    # Print summary
    if not args.quiet:
        analyzer.print_summary(results, args.top)
    
    return 0


if __name__ == "__main__":
    exit(main())

