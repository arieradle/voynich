#!/usr/bin/env python3
"""
Fast Neighbor Query Tool - Quick lookups from neighbor database
Load once, query many times
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional


class NeighborDB:
    """Fast in-memory neighbor database"""
    
    def __init__(self, db_path: str = 'data/word_neighbors.json'):
        self.db_path = Path(db_path)
        self.data = None
        self.metadata = None
        self._load_db()
    
    def _load_db(self):
        """Load neighbor database into memory"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Neighbor database not found: {self.db_path}")
        
        with open(self.db_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        
        self.metadata = full_data['metadata']
        self.data = full_data['word_neighbors']
        print(f"✓ Loaded neighbor DB: {len(self.data)} words")
    
    def get_neighbors(self, word: str, direction: str = 'both', n: int = 10) -> Optional[Dict]:
        """Get top N neighbors for a word
        
        Args:
            word: Target word to query
            direction: 'left', 'right', or 'both'
            n: Number of top neighbors to return
        """
        if word not in self.data:
            return None
        
        word_data = self.data[word]
        
        if direction == 'left':
            neighbors = word_data['top_left_neighbors'][:n]
        elif direction == 'right':
            neighbors = word_data['top_right_neighbors'][:n]
        else:
            neighbors = word_data['top_all_neighbors'][:n]
        
        return {
            'word': word,
            'latin': word_data['latin'],
            'occurrences': word_data['occurrences'],
            'neighbors': neighbors,
            'direction': direction
        }
    
    def find_common_neighbors(self, word1: str, word2: str) -> Dict:
        """Find neighbors that both words share"""
        if word1 not in self.data or word2 not in self.data:
            return {'error': 'One or both words not found'}
        
        neighbors1 = {n[0] for n in self.data[word1]['top_all_neighbors']}
        neighbors2 = {n[0] for n in self.data[word2]['top_all_neighbors']}
        
        common = neighbors1 & neighbors2
        
        return {
            'word1': word1,
            'word2': word2,
            'common_neighbors': sorted(common),
            'count': len(common)
        }
    
    def find_words_with_neighbor(self, target_neighbor: str, min_count: int = 3) -> List[Dict]:
        """Find all words that have target_neighbor appearing nearby
        
        Useful for: "What words commonly appear near 'daiin'?"
        """
        results = []
        
        for word, word_data in self.data.items():
            # Check if target_neighbor appears in this word's neighbors
            for neighbor, count in word_data['top_all_neighbors']:
                if neighbor == target_neighbor and count >= min_count:
                    results.append({
                        'word': word,
                        'latin': word_data['latin'],
                        'neighbor_count': count,
                        'total_occurrences': word_data['occurrences']
                    })
                    break
        
        # Sort by neighbor count descending
        results.sort(key=lambda x: x['neighbor_count'], reverse=True)
        return results
    
    def get_context_patterns(self, word: str) -> List[str]:
        """Get example contexts for a word"""
        if word not in self.data:
            return []
        
        return self.data[word].get('example_contexts', [])
    
    def search_words(self, pattern: str) -> List[str]:
        """Search for words matching a pattern"""
        return [w for w in self.data.keys() if pattern in w]
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            'total_words': len(self.data),
            'total_occurrences': sum(w['occurrences'] for w in self.data.values()),
            'avg_neighbors': sum(len(w['top_all_neighbors']) for w in self.data.values()) / len(self.data),
            'metadata': self.metadata
        }
    
    def analyze_word_relationships(self, word: str) -> Dict:
        """Comprehensive relationship analysis for a word"""
        if word not in self.data:
            return {'error': f'Word "{word}" not found'}
        
        word_data = self.data[word]
        
        # Get all neighbors
        all_neighbors = word_data['top_all_neighbors']
        left_neighbors = word_data['top_left_neighbors']
        right_neighbors = word_data['top_right_neighbors']
        
        # Find words that are ONLY on left or right
        left_only = [n for n in left_neighbors if n not in [r[0] for r in right_neighbors]]
        right_only = [n for n in right_neighbors if n not in [l[0] for l in left_neighbors]]
        
        # Find words that appear on BOTH sides
        both_sides = []
        left_words = {n[0]: n[1] for n in left_neighbors}
        right_words = {n[0]: n[1] for n in right_neighbors}
        for neighbor in left_words:
            if neighbor in right_words:
                both_sides.append((neighbor, left_words[neighbor] + right_words[neighbor]))
        both_sides.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'word': word,
            'latin': word_data['latin'],
            'occurrences': word_data['occurrences'],
            'total_unique_neighbors': len(all_neighbors),
            'left_only': left_only[:5],  # Top 5
            'right_only': right_only[:5],  # Top 5
            'both_sides': both_sides[:5],  # Top 5
            'contexts': word_data['example_contexts']
        }


def main():
    parser = argparse.ArgumentParser(description='Fast neighbor database queries')
    parser.add_argument('--db', type=str, default='data/word_neighbors.json', 
                       help='Path to neighbor database')
    parser.add_argument('--word', type=str, help='Query specific word')
    parser.add_argument('--direction', type=str, choices=['left', 'right', 'both'], 
                       default='both', help='Neighbor direction')
    parser.add_argument('--top-n', type=int, default=10, help='Number of neighbors to show')
    parser.add_argument('--find-with', type=str, 
                       help='Find words that have this neighbor')
    parser.add_argument('--common', nargs=2, metavar=('WORD1', 'WORD2'),
                       help='Find common neighbors between two words')
    parser.add_argument('--analyze', type=str, 
                       help='Comprehensive relationship analysis')
    parser.add_argument('--search', type=str, help='Search for words containing pattern')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    
    args = parser.parse_args()
    
    # Load database
    db = NeighborDB(args.db)
    
    # Execute query
    if args.word:
        result = db.get_neighbors(args.word, args.direction, args.top_n)
        if result:
            print(f"\n{'='*70}")
            print(f"NEIGHBORS: {result['word']} → {result['latin']}")
            print(f"{'='*70}")
            print(f"Occurrences: {result['occurrences']}")
            print(f"Direction: {result['direction']}")
            print(f"\nTop {args.top_n} neighbors:")
            for neighbor, count in result['neighbors']:
                print(f"  {neighbor:20} {count:3}x")
        else:
            print(f"❌ Word '{args.word}' not found in database")
    
    elif args.find_with:
        results = db.find_words_with_neighbor(args.find_with, min_count=3)
        print(f"\n{'='*70}")
        print(f"WORDS WITH NEIGHBOR: {args.find_with}")
        print(f"{'='*70}")
        print(f"Found {len(results)} words\n")
        for r in results[:20]:  # Top 20
            print(f"  {r['word']:20} ({r['latin']:20}) {r['neighbor_count']:3}x / {r['total_occurrences']:3} total")
    
    elif args.common:
        result = db.find_common_neighbors(args.common[0], args.common[1])
        if 'error' not in result:
            print(f"\n{'='*70}")
            print(f"COMMON NEIGHBORS: {result['word1']} & {result['word2']}")
            print(f"{'='*70}")
            print(f"Found {result['count']} common neighbors:\n")
            for neighbor in result['common_neighbors'][:20]:
                print(f"  {neighbor}")
        else:
            print(f"❌ {result['error']}")
    
    elif args.analyze:
        result = db.analyze_word_relationships(args.analyze)
        if 'error' not in result:
            print(f"\n{'='*70}")
            print(f"RELATIONSHIP ANALYSIS: {result['word']} → {result['latin']}")
            print(f"{'='*70}")
            print(f"Occurrences: {result['occurrences']}")
            print(f"Unique neighbors: {result['total_unique_neighbors']}")
            
            print(f"\n📍 LEFT-ONLY neighbors (words before):")
            for neighbor, count in result['left_only'][:5]:
                print(f"  {neighbor:20} {count:3}x")
            
            print(f"\n📍 RIGHT-ONLY neighbors (words after):")
            for neighbor, count in result['right_only'][:5]:
                print(f"  {neighbor:20} {count:3}x")
            
            print(f"\n📍 BOTH SIDES (appear on both sides):")
            for neighbor, count in result['both_sides'][:5]:
                print(f"  {neighbor:20} {count:3}x")
            
            print(f"\n💡 Example contexts:")
            for ctx in result['contexts'][:3]:
                print(f"  [{ctx['folio']}] {ctx['context']}")
        else:
            print(f"❌ {result['error']}")
    
    elif args.search:
        results = db.search_words(args.search)
        print(f"\n{'='*70}")
        print(f"SEARCH: words containing '{args.search}'")
        print(f"{'='*70}")
        print(f"Found {len(results)} words:\n")
        for word in results[:30]:
            data = db.data[word]
            print(f"  {word:20} → {data['latin']:20} ({data['occurrences']}x)")
    
    elif args.stats:
        stats = db.get_stats()
        print(f"\n{'='*70}")
        print("DATABASE STATISTICS")
        print(f"{'='*70}")
        print(f"Total words tracked: {stats['total_words']}")
        print(f"Total occurrences: {stats['total_occurrences']}")
        print(f"Avg neighbors per word: {stats['avg_neighbors']:.1f}")
        print(f"\nMetadata:")
        for key, value in stats['metadata'].items():
            print(f"  {key}: {value}")
    
    else:
        print("Please specify a query. Use --help for options.")


if __name__ == '__main__':
    main()

