#!/usr/bin/env python3
"""
Neighbor Tracker - Collocation Analysis for Voynich Dictionary
Analyzes which words commonly appear near each dictionary word
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import argparse


class NeighborTracker:
    """Tracks word collocations and neighbors for dictionary words"""
    
    def __init__(self, dictionary_path: str = 'voynich.yaml', 
                 translations_dir: str = 'data/translations'):
        self.dictionary_path = Path(dictionary_path)
        self.translations_dir = Path(translations_dir)
        self.vocab = self._load_dictionary()
        self.vocab_set = set(self.vocab.keys())
        
        # Storage for neighbor data
        self.word_neighbors = defaultdict(lambda: {
            'left_neighbors': Counter(),
            'right_neighbors': Counter(),
            'both_neighbors': Counter(),
            'total_occurrences': 0,
            'contexts': []
        })
    
    def _load_dictionary(self) -> Dict[str, dict]:
        """Load dictionary and extract vocabulary"""
        with open(self.dictionary_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        vocab = {}
        for entry in data['voynich_decipherment_rules']['vocab']:
            vocab[entry['word']] = {
                'latin': entry.get('latin', ''),
                'description': entry.get('description', '')
            }
        
        return vocab
    
    def analyze_all_folios(self, window_size: int = 2, max_contexts: int = 5):
        """Analyze all translation files for word neighbors"""
        print(f"📊 Analyzing word neighbors (window size: ±{window_size})...")
        
        folio_count = 0
        for file in sorted(self.translations_dir.glob('*.json')):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract word sequence
                words = [w['original'] for w in data.get('word_translations', [])]
                
                # Analyze neighbors for each word
                for i, word in enumerate(words):
                    if word in self.vocab_set:
                        self.word_neighbors[word]['total_occurrences'] += 1
                        
                        # Get left neighbors
                        for j in range(max(0, i-window_size), i):
                            neighbor = words[j]
                            self.word_neighbors[word]['left_neighbors'][neighbor] += 1
                            self.word_neighbors[word]['both_neighbors'][neighbor] += 1
                        
                        # Get right neighbors
                        for j in range(i+1, min(len(words), i+window_size+1)):
                            neighbor = words[j]
                            self.word_neighbors[word]['right_neighbors'][neighbor] += 1
                            self.word_neighbors[word]['both_neighbors'][neighbor] += 1
                        
                        # Store example context
                        if len(self.word_neighbors[word]['contexts']) < max_contexts:
                            start = max(0, i-2)
                            end = min(len(words), i+3)
                            context = ' '.join(words[start:end])
                            self.word_neighbors[word]['contexts'].append({
                                'folio': file.stem.replace('_translation', ''),
                                'context': context
                            })
                
                folio_count += 1
            except Exception as e:
                print(f"  ⚠️  Error processing {file}: {e}")
        
        print(f"✓ Analyzed {folio_count} folios")
        print(f"✓ Tracked neighbors for {len(self.word_neighbors)} dictionary words")
    
    def get_top_neighbors(self, word: str, n: int = 10) -> Dict:
        """Get top N neighbors for a specific word"""
        if word not in self.word_neighbors:
            return None
        
        data = self.word_neighbors[word]
        
        return {
            'word': word,
            'latin': self.vocab[word]['latin'],
            'occurrences': data['total_occurrences'],
            'top_left_neighbors': data['left_neighbors'].most_common(n),
            'top_right_neighbors': data['right_neighbors'].most_common(n),
            'top_all_neighbors': data['both_neighbors'].most_common(n),
            'example_contexts': data['contexts']
        }
    
    def export_neighbor_data(self, output_file: str, top_n: int = 10):
        """Export neighbor analysis to JSON file"""
        output = {
            'metadata': {
                'total_words_analyzed': len(self.word_neighbors),
                'dictionary_size': len(self.vocab),
                'neighbor_window_size': 2,
                'top_neighbors_per_word': top_n
            },
            'word_neighbors': {}
        }
        
        for word in sorted(self.word_neighbors.keys()):
            neighbor_data = self.get_top_neighbors(word, n=top_n)
            output['word_neighbors'][word] = neighbor_data
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported neighbor data to: {output_file}")
    
    def print_word_neighbors(self, word: str, n: int = 10):
        """Print neighbor analysis for a specific word"""
        data = self.get_top_neighbors(word, n=n)
        
        if not data:
            print(f"❌ Word '{word}' not found in dictionary or has no occurrences")
            return
        
        print(f"\n{'='*70}")
        print(f"NEIGHBOR ANALYSIS: {word} → {data['latin']}")
        print(f"{'='*70}")
        print(f"\nTotal occurrences: {data['occurrences']}")
        
        print(f"\n📍 Top {n} LEFT neighbors (words before '{word}'):")
        for neighbor, count in data['top_left_neighbors']:
            latin = self.vocab.get(neighbor, {}).get('latin', '[unknown]')
            print(f"  {neighbor:20} ({latin:20}) {count:3}x")
        
        print(f"\n📍 Top {n} RIGHT neighbors (words after '{word}'):")
        for neighbor, count in data['top_right_neighbors']:
            latin = self.vocab.get(neighbor, {}).get('latin', '[unknown]')
            print(f"  {neighbor:20} ({latin:20}) {count:3}x")
        
        print(f"\n📍 Top {n} ALL neighbors (both sides):")
        for neighbor, count in data['top_all_neighbors']:
            latin = self.vocab.get(neighbor, {}).get('latin', '[unknown]')
            print(f"  {neighbor:20} ({latin:20}) {count:3}x")
        
        print(f"\n💡 Example contexts:")
        for ctx in data['example_contexts']:
            print(f"  [{ctx['folio']}] {ctx['context']}")
    
    def generate_summary_report(self):
        """Generate summary statistics"""
        print(f"\n{'='*70}")
        print("NEIGHBOR TRACKING SUMMARY")
        print(f"{'='*70}")
        
        total_words_tracked = len(self.word_neighbors)
        total_occurrences = sum(d['total_occurrences'] for d in self.word_neighbors.values())
        
        print(f"\n📊 Statistics:")
        print(f"  Dictionary words: {len(self.vocab)}")
        print(f"  Words with neighbors: {total_words_tracked}")
        print(f"  Total word occurrences: {total_occurrences}")
        print(f"  Coverage: {total_words_tracked/len(self.vocab)*100:.1f}%")
        
        # Find words with most neighbors
        words_by_neighbors = sorted(
            [(w, len(d['both_neighbors'])) for w, d in self.word_neighbors.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        print(f"\n🔝 Top 10 words by unique neighbors:")
        for word, neighbor_count in words_by_neighbors[:10]:
            latin = self.vocab[word]['latin']
            occurrences = self.word_neighbors[word]['total_occurrences']
            print(f"  {word:15} ({latin:15}) {neighbor_count:3} unique neighbors, {occurrences:4}x occurrences")


def main():
    parser = argparse.ArgumentParser(description='Track word neighbors and collocations')
    parser.add_argument('--word', type=str, help='Analyze specific word')
    parser.add_argument('--top-n', type=int, default=10, help='Number of top neighbors to show')
    parser.add_argument('--export', type=str, help='Export all neighbor data to JSON file')
    parser.add_argument('--window-size', type=int, default=2, help='Neighbor window size (default: 2)')
    parser.add_argument('--summary', action='store_true', help='Show summary statistics')
    
    args = parser.parse_args()
    
    # Initialize tracker
    tracker = NeighborTracker()
    
    # Analyze all folios
    tracker.analyze_all_folios(window_size=args.window_size)
    
    # Perform requested action
    if args.word:
        tracker.print_word_neighbors(args.word, n=args.top_n)
    
    if args.export:
        tracker.export_neighbor_data(args.export, top_n=args.top_n)
    
    if args.summary or (not args.word and not args.export):
        tracker.generate_summary_report()


if __name__ == '__main__':
    main()

