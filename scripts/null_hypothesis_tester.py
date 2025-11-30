#!/usr/bin/env python3
"""
Null Hypothesis Testing for Voynich Translation Validation
Compare real translations against random baseline
"""

import json
import random
import re
import math
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import yaml


class NullHypothesisTester:
    """Test if translations are better than random assignment"""
    
    def __init__(self):
        self.translations_dir = Path("data/translations")
        self.vocab_file = Path("voynich.yaml")
        self.vocab = self._load_vocabulary()
        
    def _load_vocabulary(self) -> Dict:
        """Load the Voynich vocabulary"""
        with open(self.vocab_file, 'r') as f:
            data = yaml.safe_load(f)
        
        vocab = {}
        for entry in data['voynich_decipherment_rules']['vocab']:
            vocab[entry['word']] = {
                'latin': entry['latin'],
                'description': entry.get('description', '')
            }
        
        return vocab
    
    def generate_random_decipherment(self, seed: int = 42) -> Dict[str, str]:
        """
        Generate a random word mapping with same frequency distribution
        
        Strategy:
        1. Get frequency distribution of Latin words in real translations
        2. Shuffle assignments to Voynichese words randomly
        3. Maintain frequency distribution (common Voynich → common Latin)
        """
        random.seed(seed)
        
        # Collect frequency data from real translations
        voynich_freq = Counter()
        latin_freq = Counter()
        
        translation_files = list(self.translations_dir.glob("q*.json"))[:20]  # Sample
        
        for filepath in translation_files:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            voynich_words = re.findall(r'\b\w+\b', data.get('voynich_text', '').lower())
            latin_text = re.sub(r'\[[\w\s]+\]', '', data.get('latin_text', ''))
            latin_words = re.findall(r'\b\w+\b', latin_text.lower())
            
            voynich_freq.update(voynich_words)
            latin_freq.update(latin_words)
        
        # Sort by frequency
        sorted_voynich = [word for word, _ in voynich_freq.most_common()]
        sorted_latin = [word for word, _ in latin_freq.most_common()]
        
        # Shuffle Latin words randomly (breaking real associations)
        shuffled_latin = sorted_latin.copy()
        random.shuffle(shuffled_latin)
        
        # Create random mapping (preserve frequency ranking correlation)
        random_vocab = {}
        for i, voynich_word in enumerate(sorted_voynich):
            if i < len(shuffled_latin):
                random_vocab[voynich_word] = shuffled_latin[i]
            else:
                # For rare words, assign random Latin word
                random_vocab[voynich_word] = random.choice(shuffled_latin)
        
        return random_vocab
    
    def translate_with_random_vocab(self, voynich_text: str, 
                                   random_vocab: Dict[str, str]) -> str:
        """Translate using random vocabulary"""
        words = re.findall(r'\b\w+\b', voynich_text.lower())
        
        translated = []
        for word in words:
            if word in random_vocab:
                translated.append(random_vocab[word])
            else:
                translated.append(f"[{word}]")
        
        return " ".join(translated)
    
    def calculate_bigram_coherence(self, text: str) -> float:
        """
        Calculate bigram coherence score
        Higher score = more natural word transitions
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        if len(words) < 2:
            return 0.0
        
        # Build bigram model
        bigrams = defaultdict(int)
        total_bigrams = 0
        
        for i in range(len(words) - 1):
            bigram = (words[i], words[i+1])
            bigrams[bigram] += 1
            total_bigrams += 1
        
        # Calculate entropy (lower = more repetitive/predictable)
        entropy = 0.0
        for count in bigrams.values():
            p = count / total_bigrams
            entropy -= p * math.log2(p)
        
        # Normalize by theoretical maximum
        max_entropy = math.log2(total_bigrams)
        coherence = 1.0 - (entropy / max_entropy) if max_entropy > 0 else 0.0
        
        return coherence
    
    def calculate_grammar_score(self, text: str) -> Dict[str, float]:
        """
        Calculate basic grammar-like patterns
        - Word order variability
        - POS-like patterns (based on word length and endings)
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        if len(words) < 3:
            return {"pattern_score": 0.0, "order_variability": 0.0}
        
        # Simple heuristic: Latin has specific patterns
        # - Short words (1-3 chars) tend to be prepositions/conjunctions
        # - Words ending in 'um', 'us', 'a', 'is' are common Latin endings
        
        short_words = sum(1 for w in words if len(w) <= 3)
        latin_endings = sum(1 for w in words if w.endswith(('um', 'us', 'is', 'it', 'tur', 'or')))
        
        pattern_score = (latin_endings / len(words)) if words else 0.0
        short_ratio = (short_words / len(words)) if words else 0.0
        
        # Expected: Latin has ~10-15% short function words
        order_variability = abs(short_ratio - 0.125)  # Penalty for deviation from 12.5%
        
        return {
            "pattern_score": pattern_score,
            "short_word_ratio": short_ratio,
            "order_variability": 1.0 - order_variability
        }
    
    def calculate_repetition_penalty(self, text: str) -> float:
        """
        Penalize excessive word repetition
        Natural text has varied vocabulary
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return 0.0
        
        # Calculate what % of text is repeated content
        word_counts = Counter(words)
        unique_words = len(word_counts)
        total_words = len(words)
        
        # Type-token ratio (higher = more diverse)
        ttr = unique_words / total_words
        
        # Penalize if same word appears >5% of the time
        max_freq = max(word_counts.values())
        max_freq_ratio = max_freq / total_words
        
        repetition_penalty = max(0, (max_freq_ratio - 0.05) * 10)  # Scale penalty
        
        return 1.0 - min(repetition_penalty, 1.0)
    
    def compare_translations(self, real_translation: str, 
                           random_translation: str) -> Dict:
        """Compare real vs random translation quality"""
        # Calculate metrics for both
        real_metrics = {
            "coherence": self.calculate_bigram_coherence(real_translation),
            "grammar": self.calculate_grammar_score(real_translation),
            "repetition": self.calculate_repetition_penalty(real_translation)
        }
        
        random_metrics = {
            "coherence": self.calculate_bigram_coherence(random_translation),
            "grammar": self.calculate_grammar_score(random_translation),
            "repetition": self.calculate_repetition_penalty(random_translation)
        }
        
        # Calculate improvement over random
        improvement = {
            "coherence": (real_metrics["coherence"] - random_metrics["coherence"]),
            "grammar_pattern": (real_metrics["grammar"]["pattern_score"] - 
                              random_metrics["grammar"]["pattern_score"]),
            "repetition": (real_metrics["repetition"] - random_metrics["repetition"])
        }
        
        return {
            "real_metrics": real_metrics,
            "random_metrics": random_metrics,
            "improvement": improvement
        }
    
    def test_translation_file(self, filepath: Path, random_vocab: Dict[str, str]) -> Dict:
        """Test a single translation file against random baseline"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        voynich_text = data.get('voynich_text', '')
        real_latin = re.sub(r'\[[\w\s]+\]', '', data.get('latin_text', ''))
        
        # Generate random translation
        random_latin = self.translate_with_random_vocab(voynich_text, random_vocab)
        
        # Compare
        comparison = self.compare_translations(real_latin, random_latin)
        
        return {
            "folio_id": data.get('folio_id'),
            "section": data.get('section'),
            "coverage": data.get('statistics', {}).get('coverage', 0),
            "comparison": comparison
        }
    
    def run_null_hypothesis_test(self, num_random_trials: int = 5) -> Dict:
        """
        Run complete null hypothesis test
        
        Test: Are real translations significantly better than random?
        """
        print("\n🎲 RUNNING NULL HYPOTHESIS TEST")
        print("="*70)
        
        translation_files = sorted(self.translations_dir.glob("q*.json"))[:30]  # Sample
        
        all_trial_results = []
        
        for trial in range(num_random_trials):
            print(f"\n📊 Trial {trial + 1}/{num_random_trials}")
            
            # Generate random vocabulary
            random_vocab = self.generate_random_decipherment(seed=42 + trial)
            
            trial_results = []
            for filepath in translation_files:
                try:
                    result = self.test_translation_file(filepath, random_vocab)
                    trial_results.append(result)
                except Exception as e:
                    print(f"  ✗ {filepath.name}: {e}")
            
            all_trial_results.append(trial_results)
            print(f"  ✓ Analyzed {len(trial_results)} files")
        
        # Aggregate across trials
        aggregated = self._aggregate_trial_results(all_trial_results)
        
        return {
            "trials": all_trial_results,
            "aggregated": aggregated,
            "num_trials": num_random_trials,
            "num_files_per_trial": len(translation_files)
        }
    
    def _aggregate_trial_results(self, all_trials: List[List[Dict]]) -> Dict:
        """Aggregate results across multiple trials"""
        
        # Collect improvements across all trials
        all_coherence_improvements = []
        all_grammar_improvements = []
        all_repetition_improvements = []
        
        for trial_results in all_trials:
            for result in trial_results:
                comp = result['comparison']['improvement']
                all_coherence_improvements.append(comp['coherence'])
                all_grammar_improvements.append(comp['grammar_pattern'])
                all_repetition_improvements.append(comp['repetition'])
        
        def avg(values):
            return sum(values) / len(values) if values else 0.0
        
        def positive_ratio(values):
            return sum(1 for v in values if v > 0) / len(values) if values else 0.0
        
        return {
            "coherence": {
                "avg_improvement": avg(all_coherence_improvements),
                "positive_ratio": positive_ratio(all_coherence_improvements),
                "all_values": all_coherence_improvements
            },
            "grammar": {
                "avg_improvement": avg(all_grammar_improvements),
                "positive_ratio": positive_ratio(all_grammar_improvements),
                "all_values": all_grammar_improvements
            },
            "repetition": {
                "avg_improvement": avg(all_repetition_improvements),
                "positive_ratio": positive_ratio(all_repetition_improvements),
                "all_values": all_repetition_improvements
            }
        }
    
    def save_results(self, results: Dict, output_file: str = "data/null_hypothesis_test.json"):
        """Save test results"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove raw values to keep file size reasonable
        if 'aggregated' in results:
            for metric in ['coherence', 'grammar', 'repetition']:
                if metric in results['aggregated']:
                    results['aggregated'][metric].pop('all_values', None)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Results saved to: {output_path}")


def main():
    tester = NullHypothesisTester()
    
    # Run test
    results = tester.run_null_hypothesis_test(num_random_trials=5)
    
    # Save results
    tester.save_results(results)
    
    # Print summary
    agg = results['aggregated']
    
    print("\n" + "="*70)
    print("🎯 NULL HYPOTHESIS TEST RESULTS")
    print("="*70)
    
    print("\n📊 Real Translation vs Random Baseline:")
    print(f"\n  Coherence Improvement:")
    print(f"    Average:           {agg['coherence']['avg_improvement']:+.4f}")
    print(f"    Better than random: {agg['coherence']['positive_ratio']*100:.1f}%")
    
    print(f"\n  Grammar Pattern Improvement:")
    print(f"    Average:           {agg['grammar']['avg_improvement']:+.4f}")
    print(f"    Better than random: {agg['grammar']['positive_ratio']*100:.1f}%")
    
    print(f"\n  Repetition Control Improvement:")
    print(f"    Average:           {agg['repetition']['avg_improvement']:+.4f}")
    print(f"    Better than random: {agg['repetition']['positive_ratio']*100:.1f}%")
    
    print("\n" + "="*70)
    print("🔬 INTERPRETATION:")
    print("="*70)
    
    # Interpret results
    coherence_better = agg['coherence']['positive_ratio'] > 0.5
    grammar_better = agg['grammar']['positive_ratio'] > 0.5
    repetition_better = agg['repetition']['positive_ratio'] > 0.5
    
    if coherence_better and grammar_better and repetition_better:
        print("✅ SIGNIFICANT: Real translations are consistently better than random")
        print("   This suggests the translation system captures real structure.")
    elif coherence_better or grammar_better or repetition_better:
        print("⚠️  MIXED: Real translations show some improvements over random")
        print("   System may capture partial structure, but not fully linguistic.")
    else:
        print("❌ NOT SIGNIFICANT: Real translations are NOT better than random")
        print("   The translation system may be finding spurious patterns.")
    
    print("="*70)


if __name__ == "__main__":
    main()

