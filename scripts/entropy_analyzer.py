#!/usr/bin/env python3
"""
Information Theory Analysis of Voynich Translations
Calculate entropy, compression ratios, and linguistic metrics
"""

import json
import math
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import gzip


class EntropyAnalyzer:
    """Calculate information theory metrics for text analysis"""
    
    def __init__(self):
        self.translations_dir = Path("data/translations")
        
    def calculate_entropy(self, text: str, unit: str = 'char') -> float:
        """
        Calculate Shannon entropy
        H(X) = -Σ p(x) * log2(p(x))
        
        Args:
            text: Input text
            unit: 'char' or 'word'
        Returns:
            Entropy in bits per unit
        """
        if not text:
            return 0.0
        
        # Tokenize
        if unit == 'char':
            tokens = list(text.lower())
        elif unit == 'word':
            tokens = re.findall(r'\b\w+\b', text.lower())
        else:
            raise ValueError(f"Unknown unit: {unit}")
        
        # Calculate probabilities
        total = len(tokens)
        frequencies = Counter(tokens)
        
        # Calculate entropy
        entropy = 0.0
        for count in frequencies.values():
            p = count / total
            entropy -= p * math.log2(p)
        
        return entropy
    
    def calculate_conditional_entropy(self, text: str, order: int = 1) -> float:
        """
        Calculate conditional entropy (predictability)
        H(X_n | X_{n-1}, ..., X_{n-order})
        
        Lower values = more predictable
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        if len(words) <= order:
            return 0.0
        
        # Build context -> next_word mapping
        context_counts = defaultdict(lambda: defaultdict(int))
        
        for i in range(order, len(words)):
            context = tuple(words[i-order:i])
            next_word = words[i]
            context_counts[context][next_word] += 1
        
        # Calculate conditional entropy
        total_entropy = 0.0
        total_contexts = 0
        
        for context, next_words in context_counts.items():
            total = sum(next_words.values())
            context_entropy = 0.0
            
            for count in next_words.values():
                p = count / total
                context_entropy -= p * math.log2(p)
            
            total_entropy += context_entropy * total
            total_contexts += total
        
        return total_entropy / total_contexts if total_contexts > 0 else 0.0
    
    def calculate_compression_ratio(self, text: str) -> float:
        """
        Calculate gzip compression ratio
        Lower ratio = more compressible = more redundant
        """
        if not text:
            return 0.0
        
        original_bytes = text.encode('utf-8')
        compressed_bytes = gzip.compress(original_bytes)
        
        return len(compressed_bytes) / len(original_bytes)
    
    def calculate_lexical_diversity(self, text: str) -> Dict[str, float]:
        """
        Calculate type-token ratio and related metrics
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return {"ttr": 0.0, "hapax_ratio": 0.0}
        
        word_counts = Counter(words)
        unique_words = len(word_counts)
        total_words = len(words)
        hapax_legomena = sum(1 for count in word_counts.values() if count == 1)
        
        return {
            "ttr": unique_words / total_words,  # Type-Token Ratio
            "hapax_ratio": hapax_legomena / unique_words if unique_words > 0 else 0.0,
            "unique_words": unique_words,
            "total_words": total_words
        }
    
    def calculate_word_length_distribution(self, text: str) -> Dict:
        """Calculate average word length and distribution"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return {"avg_length": 0.0, "distribution": {}}
        
        lengths = [len(w) for w in words]
        length_dist = Counter(lengths)
        
        return {
            "avg_length": sum(lengths) / len(lengths),
            "distribution": dict(length_dist),
            "min_length": min(lengths),
            "max_length": max(lengths)
        }
    
    def analyze_translation_file(self, filepath: Path) -> Dict:
        """Analyze a single translation file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        voynich_text = data.get('voynich_text', '')
        latin_text = data.get('latin_text', '')
        english_text = data.get('english_text', '')
        
        # Remove bracketed unknowns for entropy calculation
        latin_clean = re.sub(r'\[[\w\s]+\]', '', latin_text)
        english_clean = re.sub(r'\[[\w\s]+\]', '', english_text)
        
        return {
            "folio_id": data.get('folio_id'),
            "section": data.get('section'),
            "coverage": data.get('statistics', {}).get('coverage', 0),
            "voynich": {
                "char_entropy": self.calculate_entropy(voynich_text, 'char'),
                "word_entropy": self.calculate_entropy(voynich_text, 'word'),
                "conditional_entropy": self.calculate_conditional_entropy(voynich_text, order=1),
                "compression_ratio": self.calculate_compression_ratio(voynich_text),
                "lexical": self.calculate_lexical_diversity(voynich_text),
                "word_length": self.calculate_word_length_distribution(voynich_text)
            },
            "latin": {
                "char_entropy": self.calculate_entropy(latin_clean, 'char'),
                "word_entropy": self.calculate_entropy(latin_clean, 'word'),
                "conditional_entropy": self.calculate_conditional_entropy(latin_clean, order=1),
                "compression_ratio": self.calculate_compression_ratio(latin_clean),
                "lexical": self.calculate_lexical_diversity(latin_clean),
                "word_length": self.calculate_word_length_distribution(latin_clean)
            },
            "english": {
                "char_entropy": self.calculate_entropy(english_clean, 'char'),
                "word_entropy": self.calculate_entropy(english_clean, 'word'),
                "conditional_entropy": self.calculate_conditional_entropy(english_clean, order=1),
                "compression_ratio": self.calculate_compression_ratio(english_clean),
                "lexical": self.calculate_lexical_diversity(english_clean),
                "word_length": self.calculate_word_length_distribution(english_clean)
            }
        }
    
    def analyze_all_translations(self) -> Dict:
        """Analyze all translation files and aggregate statistics"""
        translation_files = sorted(self.translations_dir.glob("q*.json"))
        
        print(f"\n📊 Analyzing {len(translation_files)} translation files...")
        
        results = []
        for filepath in translation_files:
            try:
                result = self.analyze_translation_file(filepath)
                results.append(result)
                print(f"  ✓ {filepath.name}")
            except Exception as e:
                print(f"  ✗ {filepath.name}: {e}")
        
        # Aggregate statistics
        aggregated = self._aggregate_results(results)
        
        return {
            "individual_results": results,
            "aggregated": aggregated,
            "total_files_analyzed": len(results)
        }
    
    def _aggregate_results(self, results: List[Dict]) -> Dict:
        """Calculate aggregate statistics across all files"""
        
        def avg(values):
            return sum(values) / len(values) if values else 0.0
        
        # Collect values
        voynich_char_ent = [r['voynich']['char_entropy'] for r in results]
        voynich_word_ent = [r['voynich']['word_entropy'] for r in results]
        voynich_cond_ent = [r['voynich']['conditional_entropy'] for r in results]
        voynich_comp = [r['voynich']['compression_ratio'] for r in results]
        
        latin_char_ent = [r['latin']['char_entropy'] for r in results]
        latin_word_ent = [r['latin']['word_entropy'] for r in results]
        latin_cond_ent = [r['latin']['conditional_entropy'] for r in results]
        latin_comp = [r['latin']['compression_ratio'] for r in results]
        
        english_char_ent = [r['english']['char_entropy'] for r in results]
        english_word_ent = [r['english']['word_entropy'] for r in results]
        english_cond_ent = [r['english']['conditional_entropy'] for r in results]
        english_comp = [r['english']['compression_ratio'] for r in results]
        
        return {
            "voynich": {
                "avg_char_entropy": avg(voynich_char_ent),
                "avg_word_entropy": avg(voynich_word_ent),
                "avg_conditional_entropy": avg(voynich_cond_ent),
                "avg_compression_ratio": avg(voynich_comp)
            },
            "latin": {
                "avg_char_entropy": avg(latin_char_ent),
                "avg_word_entropy": avg(latin_word_ent),
                "avg_conditional_entropy": avg(latin_cond_ent),
                "avg_compression_ratio": avg(latin_comp)
            },
            "english": {
                "avg_char_entropy": avg(english_char_ent),
                "avg_word_entropy": avg(english_word_ent),
                "avg_conditional_entropy": avg(english_cond_ent),
                "avg_compression_ratio": avg(english_comp)
            }
        }
    
    def save_results(self, results: Dict, output_file: str = "data/entropy_analysis.json"):
        """Save analysis results to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Results saved to: {output_path}")


def main():
    analyzer = EntropyAnalyzer()
    
    # Run analysis
    results = analyzer.analyze_all_translations()
    
    # Save results
    analyzer.save_results(results)
    
    # Print summary
    agg = results['aggregated']
    print("\n" + "="*70)
    print("📊 ENTROPY ANALYSIS SUMMARY")
    print("="*70)
    
    print("\n🔤 Voynichese (Source):")
    print(f"  Character Entropy:     {agg['voynich']['avg_char_entropy']:.3f} bits/char")
    print(f"  Word Entropy:          {agg['voynich']['avg_word_entropy']:.3f} bits/word")
    print(f"  Conditional Entropy:   {agg['voynich']['avg_conditional_entropy']:.3f} bits/word")
    print(f"  Compression Ratio:     {agg['voynich']['avg_compression_ratio']:.3f}")
    
    print("\n🏛️  Latin (Translation):")
    print(f"  Character Entropy:     {agg['latin']['avg_char_entropy']:.3f} bits/char")
    print(f"  Word Entropy:          {agg['latin']['avg_word_entropy']:.3f} bits/word")
    print(f"  Conditional Entropy:   {agg['latin']['avg_conditional_entropy']:.3f} bits/word")
    print(f"  Compression Ratio:     {agg['latin']['avg_compression_ratio']:.3f}")
    
    print("\n🌍 English (Translation):")
    print(f"  Character Entropy:     {agg['english']['avg_char_entropy']:.3f} bits/char")
    print(f"  Word Entropy:          {agg['english']['avg_word_entropy']:.3f} bits/word")
    print(f"  Conditional Entropy:   {agg['english']['avg_conditional_entropy']:.3f} bits/word")
    print(f"  Compression Ratio:     {agg['english']['avg_compression_ratio']:.3f}")
    
    print("\n" + "="*70)
    
    # Expected values for comparison
    print("\n📚 Expected Values (Natural Language):")
    print("  English:  ~4.1 bits/char, ~10.0 bits/word")
    print("  Latin:    ~3.8 bits/char, ~9.5 bits/word")
    print("  Voynich:  ~4.0 bits/char (known from literature)")
    print("="*70)


if __name__ == "__main__":
    main()

