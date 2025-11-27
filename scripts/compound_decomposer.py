#!/usr/bin/env python3
"""
Compound Decomposer
Specialized tool for decomposing compound words using multiple strategies
"""

import argparse
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class CompoundDecomposer:
    """Decompose compound words into constituent parts"""
    
    def __init__(self, dictionary_path: str = "voynich.yaml",
                 rules_path: str = "vocabulary_rules.yaml"):
        self.dictionary_path = Path(dictionary_path)
        self.rules_path = Path(rules_path)
        self.dictionary = {}
        self.prefixes = []
        self.suffixes = []
        self.rules = {}
        
        self.load_resources()
    
    def load_resources(self):
        """Load dictionary and rules"""
        # Load dictionary
        if self.dictionary_path.exists():
            with open(self.dictionary_path, 'r') as f:
                data = yaml.safe_load(f)
            
            vocab_list = data.get("voynich_decipherment_rules", {}).get("vocab", [])
            for entry in vocab_list:
                word = entry.get("word", "")
                if word:
                    self.dictionary[word] = entry.get("latin", "")
        
        # Load rules
        if self.rules_path.exists():
            with open(self.rules_path, 'r') as f:
                self.rules = yaml.safe_load(f)
            
            morpho = self.rules.get("morphological_rules", {})
            
            # Extract prefix patterns
            prefix_dict = morpho.get("prefixes", {})
            for name, data in prefix_dict.items():
                pattern = data.get("pattern", "").replace("^", "").replace("$", "")
                if not ("(?!" in pattern or "[" in pattern):
                    self.prefixes.append((pattern, name, data))
            
            # Extract suffix patterns
            suffix_dict = morpho.get("suffixes", {})
            for name, data in suffix_dict.items():
                pattern = data.get("pattern", "").replace("^", "").replace("$", "")
                self.suffixes.append((pattern, name, data))
            
            # Sort by length (longest first for greedy matching)
            self.prefixes.sort(key=lambda x: len(x[0]), reverse=True)
            self.suffixes.sort(key=lambda x: len(x[0]), reverse=True)
        
        print(f"✓ Loaded {len(self.dictionary)} dictionary entries")
        print(f"✓ Loaded {len(self.prefixes)} prefixes, {len(self.suffixes)} suffixes")
    
    def greedy_decompose(self, word: str) -> List[Dict]:
        """Greedy strategy: match longest prefix and suffix first"""
        results = []
        
        # Try each prefix
        for prefix_pattern, prefix_name, prefix_data in self.prefixes:
            if word.startswith(prefix_pattern):
                remainder = word[len(prefix_pattern):]
                
                # Try each suffix on remainder
                for suffix_pattern, suffix_name, suffix_data in self.suffixes:
                    if remainder.endswith(suffix_pattern):
                        root = remainder[:-len(suffix_pattern)]
                        
                        if root and root in self.dictionary:
                            results.append({
                                "strategy": "greedy",
                                "components": {
                                    "prefix": prefix_pattern,
                                    "root": root,
                                    "suffix": suffix_pattern
                                },
                                "translations": {
                                    "prefix": prefix_data.get("meaning_modifier", ""),
                                    "root": self.dictionary[root],
                                    "suffix": suffix_data.get("meaning_modifier", "")
                                },
                                "confidence": 0.7,
                                "full_match": True
                            })
        
        # Try prefix + root (no suffix)
        for prefix_pattern, prefix_name, prefix_data in self.prefixes:
            if word.startswith(prefix_pattern):
                root = word[len(prefix_pattern):]
                if root in self.dictionary:
                    results.append({
                        "strategy": "greedy",
                        "components": {
                            "prefix": prefix_pattern,
                            "root": root
                        },
                        "translations": {
                            "prefix": prefix_data.get("meaning_modifier", ""),
                            "root": self.dictionary[root]
                        },
                        "confidence": 0.6,
                        "full_match": True
                    })
        
        # Try root + suffix (no prefix)
        for suffix_pattern, suffix_name, suffix_data in self.suffixes:
            if word.endswith(suffix_pattern):
                root = word[:-len(suffix_pattern)]
                if root in self.dictionary:
                    results.append({
                        "strategy": "greedy",
                        "components": {
                            "root": root,
                            "suffix": suffix_pattern
                        },
                        "translations": {
                            "root": self.dictionary[root],
                            "suffix": suffix_data.get("meaning_modifier", "")
                        },
                        "confidence": 0.6,
                        "full_match": True
                    })
        
        return results
    
    def exhaustive_decompose(self, word: str) -> List[Dict]:
        """Exhaustive strategy: try all possible splits"""
        results = []
        word_len = len(word)
        
        # Try all possible three-way splits
        for i in range(1, word_len):
            for j in range(i+1, word_len):
                part1 = word[:i]
                part2 = word[i:j]
                part3 = word[j:]
                
                # Check if part2 is a known root
                if part2 in self.dictionary:
                    # Check if part1 could be a prefix
                    is_prefix = any(part1 == p[0] for p in self.prefixes)
                    # Check if part3 could be a suffix
                    is_suffix = any(part3 == s[0] for s in self.suffixes)
                    
                    if is_prefix and is_suffix:
                        confidence = 0.5
                    elif is_prefix or is_suffix:
                        confidence = 0.4
                    else:
                        confidence = 0.3
                    
                    results.append({
                        "strategy": "exhaustive",
                        "components": {
                            "part1": part1,
                            "root": part2,
                            "part3": part3
                        },
                        "translations": {
                            "root": self.dictionary[part2]
                        },
                        "confidence": confidence,
                        "full_match": True
                    })
        
        # Try two-way splits
        for i in range(1, word_len):
            part1 = word[:i]
            part2 = word[i:]
            
            if part1 in self.dictionary:
                results.append({
                    "strategy": "exhaustive",
                    "components": {
                        "root1": part1,
                        "part2": part2
                    },
                    "translations": {
                        "root1": self.dictionary[part1]
                    },
                    "confidence": 0.3,
                    "full_match": False
                })
            
            if part2 in self.dictionary:
                results.append({
                    "strategy": "exhaustive",
                    "components": {
                        "part1": part1,
                        "root2": part2
                    },
                    "translations": {
                        "root2": self.dictionary[part2]
                    },
                    "confidence": 0.3,
                    "full_match": False
                })
        
        return results
    
    def heuristic_decompose(self, word: str) -> List[Dict]:
        """Heuristic strategy: use linguistic rules and patterns"""
        results = []
        
        # Heuristic 1: qo- prefix is very common
        if word.startswith("qo"):
            remainder = word[2:]
            if remainder in self.dictionary:
                results.append({
                    "strategy": "heuristic",
                    "components": {
                        "prefix": "qo",
                        "root": remainder
                    },
                    "translations": {
                        "prefix": "valde",
                        "root": self.dictionary[remainder]
                    },
                    "confidence": 0.8,
                    "full_match": True,
                    "rule": "qo-intensifier"
                })
        
        # Heuristic 2: -aiin suffix is very common
        if word.endswith("aiin"):
            root = word[:-4]
            if root in self.dictionary:
                results.append({
                    "strategy": "heuristic",
                    "components": {
                        "root": root,
                        "suffix": "aiin"
                    },
                    "translations": {
                        "root": self.dictionary[root],
                        "suffix": "est/erat"
                    },
                    "confidence": 0.8,
                    "full_match": True,
                    "rule": "aiin-state-marker"
                })
        
        # Heuristic 3: ot- prefix (from/source)
        if word.startswith("ot"):
            remainder = word[2:]
            if remainder in self.dictionary:
                results.append({
                    "strategy": "heuristic",
                    "components": {
                        "prefix": "ot",
                        "root": remainder
                    },
                    "translations": {
                        "prefix": "ex",
                        "root": self.dictionary[remainder]
                    },
                    "confidence": 0.75,
                    "full_match": True,
                    "rule": "ot-source"
                })
        
        # Heuristic 4: Look for embedded known roots (length >= 3)
        for known_root in self.dictionary:
            if len(known_root) >= 3 and known_root in word and known_root != word:
                idx = word.index(known_root)
                before = word[:idx]
                after = word[idx+len(known_root):]
                
                results.append({
                    "strategy": "heuristic",
                    "components": {
                        "before": before if before else None,
                        "root": known_root,
                        "after": after if after else None
                    },
                    "translations": {
                        "root": self.dictionary[known_root]
                    },
                    "confidence": 0.4,
                    "full_match": bool(before or after),
                    "rule": "embedded-root"
                })
        
        return results
    
    def decompose(self, word: str, strategy: str = "all") -> List[Dict]:
        """Decompose word using specified strategy"""
        results = []
        
        if strategy in ["all", "greedy"]:
            results.extend(self.greedy_decompose(word))
        
        if strategy in ["all", "exhaustive"]:
            results.extend(self.exhaustive_decompose(word))
        
        if strategy in ["all", "heuristic"]:
            results.extend(self.heuristic_decompose(word))
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique_results = []
        for r in results:
            key = str(r.get("components", {}))
            if key not in seen:
                seen.add(key)
                unique_results.append(r)
        
        unique_results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return unique_results
    
    def suggest_translation(self, decomposition: Dict) -> str:
        """Suggest Latin translation from decomposition"""
        components = decomposition.get("components", {})
        translations = decomposition.get("translations", {})
        
        parts = []
        
        if "prefix" in components:
            parts.append(translations.get("prefix", components["prefix"]))
        
        if "root" in components:
            parts.append(translations.get("root", components["root"]))
        elif "root1" in components:
            parts.append(translations.get("root1", components["root1"]))
        elif "root2" in components:
            parts.append(translations.get("root2", components["root2"]))
        
        if "suffix" in components:
            parts.append(translations.get("suffix", components["suffix"]))
        
        return " ".join(p for p in parts if p)


def main():
    parser = argparse.ArgumentParser(
        description="Decompose compound words",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Decompose single word with all strategies
  %(prog)s --word kokaiin
  
  # Use specific strategy
  %(prog)s --word qotchedy --strategy heuristic
  
  # Batch mode from file
  %(prog)s --batch-file unknowns.txt --output decompositions.json
        """
    )
    
    parser.add_argument("--word", help="Single word to decompose")
    parser.add_argument("--batch-file", help="File with words (one per line)")
    parser.add_argument("--strategy", 
                       choices=['greedy', 'exhaustive', 'heuristic', 'all'],
                       default='all',
                       help="Decomposition strategy")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--min-confidence", type=float, default=0.0,
                       help="Minimum confidence threshold")
    
    args = parser.parse_args()
    
    decomposer = CompoundDecomposer()
    
    results = []
    
    if args.word:
        decompositions = decomposer.decompose(args.word, args.strategy)
        
        print(f"\n🔍 Decomposing: {args.word}")
        print("="*70)
        
        if decompositions:
            for i, decomp in enumerate(decompositions, 1):
                if decomp.get("confidence", 0) >= args.min_confidence:
                    print(f"\n{i}. Strategy: {decomp['strategy']} "
                          f"(confidence: {decomp['confidence']:.2f})")
                    print(f"   Components: {decomp['components']}")
                    print(f"   Translation: {decomposer.suggest_translation(decomp)}")
        else:
            print("\n⚠️  No decompositions found")
        
        results = [{"word": args.word, "decompositions": decompositions}]
    
    elif args.batch_file:
        words = Path(args.batch_file).read_text().strip().split('\n')
        
        for word in words:
            word = word.strip()
            if word:
                decompositions = decomposer.decompose(word, args.strategy)
                filtered = [d for d in decompositions 
                           if d.get("confidence", 0) >= args.min_confidence]
                results.append({
                    "word": word,
                    "decompositions": filtered
                })
        
        print(f"✓ Processed {len(results)} words")
    
    # Save output
    if args.output and results:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Saved to {output_path}")


if __name__ == "__main__":
    main()

