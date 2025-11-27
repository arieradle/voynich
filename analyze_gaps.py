#!/usr/bin/env python3
"""
Analyze translation gaps and suggest dictionary updates
"""

import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set
from translator import VoynichTranslator


class GapAnalyzer:
    """Analyze unknown words and suggest dictionary entries"""
    
    def __init__(self, translations_dir: str = "data/translations"):
        self.translations_dir = Path(translations_dir)
        self.translator = VoynichTranslator()
        self.all_translations = []
        self.unknown_words = Counter()
        self.unknown_by_section = defaultdict(list)
        self.context_patterns = defaultdict(list)
    
    def load_translations(self):
        """Load all translation files"""
        print("📂 Loading translations...")
        
        if not self.translations_dir.exists():
            print(f"❌ Translations directory not found: {self.translations_dir}")
            return
        
        for file_path in self.translations_dir.glob("*_translation.json"):
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.all_translations.append(data)
                
                # Collect unknown words
                for word in data.get("unknown_words", []):
                    self.unknown_words[word] += 1
                    self.unknown_by_section[data["section"]].append(word)
                    self.context_patterns[data["context"]].append(word)
        
        print(f"✓ Loaded {len(self.all_translations)} translations")
    
    def analyze_unknown_words(self, min_frequency: int = 2) -> List[Dict]:
        """Analyze unknown words and rank by importance"""
        print(f"\n🔍 Analyzing unknown words (min frequency: {min_frequency})")
        
        candidates = []
        
        for word, freq in self.unknown_words.most_common():
            if freq < min_frequency:
                continue
            
            # Find which sections this word appears in
            sections = []
            contexts = []
            
            for trans in self.all_translations:
                if word in trans.get("unknown_words", []):
                    if trans["section"] not in sections:
                        sections.append(trans["section"])
                    if trans["context"] not in contexts:
                        contexts.append(trans["context"])
            
            # Analyze word structure
            analysis = self._analyze_word_structure(word)
            
            candidates.append({
                "word": word,
                "frequency": freq,
                "sections": sections,
                "contexts": contexts,
                "analysis": analysis,
                "priority": self._calculate_priority(freq, len(sections), analysis)
            })
        
        # Sort by priority
        candidates.sort(key=lambda x: x["priority"], reverse=True)
        
        return candidates
    
    def _analyze_word_structure(self, word: str) -> Dict:
        """Analyze word structure for clues"""
        analysis = {
            "length": len(word),
            "has_qo_prefix": word.startswith("qo"),
            "has_ch": "ch" in word,
            "has_y_suffix": word.endswith("y"),
            "has_aiin": "aiin" in word,
            "has_edy_suffix": word.endswith("edy"),
        }
        
        # Check for known roots
        roots = []
        for vocab_word in self.translator.vocab.keys():
            if len(vocab_word) >= 3 and vocab_word in word and vocab_word != word:
                roots.append(vocab_word)
        
        analysis["possible_roots"] = roots
        
        return analysis
    
    def _calculate_priority(self, frequency: int, section_count: int, analysis: Dict) -> float:
        """Calculate priority score for word"""
        score = 0.0
        
        # Frequency is most important
        score += frequency * 10
        
        # Words appearing in multiple sections are more important
        score += section_count * 5
        
        # Structural bonuses
        if analysis["has_qo_prefix"]:
            score += 3  # Likely a verb
        if analysis["has_edy_suffix"]:
            score += 3  # Likely a verb
        if analysis["possible_roots"]:
            score += 2  # Likely a compound
        
        return score
    
    def generate_suggestions(self, candidates: List[Dict], max_suggestions: int = 20) -> List[Dict]:
        """Generate dictionary entry suggestions"""
        print(f"\n💡 Generating suggestions (top {max_suggestions})...")
        
        suggestions = []
        
        for candidate in candidates[:max_suggestions]:
            word = candidate["word"]
            freq = candidate["frequency"]
            sections = candidate["sections"]
            contexts = candidate["contexts"]
            analysis = candidate["analysis"]
            
            suggestion = {
                "word": word,
                "frequency": freq,
                "suggested_latin": self._suggest_latin(word, analysis, contexts),
                "suggested_contexts": contexts,
                "reasoning": self._generate_reasoning(word, analysis, sections, freq),
                "confidence": "low"  # All suggestions start with low confidence
            }
            
            suggestions.append(suggestion)
        
        return suggestions
    
    def _suggest_latin(self, word: str, analysis: Dict, contexts: List[str]) -> str:
        """Suggest possible Latin translation"""
        # This is where we'd use heuristics or patterns
        # For now, provide placeholder based on structure
        
        if analysis["has_qo_prefix"]:
            base = word[2:]
            if base in self.translator.vocab:
                return f"valde {self.translator.vocab[base]['latin']}"
            return f"[verb: {word}]"
        
        if analysis["has_edy_suffix"]:
            return f"[verb: {word}]"
        
        if analysis["possible_roots"]:
            return f"[compound of: {', '.join(analysis['possible_roots'])}]"
        
        # Context-based guesses
        if "herbal" in contexts:
            return "[plant-related]"
        elif "astronomical" in contexts:
            return "[star-related]"
        elif "biological" in contexts:
            return "[water/body-related]"
        elif "pharmaceutical" in contexts:
            return "[recipe/material-related]"
        
        return "[unknown]"
    
    def _generate_reasoning(self, word: str, analysis: Dict, sections: List[str], freq: int) -> str:
        """Generate human-readable reasoning"""
        reasons = []
        
        reasons.append(f"Appears {freq}x across {len(sections)} section(s): {', '.join(sections)}")
        
        if analysis["has_qo_prefix"]:
            reasons.append("Has 'qo-' prefix → likely intensified verb")
        
        if analysis["has_edy_suffix"]:
            reasons.append("Has '-edy' suffix → likely verb")
        
        if analysis["possible_roots"]:
            reasons.append(f"Contains known roots: {', '.join(analysis['possible_roots'])}")
        
        if analysis["length"] < 4:
            reasons.append("Short word → possibly function word (preposition, article)")
        
        return "; ".join(reasons)
    
    def export_suggestions(self, suggestions: List[Dict], output_file: str = "data/dictionary_suggestions.json"):
        """Export suggestions for review"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(suggestions, f, indent=2)
        
        print(f"\n✓ Suggestions exported to: {output_path}")
    
    def print_report(self, candidates: List[Dict], suggestions: List[Dict]):
        """Print analysis report"""
        print("\n" + "="*60)
        print("📊 GAP ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📈 Overall Statistics:")
        print(f"   • Total translations analyzed: {len(self.all_translations)}")
        print(f"   • Unique unknown words: {len(self.unknown_words)}")
        print(f"   • High-priority candidates: {len(candidates)}")
        
        if self.all_translations:
            avg_coverage = sum(t["statistics"]["coverage"] for t in self.all_translations) / len(self.all_translations)
            print(f"   • Average coverage: {avg_coverage:.1%}")
        
        print(f"\n🎯 Top 10 Unknown Words by Frequency:")
        for i, candidate in enumerate(candidates[:10], 1):
            word = candidate["word"]
            freq = candidate["frequency"]
            sections = ", ".join(candidate["sections"])
            print(f"   {i}. {word:15s} ({freq:3d}x) - {sections}")
        
        print(f"\n💡 Top 5 Suggestions for Dictionary:")
        for i, sug in enumerate(suggestions[:5], 1):
            print(f"\n   {i}. {sug['word']} (appears {sug['frequency']}x)")
            print(f"      Suggested: {sug['suggested_latin']}")
            print(f"      Reasoning: {sug['reasoning']}")
        
        print("\n" + "="*60)
    
    def run_analysis(self, min_frequency: int = 2, max_suggestions: int = 20):
        """Run complete gap analysis"""
        self.load_translations()
        
        if not self.all_translations:
            print("❌ No translations found. Run some translations first.")
            return
        
        candidates = self.analyze_unknown_words(min_frequency)
        suggestions = self.generate_suggestions(candidates, max_suggestions)
        
        self.print_report(candidates, suggestions)
        self.export_suggestions(suggestions)
        
        return candidates, suggestions


def main():
    parser = argparse.ArgumentParser(description="Analyze translation gaps")
    parser.add_argument("--min-freq", type=int, default=2, help="Minimum word frequency")
    parser.add_argument("--max-suggestions", type=int, default=20, help="Max suggestions to generate")
    parser.add_argument("--output", default="data/dictionary_suggestions.json", help="Output file")
    
    args = parser.parse_args()
    
    analyzer = GapAnalyzer()
    analyzer.run_analysis(args.min_freq, args.max_suggestions)


if __name__ == "__main__":
    main()

