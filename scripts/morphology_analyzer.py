#!/usr/bin/env python3
"""
Morphological Analyzer
Decomposes words into morphological components and suggests meanings
"""

import argparse
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class MorphologyAnalyzer:
    """Analyze word morphology and decompose compounds"""
    
    def __init__(self, dictionary_path: str = "voynich.yaml",
                 rules_path: str = "vocabulary_rules.yaml"):
        self.dictionary_path = Path(dictionary_path)
        self.rules_path = Path(rules_path)
        self.dictionary = {}
        self.prefixes = {}
        self.suffixes = {}
        self.rules = {}
        
        self.load_dictionary()
        self.load_rules()
    
    def load_dictionary(self):
        """Load existing vocabulary"""
        if not self.dictionary_path.exists():
            print(f"⚠️  Dictionary not found: {self.dictionary_path}")
            return
        
        with open(self.dictionary_path, 'r') as f:
            data = yaml.safe_load(f)
        
        vocab_list = data.get("voynich_decipherment_rules", {}).get("vocab", [])
        for entry in vocab_list:
            word = entry.get("word", "")
            if word:
                self.dictionary[word] = {
                    "latin": entry.get("latin", ""),
                    "description": entry.get("description", "")
                }
        
        print(f"✓ Loaded {len(self.dictionary)} dictionary entries")
    
    def load_rules(self):
        """Load morphological rules"""
        if not self.rules_path.exists():
            print(f"⚠️  Rules not found: {self.rules_path}")
            return
        
        with open(self.rules_path, 'r') as f:
            self.rules = yaml.safe_load(f)
        
        # Extract prefix and suffix patterns
        morpho_rules = self.rules.get("morphological_rules", {})
        self.prefixes = morpho_rules.get("prefixes", {})
        self.suffixes = morpho_rules.get("suffixes", {})
        
        print(f"✓ Loaded {len(self.prefixes)} prefix patterns")
        print(f"✓ Loaded {len(self.suffixes)} suffix patterns")
    
    def find_prefix(self, word: str) -> Optional[Tuple[str, str, Dict]]:
        """Find matching prefix in word"""
        for prefix_name, prefix_data in self.prefixes.items():
            pattern = prefix_data.get("pattern", "")
            if pattern.startswith("^"):
                pattern = pattern[1:]  # Remove ^
            
            # Handle regex-like patterns
            if "(?!" in pattern:
                # Complex pattern like ^d(?!y) - match 'd' not followed by 'y'
                if pattern == "d(?!y)":
                    if word.startswith("d") and not word.startswith("dy"):
                        remainder = word[1:]
                        return ("d", remainder, prefix_data)
            elif "(?!" in pattern or "[" in pattern:
                # Skip complex patterns for now
                continue
            else:
                # Simple pattern
                if word.startswith(pattern):
                    remainder = word[len(pattern):]
                    return (pattern, remainder, prefix_data)
        
        return None
    
    def find_suffix(self, word: str) -> Optional[Tuple[str, str, Dict]]:
        """Find matching suffix in word"""
        for suffix_name, suffix_data in self.suffixes.items():
            pattern = suffix_data.get("pattern", "")
            if pattern.endswith("$"):
                pattern = pattern[:-1]  # Remove $
            
            if word.endswith(pattern):
                remainder = word[:-len(pattern)]
                return (pattern, remainder, suffix_data)
        
        return None
    
    def decompose_word(self, word: str) -> List[Dict]:
        """
        Try to decompose word into morphological components
        Returns list of possible decompositions with confidence scores
        """
        decompositions = []
        
        # Strategy 1: prefix + root + suffix
        prefix_match = self.find_prefix(word)
        if prefix_match:
            prefix, after_prefix, prefix_data = prefix_match
            
            suffix_match = self.find_suffix(after_prefix)
            if suffix_match:
                suffix, root, suffix_data = suffix_match
                
                if root in self.dictionary:
                    # Found full decomposition!
                    decompositions.append({
                        "strategy": "prefix+root+suffix",
                        "components": {
                            "prefix": prefix,
                            "root": root,
                            "suffix": suffix
                        },
                        "meanings": {
                            "prefix": prefix_data.get("description", ""),
                            "root": self.dictionary[root]["latin"],
                            "suffix": suffix_data.get("description", "")
                        },
                        "suggested_latin": self._synthesize_meaning(
                            prefix_data, self.dictionary[root]["latin"], suffix_data
                        ),
                        "confidence": 0.8,
                        "reasoning": f"Decomposed as {prefix}+{root}+{suffix}"
                    })
        
        # Strategy 2: prefix + root (no suffix)
        prefix_match = self.find_prefix(word)
        if prefix_match:
            prefix, remainder, prefix_data = prefix_match
            
            if remainder in self.dictionary:
                decompositions.append({
                    "strategy": "prefix+root",
                    "components": {
                        "prefix": prefix,
                        "root": remainder
                    },
                    "meanings": {
                        "prefix": prefix_data.get("description", ""),
                        "root": self.dictionary[remainder]["latin"]
                    },
                    "suggested_latin": self._synthesize_prefix_root(
                        prefix_data, self.dictionary[remainder]["latin"]
                    ),
                    "confidence": 0.75,
                    "reasoning": f"Decomposed as {prefix}+{remainder}"
                })
        
        # Strategy 3: root + suffix (no prefix)
        suffix_match = self.find_suffix(word)
        if suffix_match:
            suffix, root, suffix_data = suffix_match
            
            if root in self.dictionary:
                decompositions.append({
                    "strategy": "root+suffix",
                    "components": {
                        "root": root,
                        "suffix": suffix
                    },
                    "meanings": {
                        "root": self.dictionary[root]["latin"],
                        "suffix": suffix_data.get("description", "")
                    },
                    "suggested_latin": self._synthesize_root_suffix(
                        self.dictionary[root]["latin"], suffix_data
                    ),
                    "confidence": 0.7,
                    "reasoning": f"Decomposed as {root}+{suffix}"
                })
        
        # Strategy 4: Known root with partial matches
        for known_root in self.dictionary:
            if len(known_root) >= 3 and known_root in word and known_root != word:
                # Root is embedded in word
                decompositions.append({
                    "strategy": "embedded_root",
                    "components": {
                        "contains": known_root
                    },
                    "meanings": {
                        "root": self.dictionary[known_root]["latin"]
                    },
                    "suggested_latin": f"[contains: {self.dictionary[known_root]['latin']}]",
                    "confidence": 0.4,
                    "reasoning": f"Contains known root '{known_root}'"
                })
        
        # Sort by confidence
        decompositions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return decompositions
    
    def _synthesize_meaning(self, prefix_data: Dict, root_latin: str, 
                           suffix_data: Dict) -> str:
        """Synthesize meaning from prefix + root + suffix"""
        prefix_mod = prefix_data.get("meaning_modifier", "")
        suffix_mod = suffix_data.get("meaning_modifier", "")
        
        # Simple synthesis rules
        if "valde" in prefix_mod:
            result = f"valde {root_latin}"
        elif "ex" in prefix_mod:
            result = f"ex {root_latin}"
        elif "hic" in prefix_mod:
            result = f"hic {root_latin}"
        else:
            result = root_latin
        
        # Add suffix modification
        if "movet" in suffix_mod:
            result += " movet"
        elif "est" in suffix_mod or "erat" in suffix_mod:
            result += " est"
        
        return result
    
    def _synthesize_prefix_root(self, prefix_data: Dict, root_latin: str) -> str:
        """Synthesize meaning from prefix + root"""
        latin_addition = prefix_data.get("latin_addition", "")
        if "[base]" in latin_addition:
            return latin_addition.replace("[base]", root_latin)
        return f"{prefix_data.get('meaning_modifier', '')} {root_latin}"
    
    def _synthesize_root_suffix(self, root_latin: str, suffix_data: Dict) -> str:
        """Synthesize meaning from root + suffix"""
        latin_addition = suffix_data.get("latin_addition", "")
        if "[base]" in latin_addition:
            return latin_addition.replace("[base]", root_latin)
        return f"{root_latin} {suffix_data.get('meaning_modifier', '')}"
    
    def analyze_word(self, word: str) -> Dict:
        """Complete analysis of a single word"""
        result = {
            "word": word,
            "length": len(word),
            "in_dictionary": word in self.dictionary,
            "decompositions": []
        }
        
        if word in self.dictionary:
            result["current_translation"] = self.dictionary[word]["latin"]
            result["description"] = self.dictionary[word]["description"]
        else:
            result["decompositions"] = self.decompose_word(word)
        
        return result
    
    def analyze_batch(self, words: List[str]) -> List[Dict]:
        """Analyze multiple words"""
        results = []
        for word in words:
            results.append(self.analyze_word(word))
        return results
    
    def generate_word_family(self, root: str) -> List[Dict]:
        """Generate systematic word family from a known root"""
        if root not in self.dictionary:
            print(f"⚠️  Root '{root}' not in dictionary")
            return []
        
        family = []
        root_latin = self.dictionary[root]["latin"]
        
        # Add prefixes
        for prefix_name, prefix_data in self.prefixes.items():
            pattern = prefix_data.get("pattern", "").replace("^", "").replace("$", "")
            if "(?!" in pattern or "[" in pattern:
                continue  # Skip complex patterns
            
            new_word = pattern + root
            if new_word not in self.dictionary:
                family.append({
                    "word": new_word,
                    "construction": f"{pattern}+{root}",
                    "suggested_latin": self._synthesize_prefix_root(prefix_data, root_latin),
                    "confidence": 0.5,
                    "reasoning": f"Systematic prefix addition to known root '{root}'"
                })
        
        # Add suffixes
        for suffix_name, suffix_data in self.suffixes.items():
            pattern = suffix_data.get("pattern", "").replace("^", "").replace("$", "")
            
            new_word = root + pattern
            if new_word not in self.dictionary:
                family.append({
                    "word": new_word,
                    "construction": f"{root}+{pattern}",
                    "suggested_latin": self._synthesize_root_suffix(root_latin, suffix_data),
                    "confidence": 0.5,
                    "reasoning": f"Systematic suffix addition to known root '{root}'"
                })
        
        return family


def main():
    parser = argparse.ArgumentParser(
        description="Analyze word morphology and suggest decompositions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single word
  %(prog)s --word kokaiin
  
  # Analyze words from file
  %(prog)s --batch-file data/unknown_words.txt
  
  # Generate word family from known root
  %(prog)s --generate-family chol
  
  # Auto-suggest decompositions for top unknowns
  %(prog)s --auto-suggest --min-confidence 0.6
        """
    )
    
    parser.add_argument("--word", help="Analyze single word")
    parser.add_argument("--batch-file", help="File with words to analyze (one per line)")
    parser.add_argument("--generate-family", help="Generate word family from known root")
    parser.add_argument("--auto-suggest", action="store_true",
                       help="Auto-suggest from unknown words in translations")
    parser.add_argument("--min-confidence", type=float, default=0.6,
                       help="Minimum confidence for suggestions (default: 0.6)")
    parser.add_argument("--output", help="Output JSON file")
    
    args = parser.parse_args()
    
    analyzer = MorphologyAnalyzer()
    
    results = []
    
    if args.word:
        # Analyze single word
        result = analyzer.analyze_word(args.word)
        results = [result]
        
        print(f"\n🔍 Analysis: {args.word}")
        print("="*60)
        
        if result["in_dictionary"]:
            print(f"✓ In dictionary: {result['current_translation']}")
            print(f"  Description: {result['description']}")
        else:
            print(f"✗ Not in dictionary")
            
            if result["decompositions"]:
                print(f"\n💡 Possible decompositions ({len(result['decompositions'])}):")
                for i, decomp in enumerate(result["decompositions"][:3], 1):
                    print(f"\n{i}. {decomp['strategy']} (confidence: {decomp['confidence']:.2f})")
                    print(f"   Components: {decomp['components']}")
                    print(f"   Suggested: {decomp['suggested_latin']}")
                    print(f"   Reasoning: {decomp['reasoning']}")
            else:
                print("\n⚠️  No decompositions found")
    
    elif args.batch_file:
        # Analyze from file
        words = Path(args.batch_file).read_text().strip().split('\n')
        results = analyzer.analyze_batch(words)
        print(f"✓ Analyzed {len(results)} words")
    
    elif args.generate_family:
        # Generate word family
        family = analyzer.generate_word_family(args.generate_family)
        print(f"\n✓ Generated {len(family)} systematic variations of '{args.generate_family}'")
        
        for item in family[:10]:
            print(f"  • {item['word']:15s} → {item['suggested_latin']}")
        
        if len(family) > 10:
            print(f"  ... and {len(family)-10} more")
        
        results = family
    
    # Save output
    if args.output and results:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Saved to {output_path}")


if __name__ == "__main__":
    main()

