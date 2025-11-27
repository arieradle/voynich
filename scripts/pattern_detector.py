#!/usr/bin/env python3
"""
Pattern Detector
Finds repeated patterns, formulaic phrases, and word co-occurrences
"""

import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
import re


class PatternDetector:
    """Detect patterns in Voynich text"""
    
    def __init__(self, folios_dir: str = "data/folios",
                 translations_dir: str = "data/translations"):
        self.folios_dir = Path(folios_dir)
        self.translations_dir = Path(translations_dir)
        self.folio_texts = {}
        self.word_sequences = []
        self.word_pairs = Counter()
        self.word_triplets = Counter()
        self.repeated_sequences = Counter()
    
    def load_folios(self, section_filter: str = None):
        """Load folio text files"""
        if not self.folios_dir.exists():
            print(f"❌ Folios directory not found: {self.folios_dir}")
            return False
        
        pattern = "*.txt"
        if section_filter:
            pattern = f"{section_filter}_*.txt"
        
        for file_path in self.folios_dir.glob(pattern):
            if file_path.name == "metadata.json":
                continue
            
            try:
                with open(file_path, 'r') as f:
                    text = f.read()
                    # Extract just the words (skip metadata lines)
                    lines = [line for line in text.split('\n') 
                            if line and not line.startswith('#') 
                            and not line.startswith('<')]
                    words = []
                    for line in lines:
                        words.extend(line.split())
                    
                    folio_id = file_path.stem
                    self.folio_texts[folio_id] = words
            except Exception as e:
                print(f"⚠️  Error loading {file_path.name}: {e}")
        
        print(f"✓ Loaded {len(self.folio_texts)} folio texts")
        return True
    
    def detect_repeated_sequences(self, min_length: int = 2, 
                                  max_length: int = 5,
                                  min_occurrences: int = 3):
        """Find repeated word sequences"""
        print(f"\n🔍 Detecting repeated sequences...")
        
        sequences = Counter()
        
        for folio_id, words in self.folio_texts.items():
            # Extract sequences of various lengths
            for length in range(min_length, max_length + 1):
                for i in range(len(words) - length + 1):
                    sequence = tuple(words[i:i+length])
                    sequences[sequence] += 1
        
        # Filter by minimum occurrences
        self.repeated_sequences = {
            seq: count for seq, count in sequences.items()
            if count >= min_occurrences
        }
        
        print(f"✓ Found {len(self.repeated_sequences)} repeated sequences")
        return self.repeated_sequences
    
    def detect_word_pairs(self, min_occurrences: int = 3):
        """Find common word pairs (bigrams)"""
        print(f"\n🔍 Detecting word pairs...")
        
        for folio_id, words in self.folio_texts.items():
            for i in range(len(words) - 1):
                pair = (words[i], words[i+1])
                self.word_pairs[pair] += 1
        
        # Filter by minimum occurrences
        self.word_pairs = Counter({
            pair: count for pair, count in self.word_pairs.items()
            if count >= min_occurrences
        })
        
        print(f"✓ Found {len(self.word_pairs)} common word pairs")
        return self.word_pairs
    
    def detect_word_triplets(self, min_occurrences: int = 3):
        """Find common word triplets (trigrams)"""
        print(f"\n🔍 Detecting word triplets...")
        
        for folio_id, words in self.folio_texts.items():
            for i in range(len(words) - 2):
                triplet = (words[i], words[i+1], words[i+2])
                self.word_triplets[triplet] += 1
        
        # Filter by minimum occurrences
        self.word_triplets = Counter({
            triplet: count for triplet, count in self.word_triplets.items()
            if count >= min_occurrences
        })
        
        print(f"✓ Found {len(self.word_triplets)} common word triplets")
        return self.word_triplets
    
    def detect_formulaic_phrases(self, min_occurrences: int = 5):
        """
        Detect formulaic phrases (sequences that appear intact multiple times)
        """
        print(f"\n🔍 Detecting formulaic phrases...")
        
        # Look for sequences of 3+ words that repeat exactly
        formulaic = {}
        
        for sequence, count in self.repeated_sequences.items():
            if len(sequence) >= 3 and count >= min_occurrences:
                phrase = ' '.join(sequence)
                formulaic[phrase] = {
                    "sequence": sequence,
                    "count": count,
                    "length": len(sequence),
                    "type": "formulaic"
                }
        
        print(f"✓ Found {len(formulaic)} formulaic phrases")
        return formulaic
    
    def detect_word_co_occurrence(self, target_word: str, 
                                   window_size: int = 5):
        """Find words that frequently appear near target word"""
        print(f"\n🔍 Detecting co-occurrences with '{target_word}'...")
        
        co_occurrences = Counter()
        
        for folio_id, words in self.folio_texts.items():
            for i, word in enumerate(words):
                if word == target_word:
                    # Look at words in window
                    start = max(0, i - window_size)
                    end = min(len(words), i + window_size + 1)
                    
                    for j in range(start, end):
                        if j != i:  # Don't count the target word itself
                            co_occurrences[words[j]] += 1
        
        print(f"✓ Found {len(co_occurrences)} co-occurring words")
        return co_occurrences
    
    def analyze_pattern_distribution(self, pattern: str):
        """Analyze where a pattern appears across folios"""
        distribution = defaultdict(int)
        
        for folio_id, words in self.folio_texts.items():
            # Count occurrences in this folio
            text = ' '.join(words)
            count = text.count(pattern)
            if count > 0:
                distribution[folio_id] = count
        
        return distribution
    
    def detect_statistical_patterns(self):
        """Detect statistical patterns in word usage"""
        print(f"\n🔍 Analyzing statistical patterns...")
        
        stats = {}
        
        # Word length distribution
        lengths = Counter()
        for folio_id, words in self.folio_texts.items():
            for word in words:
                lengths[len(word)] += 1
        
        stats["word_lengths"] = dict(lengths)
        
        # Most common words overall
        all_words = Counter()
        for folio_id, words in self.folio_texts.items():
            all_words.update(words)
        
        stats["most_common_words"] = dict(all_words.most_common(50))
        
        # Starting/ending patterns
        starts = Counter()
        ends = Counter()
        for folio_id, words in self.folio_texts.items():
            for word in words:
                if len(word) >= 2:
                    starts[word[:2]] += 1
                    ends[word[-2:]] += 1
        
        stats["common_starts"] = dict(starts.most_common(20))
        stats["common_ends"] = dict(ends.most_common(20))
        
        print(f"✓ Statistical analysis complete")
        return stats
    
    def generate_report(self) -> Dict:
        """Generate comprehensive pattern report"""
        report = {
            "repeated_sequences": [
                {
                    "sequence": ' '.join(seq),
                    "words": list(seq),
                    "count": count,
                    "length": len(seq)
                }
                for seq, count in sorted(
                    self.repeated_sequences.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:50]
            ],
            "word_pairs": [
                {
                    "pair": f"{pair[0]} {pair[1]}",
                    "words": list(pair),
                    "count": count
                }
                for pair, count in self.word_pairs.most_common(50)
            ],
            "word_triplets": [
                {
                    "triplet": f"{t[0]} {t[1]} {t[2]}",
                    "words": list(t),
                    "count": count
                }
                for t, count in self.word_triplets.most_common(30)
            ]
        }
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description="Detect patterns in Voynich manuscript",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Detect all patterns
  %(prog)s --pattern-type all --min-occurrences 3
  
  # Find formulaic phrases
  %(prog)s --pattern-type formulaic --min-occurrences 5
  
  # Find word pairs in specific section
  %(prog)s --pattern-type pairs --section q01
  
  # Analyze co-occurrences of a word
  %(prog)s --pattern-type cooccurrence --target-word daiin
        """
    )
    
    parser.add_argument("--pattern-type", 
                       choices=['all', 'sequences', 'pairs', 'triplets', 
                               'formulaic', 'cooccurrence', 'statistical'],
                       default='all',
                       help="Type of pattern to detect")
    parser.add_argument("--section", help="Filter by section (q01, q02, etc.)")
    parser.add_argument("--min-occurrences", type=int, default=3,
                       help="Minimum pattern occurrences (default: 3)")
    parser.add_argument("--target-word", help="Target word for co-occurrence analysis")
    parser.add_argument("--output", default="data/patterns_detected.json",
                       help="Output JSON file")
    parser.add_argument("--window-size", type=int, default=5,
                       help="Window size for co-occurrence (default: 5)")
    
    args = parser.parse_args()
    
    detector = PatternDetector()
    
    if not detector.load_folios(args.section):
        return 1
    
    results = {}
    
    if args.pattern_type in ['all', 'sequences']:
        detector.detect_repeated_sequences(min_occurrences=args.min_occurrences)
    
    if args.pattern_type in ['all', 'pairs']:
        detector.detect_word_pairs(min_occurrences=args.min_occurrences)
    
    if args.pattern_type in ['all', 'triplets']:
        detector.detect_word_triplets(min_occurrences=args.min_occurrences)
    
    if args.pattern_type == 'formulaic':
        results['formulaic'] = detector.detect_formulaic_phrases(
            min_occurrences=args.min_occurrences
        )
    
    if args.pattern_type == 'cooccurrence':
        if not args.target_word:
            print("❌ --target-word required for co-occurrence analysis")
            return 1
        results['cooccurrence'] = dict(
            detector.detect_word_co_occurrence(
                args.target_word, args.window_size
            ).most_common(50)
        )
    
    if args.pattern_type in ['all', 'statistical']:
        results['statistical'] = detector.detect_statistical_patterns()
    
    if args.pattern_type == 'all':
        results = detector.generate_report()
        if 'statistical' in results:
            results['statistical'] = detector.detect_statistical_patterns()
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_path}")
    
    # Print summary
    print("\n" + "="*70)
    print("📊 PATTERN DETECTION SUMMARY")
    print("="*70)
    
    if args.pattern_type in ['all', 'sequences']:
        print(f"\n🔁 Repeated sequences: {len(detector.repeated_sequences)}")
        for seq, count in list(detector.repeated_sequences.items())[:5]:
            print(f"   • {' '.join(seq):<40s} ({count}x)")
    
    if args.pattern_type in ['all', 'pairs']:
        print(f"\n👥 Word pairs: {len(detector.word_pairs)}")
        for (w1, w2), count in detector.word_pairs.most_common(5):
            print(f"   • {w1} {w2:<35s} ({count}x)")
    
    if args.pattern_type in ['all', 'triplets']:
        print(f"\n🎯 Word triplets: {len(detector.word_triplets)}")
        for (w1, w2, w3), count in detector.word_triplets.most_common(5):
            print(f"   • {w1} {w2} {w3:<30s} ({count}x)")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

