#!/usr/bin/env python3
"""
Neighbor-Enhanced Word Analysis
Uses neighbor database to boost confidence scores and validate proposals
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

def load_neighbor_db(path: str = "data/word_neighbors.json") -> Dict:
    """Load neighbor database"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_dictionary(path: str = "voynich.yaml") -> Dict[str, str]:
    """Load dictionary word->latin mapping"""
    import yaml
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    word_map = {}
    for entry in data['voynich_decipherment_rules']['vocab']:
        word_map[entry['word']] = entry['latin']
    return word_map

def analyze_unknown_with_neighbors(unknown_word: str, neighbor_db: Dict, 
                                   dictionary: Dict[str, str]) -> Dict:
    """
    Analyze an unknown word using neighbor patterns
    
    Returns enhanced analysis with:
    - Known neighbors and their frequencies
    - Pattern strength score
    - Semantic cluster hints
    - Confidence boost calculation
    """
    
    result = {
        'word': unknown_word,
        'neighbor_count': 0,
        'known_neighbors': [],
        'pattern_strength': 0.0,
        'confidence_boost': 0.0,
        'semantic_hints': [],
        'morphological_clues': []
    }
    
    # Find all words that have this unknown as a neighbor
    neighbors_with_unknown = []
    
    for known_word, data in neighbor_db.items():
        # Check left neighbors
        for neighbor, count in data.get('top_left_neighbors', []):
            if neighbor == unknown_word:
                neighbors_with_unknown.append({
                    'known_word': known_word,
                    'latin': data['latin'],
                    'count': count,
                    'direction': 'left',
                    'total_occurrences': data['occurrences']
                })
        
        # Check right neighbors
        for neighbor, count in data.get('top_right_neighbors', []):
            if neighbor == unknown_word:
                neighbors_with_unknown.append({
                    'known_word': known_word,
                    'latin': data['latin'],
                    'count': count,
                    'direction': 'right',
                    'total_occurrences': data['occurrences']
                })
    
    if not neighbors_with_unknown:
        return result
    
    # Sort by collocation strength
    neighbors_with_unknown.sort(key=lambda x: x['count'], reverse=True)
    
    result['neighbor_count'] = len(neighbors_with_unknown)
    result['known_neighbors'] = neighbors_with_unknown[:10]  # Top 10
    
    # Calculate pattern strength (0.0-1.0)
    # Based on: number of collocations, max frequency, consistency
    total_collocations = sum(n['count'] for n in neighbors_with_unknown)
    max_collocation = max(n['count'] for n in neighbors_with_unknown)
    avg_collocation = total_collocations / len(neighbors_with_unknown)
    
    # Pattern strength = weighted combination
    strength = min(1.0, (
        (len(neighbors_with_unknown) / 10) * 0.3 +  # More neighbors = stronger
        (max_collocation / 20) * 0.4 +               # Strong max = clearer pattern
        (avg_collocation / 5) * 0.3                  # Good average = consistent
    ))
    result['pattern_strength'] = round(strength, 3)
    
    # Confidence boost calculation
    # Strong neighbor patterns boost confidence by 0.1-0.2
    if strength > 0.7:
        boost = 0.20
    elif strength > 0.5:
        boost = 0.15
    elif strength > 0.3:
        boost = 0.10
    else:
        boost = 0.05
    
    result['confidence_boost'] = boost
    
    # Extract semantic hints from Latin translations
    latin_words = [n['latin'] for n in neighbors_with_unknown[:5]]
    semantic_categories = categorize_semantic_field(latin_words)
    result['semantic_hints'] = semantic_categories
    
    # Extract morphological clues
    known_words = [n['known_word'] for n in neighbors_with_unknown[:10]]
    morph_patterns = find_morphological_patterns(unknown_word, known_words, dictionary)
    result['morphological_clues'] = morph_patterns
    
    return result

def categorize_semantic_field(latin_words: List[str]) -> List[str]:
    """Categorize Latin words into semantic fields"""
    
    semantic_fields = {
        'botanical': ['herba', 'planta', 'folium', 'caulis', 'ramus', 'flos', 
                     'radix', 'fructus', 'semen', 'folia', 'pars'],
        'location': ['hic', 'locus', 'ad', 'in', 'ex', 'circa', 'sub', 'super'],
        'action': ['facit', 'movet', 'crescit', 'producit', 'extendit', 'dat', 
                  'tangit', 'volvit'],
        'state': ['est', 'erat', 'ponit', 'continet'],
        'quality': ['magnus', 'parvus', 'altus', 'robur', 'valde'],
        'earth': ['terra', 'terrae', 'humus'],
        'celestial': ['caelum', 'stella', 'luna', 'sol']
    }
    
    categories = []
    for category, keywords in semantic_fields.items():
        for latin in latin_words:
            if any(kw in latin.lower() for kw in keywords):
                if category not in categories:
                    categories.append(category)
                break
    
    return categories

def find_morphological_patterns(unknown: str, known_neighbors: List[str], 
                                dictionary: Dict[str, str]) -> List[Dict]:
    """Find morphological patterns from neighbor words"""
    
    patterns = []
    
    # Check for shared prefixes
    common_prefixes = ['qo', 'ot', 'sh', 'ch', 'dy', 'ct', 'ok']
    for prefix in common_prefixes:
        if unknown.startswith(prefix):
            # Count how many neighbors also have this prefix
            neighbor_with_prefix = [n for n in known_neighbors if n.startswith(prefix)]
            if len(neighbor_with_prefix) >= 2:
                patterns.append({
                    'type': 'prefix',
                    'pattern': prefix,
                    'support': len(neighbor_with_prefix),
                    'examples': neighbor_with_prefix[:3]
                })
    
    # Check for shared suffixes
    common_suffixes = ['aiin', 'ain', 'edy', 'ody', 'ar', 'or', 'ol', 'al', 'y']
    for suffix in common_suffixes:
        if unknown.endswith(suffix):
            neighbor_with_suffix = [n for n in known_neighbors if n.endswith(suffix)]
            if len(neighbor_with_suffix) >= 2:
                patterns.append({
                    'type': 'suffix',
                    'pattern': suffix,
                    'support': len(neighbor_with_suffix),
                    'examples': neighbor_with_suffix[:3]
                })
    
    # Check for word family membership
    # E.g., if unknown = "sheol" and neighbors include "she", "shol", "sho"
    potential_roots = []
    for length in range(2, len(unknown)):
        root = unknown[:length]
        if root in known_neighbors or root in dictionary:
            potential_roots.append(root)
    
    if potential_roots:
        patterns.append({
            'type': 'family',
            'pattern': 'word_family',
            'roots': potential_roots
        })
    
    return patterns

def calculate_enhanced_confidence(base_confidence: float, neighbor_analysis: Dict) -> float:
    """Calculate confidence with neighbor boost"""
    
    boosted = base_confidence + neighbor_analysis['confidence_boost']
    
    # Additional boost for strong semantic clustering
    if len(neighbor_analysis['semantic_hints']) >= 2:
        boosted += 0.05
    
    # Additional boost for morphological support
    if len(neighbor_analysis['morphological_clues']) >= 2:
        boosted += 0.05
    
    # Cap at 0.95 (never 100% certain)
    return min(0.95, boosted)

def analyze_word_list(words: List[str], neighbor_db: Dict, dictionary: Dict) -> List[Dict]:
    """Analyze multiple unknown words with neighbor data"""
    
    results = []
    for word in words:
        analysis = analyze_unknown_with_neighbors(word, neighbor_db, dictionary)
        results.append(analysis)
    
    # Sort by pattern strength
    results.sort(key=lambda x: x['pattern_strength'], reverse=True)
    return results

def print_analysis_report(analysis: Dict):
    """Print formatted analysis report"""
    
    print(f"\n{'='*70}")
    print(f"🔍 NEIGHBOR-ENHANCED ANALYSIS: {analysis['word']}")
    print(f"{'='*70}\n")
    
    print(f"📊 Pattern Strength: {analysis['pattern_strength']:.3f}")
    print(f"⬆️  Confidence Boost: +{analysis['confidence_boost']:.2f}")
    print(f"👥 Known Neighbors: {analysis['neighbor_count']}")
    
    if analysis['semantic_hints']:
        print(f"\n🎯 Semantic Field(s): {', '.join(analysis['semantic_hints'])}")
    
    if analysis['morphological_clues']:
        print(f"\n🔤 Morphological Patterns:")
        for clue in analysis['morphological_clues']:
            if clue['type'] == 'prefix':
                print(f"   • Prefix '{clue['pattern']}' (support: {clue['support']})")
                print(f"     Examples: {', '.join(clue['examples'])}")
            elif clue['type'] == 'suffix':
                print(f"   • Suffix '{clue['pattern']}' (support: {clue['support']})")
                print(f"     Examples: {', '.join(clue['examples'])}")
            elif clue['type'] == 'family':
                print(f"   • Word family roots: {', '.join(clue['roots'])}")
    
    if analysis['known_neighbors']:
        print(f"\n🔗 Top Collocations:")
        for i, n in enumerate(analysis['known_neighbors'][:5], 1):
            direction = "←" if n['direction'] == 'left' else "→"
            print(f"   {i}. {direction} {n['known_word']} ({n['latin']}) - {n['count']}x")
    
    print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Neighbor-enhanced word analysis')
    parser.add_argument('--word', help='Analyze specific unknown word')
    parser.add_argument('--words', nargs='+', help='Analyze multiple words')
    parser.add_argument('--top-unknowns', type=int, help='Analyze top N unknowns from frequency file')
    parser.add_argument('--neighbor-db', default='data/word_neighbors.json', 
                       help='Path to neighbor database')
    parser.add_argument('--dictionary', default='voynich.yaml',
                       help='Path to dictionary')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    # Load data
    print("✓ Loading neighbor database...")
    neighbor_db = load_neighbor_db(args.neighbor_db)
    
    print("✓ Loading dictionary...")
    dictionary = load_dictionary(args.dictionary)
    
    # Analyze
    if args.word:
        analysis = analyze_unknown_with_neighbors(args.word, neighbor_db, dictionary)
        print_analysis_report(analysis)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    elif args.words:
        results = analyze_word_list(args.words, neighbor_db, dictionary)
        for analysis in results:
            print_analysis_report(analysis)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
    
    elif args.top_unknowns:
        # Load from frequency analysis
        freq_file = 'data/iterations/word_frequency.json'
        if Path(freq_file).exists():
            with open(freq_file, 'r', encoding='utf-8') as f:
                freq_data = json.load(f)
            
            top_words = [w['word'] for w in freq_data[:args.top_unknowns]]
            results = analyze_word_list(top_words, neighbor_db, dictionary)
            
            for analysis in results:
                print_analysis_report(analysis)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
    
    else:
        print("❌ Please specify --word, --words, or --top-unknowns")
        sys.exit(1)

if __name__ == '__main__':
    main()

