#!/usr/bin/env python3
"""
Neighbor Tracker - Collocation Analysis for Voynich Dictionary
Analyzes which words commonly appear near each dictionary word

OPTIMIZED: Multithreaded processing for fast analysis
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import argparse
from multiprocessing import Pool, cpu_count
from functools import partial


class NeighborTracker:
    """Tracks word collocations and neighbors for dictionary words"""
    
    def __init__(self, dictionary_path: str = 'voynich.yaml', 
                 translations_dir: str = 'data/translations',
                 window_size: int = 2):
        self.dictionary_path = Path(dictionary_path)
        self.translations_dir = Path(translations_dir)
        self.window_size = window_size
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
    
    @staticmethod
    def _process_file(file_path: Path, vocab_set: set, window_size: int = 2, 
                     max_contexts: int = 5, show_progress: bool = True) -> Dict:
        """Process a single file (designed for multiprocessing)"""
        if show_progress:
            print(f"  📄 Processing: {file_path.stem.replace('_translation', '')}")
        
        file_neighbors = defaultdict(lambda: {
            'left_neighbors': Counter(),
            'right_neighbors': Counter(),
            'both_neighbors': Counter(),
            'total_occurrences': 0,
            'contexts': []
        })
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract word sequence
            words = [w['original'] for w in data.get('word_translations', [])]
            
            # Analyze neighbors for each word
            for i, word in enumerate(words):
                if word in vocab_set:
                    file_neighbors[word]['total_occurrences'] += 1
                    
                    # Get left neighbors
                    for j in range(max(0, i-window_size), i):
                        neighbor = words[j]
                        file_neighbors[word]['left_neighbors'][neighbor] += 1
                        file_neighbors[word]['both_neighbors'][neighbor] += 1
                    
                    # Get right neighbors
                    for j in range(i+1, min(len(words), i+window_size+1)):
                        neighbor = words[j]
                        file_neighbors[word]['right_neighbors'][neighbor] += 1
                        file_neighbors[word]['both_neighbors'][neighbor] += 1
                    
                    # Store example context
                    if len(file_neighbors[word]['contexts']) < max_contexts:
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        context = ' '.join(words[start:end])
                        file_neighbors[word]['contexts'].append({
                            'folio': file_path.stem.replace('_translation', ''),
                            'context': context
                        })
            
            return dict(file_neighbors)
            
        except Exception as e:
            print(f"  ⚠️  Error processing {file_path.name}: {e}")
            return {}
    
    def _merge_results(self, results: List[Dict]):
        """Merge results from multiple workers into main storage"""
        for file_result in results:
            for word, data in file_result.items():
                # Merge occurrences
                self.word_neighbors[word]['total_occurrences'] += data['total_occurrences']
                
                # Merge neighbor counters
                self.word_neighbors[word]['left_neighbors'].update(data['left_neighbors'])
                self.word_neighbors[word]['right_neighbors'].update(data['right_neighbors'])
                self.word_neighbors[word]['both_neighbors'].update(data['both_neighbors'])
                
                # Merge contexts (up to max_contexts total)
                remaining = 5 - len(self.word_neighbors[word]['contexts'])
                if remaining > 0:
                    self.word_neighbors[word]['contexts'].extend(data['contexts'][:remaining])
    
    def analyze_all_folios(self, max_contexts: int = 5, 
                          num_workers: int = None, show_progress: bool = True):
        """Analyze all translation files for word neighbors using multiprocessing
        
        Args:
            max_contexts: Maximum example contexts per word
            num_workers: Number of worker processes (None = auto-detect CPUs)
            show_progress: Show per-file progress logs
        """
        if num_workers is None:
            num_workers = cpu_count()
        
        # Get all translation files
        files = sorted(self.translations_dir.glob('*.json'))
        
        if not files:
            print("  ❌ No translation files found!")
            return
        
        print(f"📊 Analyzing word neighbors")
        print(f"   Window size: ±{self.window_size} words")
        print(f"   Workers: {num_workers} (CPU cores: {cpu_count()})")
        print(f"   Files to process: {len(files)}")
        print()
        
        # Create partial function with fixed parameters
        process_func = partial(
            NeighborTracker._process_file,
            vocab_set=self.vocab_set,
            window_size=self.window_size,
            max_contexts=max_contexts,
            show_progress=show_progress
        )
        
        # Process files in parallel
        if num_workers > 1 and len(files) > 1:
            print(f"🚀 Starting parallel processing with {num_workers} workers...")
            print()
            with Pool(processes=num_workers) as pool:
                results = pool.map(process_func, files)
            print()
            print(f"✓ Parallel processing complete")
        else:
            # Single-threaded fallback
            print("⚡ Processing files sequentially...")
            print()
            results = [process_func(f) for f in files]
            print()
            print(f"✓ Sequential processing complete")
        
        # Merge all results
        print("🔄 Merging results from all workers...")
        self._merge_results(results)
        
        print(f"✓ Analyzed {len(files)} folios")
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
                'neighbor_window_size': self.window_size,
                'top_neighbors_per_word': top_n
            },
            'word_neighbors': {}
        }
        
        for word in sorted(self.word_neighbors.keys()):
            neighbor_data = self.get_top_neighbors(word, n=top_n)
            output['word_neighbors'][word] = neighbor_data
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
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
    parser = argparse.ArgumentParser(description='Track word neighbors and collocations (MULTITHREADED)')
    parser.add_argument('--word', type=str, help='Analyze specific word')
    parser.add_argument('--top-n', type=int, default=10, help='Number of top neighbors to show')
    parser.add_argument('--export', type=str, help='Export all neighbor data to JSON file')
    parser.add_argument('--window-size', type=int, default=2, help='Neighbor window size (default: 2)')
    parser.add_argument('--summary', action='store_true', help='Show summary statistics')
    parser.add_argument('--workers', type=int, default=None, 
                       help=f'Number of worker processes (default: auto-detect, max: {cpu_count()})')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress per-file progress logs')
    
    args = parser.parse_args()
    
    # Initialize tracker with window size
    print("🔧 Initializing neighbor tracker...")
    tracker = NeighborTracker(window_size=args.window_size)
    print(f"✓ Loaded dictionary: {len(tracker.vocab)} words")
    print()
    
    # Analyze all folios (MULTITHREADED)
    tracker.analyze_all_folios(
        num_workers=args.workers,
        show_progress=not args.quiet
    )
    
    # Perform requested action
    if args.word:
        tracker.print_word_neighbors(args.word, n=args.top_n)
    
    if args.export:
        tracker.export_neighbor_data(args.export, top_n=args.top_n)
    
    if args.summary or (not args.word and not args.export):
        tracker.generate_summary_report()


if __name__ == '__main__':
    main()
