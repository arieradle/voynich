#!/usr/bin/env python3
"""
Fast Neighbor-Enhanced Word Analysis
Uses neighbor_query.py for fast lookups with multithreading
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

def query_neighbors_for_word(unknown_word: str) -> Dict:
    """Fast query using neighbor_query.py"""
    try:
        result = subprocess.run(
            ['python', 'scripts/neighbor_query.py', '--find-with', unknown_word, '--direction', 'both'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return {'word': unknown_word, 'neighbors': [], 'error': result.stderr}
        
        # Parse output
        neighbors = []
        lines = result.stdout.split('\n')
        
        in_results = False
        for line in lines:
            if 'Found' in line and 'words' in line:
                in_results = True
                continue
            
            if in_results and line.strip():
                # Parse line like: "  chol                 (pars                ) 144x / 544 total"
                match = re.match(r'\s+(\S+)\s+\(([^)]+)\)\s+(\d+)x\s+/\s+(\d+)\s+total', line)
                if match:
                    neighbors.append({
                        'word': match.group(1),
                        'latin': match.group(2).strip(),
                        'count': int(match.group(3)),
                        'total': int(match.group(4))
                    })
        
        return {
            'word': unknown_word,
            'neighbors': neighbors,
            'neighbor_count': len(neighbors)
        }
    
    except subprocess.TimeoutExpired:
        return {'word': unknown_word, 'neighbors': [], 'error': 'timeout'}
    except Exception as e:
        return {'word': unknown_word, 'neighbors': [], 'error': str(e)}

def load_dictionary() -> Dict[str, str]:
    """Load dictionary word->latin mapping"""
    import yaml
    with open('voynich.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    word_map = {}
    for entry in data['voynich_decipherment_rules']['vocab']:
        word_map[entry['word']] = entry['latin']
    return word_map

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
    common_prefixes = ['qo', 'ot', 'sh', 'ch', 'dy', 'ct', 'ok', 'che', 'cth']
    for prefix in common_prefixes:
        if unknown.startswith(prefix):
            neighbor_with_prefix = [n for n in known_neighbors if n.startswith(prefix)]
            if len(neighbor_with_prefix) >= 2:
                patterns.append({
                    'type': 'prefix',
                    'pattern': prefix,
                    'support': len(neighbor_with_prefix),
                    'examples': neighbor_with_prefix[:3]
                })
    
    # Check for shared suffixes
    common_suffixes = ['aiin', 'ain', 'edy', 'ody', 'ar', 'or', 'ol', 'al', 'y', 'eol']
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

def analyze_word_with_neighbors(word: str, dictionary: Dict) -> Dict:
    """Analyze a word using neighbor patterns"""
    
    # Fast query
    neighbor_data = query_neighbors_for_word(word)
    
    if 'error' in neighbor_data:
        return {
            'word': word,
            'pattern_strength': 0.0,
            'confidence_boost': 0.0,
            'neighbor_count': 0,
            'error': neighbor_data['error']
        }
    
    neighbors = neighbor_data['neighbors']
    
    if not neighbors:
        return {
            'word': word,
            'pattern_strength': 0.0,
            'confidence_boost': 0.0,
            'neighbor_count': 0,
            'known_neighbors': [],
            'semantic_hints': [],
            'morphological_clues': []
        }
    
    # Calculate pattern strength
    total_collocations = sum(n['count'] for n in neighbors)
    max_collocation = max(n['count'] for n in neighbors)
    avg_collocation = total_collocations / len(neighbors) if neighbors else 0
    
    strength = min(1.0, (
        (len(neighbors) / 20) * 0.3 +      # More neighbors = stronger
        (max_collocation / 20) * 0.4 +     # Strong max = clearer pattern
        (avg_collocation / 5) * 0.3        # Good average = consistent
    ))
    
    # Confidence boost
    if strength > 0.7:
        boost = 0.20
    elif strength > 0.5:
        boost = 0.15
    elif strength > 0.3:
        boost = 0.10
    else:
        boost = 0.05
    
    # Semantic analysis
    latin_words = [n['latin'] for n in neighbors[:10]]
    semantic_hints = categorize_semantic_field(latin_words)
    
    # Morphological analysis
    known_words = [n['word'] for n in neighbors[:15]]
    morph_clues = find_morphological_patterns(word, known_words, dictionary)
    
    # Additional boosts
    if len(semantic_hints) >= 2:
        boost += 0.05
    if len(morph_clues) >= 2:
        boost += 0.05
    
    return {
        'word': word,
        'pattern_strength': round(strength, 3),
        'confidence_boost': round(boost, 2),
        'neighbor_count': len(neighbors),
        'known_neighbors': neighbors[:10],
        'semantic_hints': semantic_hints,
        'morphological_clues': morph_clues
    }

def analyze_words_parallel(words: List[str], dictionary: Dict, max_workers: int = 8) -> List[Dict]:
    """Analyze multiple words in parallel"""
    
    print(f"⚡ Analyzing {len(words)} words with {max_workers} workers...")
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(analyze_word_with_neighbors, word, dictionary): word 
                  for word in words}
        
        for i, future in enumerate(as_completed(futures), 1):
            word = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"  ✓ [{i}/{len(words)}] {word}")
            except Exception as e:
                print(f"  ✗ [{i}/{len(words)}] {word}: {e}")
                results.append({
                    'word': word,
                    'error': str(e),
                    'pattern_strength': 0.0,
                    'confidence_boost': 0.0
                })
    
    # Sort by pattern strength
    results.sort(key=lambda x: x.get('pattern_strength', 0), reverse=True)
    return results

def print_analysis_report(analysis: Dict):
    """Print formatted analysis report"""
    
    print(f"\n{'='*70}")
    print(f"🔍 NEIGHBOR-ENHANCED ANALYSIS: {analysis['word']}")
    print(f"{'='*70}\n")
    
    if 'error' in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    print(f"📊 Pattern Strength: {analysis['pattern_strength']:.3f}")
    print(f"⬆️  Confidence Boost: +{analysis['confidence_boost']:.2f}")
    print(f"👥 Known Neighbors: {analysis['neighbor_count']}")
    
    if analysis.get('semantic_hints'):
        print(f"\n🎯 Semantic Field(s): {', '.join(analysis['semantic_hints'])}")
    
    if analysis.get('morphological_clues'):
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
    
    if analysis.get('known_neighbors'):
        print(f"\n🔗 Top Collocations:")
        for i, n in enumerate(analysis['known_neighbors'][:5], 1):
            print(f"   {i}. {n['word']} ({n['latin']}) - {n['count']}x / {n['total']} total")
    
    print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fast neighbor-enhanced analysis')
    parser.add_argument('--word', help='Analyze specific word')
    parser.add_argument('--words', nargs='+', help='Analyze multiple words')
    parser.add_argument('--top', type=int, help='Analyze top N from frequency file')
    parser.add_argument('--workers', type=int, default=8, help='Number of parallel workers')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    # Load dictionary
    print("✓ Loading dictionary...")
    dictionary = load_dictionary()
    
    # Analyze
    if args.word:
        result = analyze_word_with_neighbors(args.word, dictionary)
        print_analysis_report(result)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
    
    elif args.words:
        results = analyze_words_parallel(args.words, dictionary, args.workers)
        
        print(f"\n{'='*70}")
        print("📊 SUMMARY")
        print(f"{'='*70}\n")
        
        for result in results:
            print_analysis_report(result)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
    
    elif args.top:
        freq_file = 'data/iterations/word_frequency.json'
        if not Path(freq_file).exists():
            print(f"❌ Frequency file not found: {freq_file}")
            print("   Run: python scripts/word_frequency.py --min-freq 8 --format json")
            sys.exit(1)
        
        with open(freq_file, 'r', encoding='utf-8') as f:
            freq_data = json.load(f)
        
        top_words = [w['word'] for w in freq_data[:args.top]]
        results = analyze_words_parallel(top_words, dictionary, args.workers)
        
        print(f"\n{'='*70}")
        print("📊 SUMMARY - TOP CANDIDATES BY NEIGHBOR STRENGTH")
        print(f"{'='*70}\n")
        
        for result in results:
            print_analysis_report(result)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
    
    else:
        print("❌ Please specify --word, --words, or --top")
        sys.exit(1)

if __name__ == '__main__':
    main()

