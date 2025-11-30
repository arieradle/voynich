#!/usr/bin/env python3
"""
Translate Voynich manuscript folios using deterministic translation
"""

import argparse
import json
import math
import re
import gzip
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import Counter
from download_folios import FolioDownloader
from translator import VoynichTranslator, TranslationResult


class FolioTranslator:
    """High-level folio translation coordinator"""
    
    def __init__(self, output_dir: str = "data/translations", include_validation: bool = True):
        self.downloader = FolioDownloader()
        self.translator = VoynichTranslator()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.include_validation = include_validation
    
    def calculate_entropy(self, text: str, unit: str = 'char') -> float:
        """Calculate Shannon entropy for validation"""
        if not text:
            return 0.0
        
        if unit == 'char':
            tokens = list(text.lower())
        elif unit == 'word':
            tokens = re.findall(r'\b\w+\b', text.lower())
        else:
            return 0.0
        
        if not tokens:
            return 0.0
        
        frequencies = Counter(tokens)
        total = len(tokens)
        
        entropy = 0.0
        for count in frequencies.values():
            p = count / total
            entropy -= p * math.log2(p)
        
        return entropy
    
    def calculate_compression_ratio(self, text: str) -> float:
        """Calculate gzip compression ratio"""
        if not text:
            return 0.0
        
        original_bytes = text.encode('utf-8')
        compressed_bytes = gzip.compress(original_bytes)
        
        return len(compressed_bytes) / len(original_bytes)
    
    def calculate_lexical_diversity(self, text: str) -> Dict:
        """Calculate type-token ratio"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return {"ttr": 0.0, "unique_words": 0, "total_words": 0}
        
        word_counts = Counter(words)
        unique_words = len(word_counts)
        total_words = len(words)
        
        return {
            "ttr": unique_words / total_words,
            "unique_words": unique_words,
            "total_words": total_words
        }
    
    def calculate_validation_metrics(self, voynich_text: str, latin_text: str, english_text: str) -> Dict:
        """Calculate validation metrics for a translation"""
        # Remove bracketed unknowns for cleaner analysis
        latin_clean = re.sub(r'\[[\w\s]+\]', '', latin_text)
        english_clean = re.sub(r'\[[\w\s]+\]', '', english_text)
        
        return {
            "voynich": {
                "char_entropy": round(self.calculate_entropy(voynich_text, 'char'), 3),
                "word_entropy": round(self.calculate_entropy(voynich_text, 'word'), 3),
                "compression_ratio": round(self.calculate_compression_ratio(voynich_text), 3),
                "lexical_diversity": self.calculate_lexical_diversity(voynich_text)
            },
            "latin": {
                "char_entropy": round(self.calculate_entropy(latin_clean, 'char'), 3),
                "word_entropy": round(self.calculate_entropy(latin_clean, 'word'), 3),
                "compression_ratio": round(self.calculate_compression_ratio(latin_clean), 3),
                "lexical_diversity": self.calculate_lexical_diversity(latin_clean)
            },
            "english": {
                "char_entropy": round(self.calculate_entropy(english_clean, 'char'), 3),
                "word_entropy": round(self.calculate_entropy(english_clean, 'word'), 3),
                "compression_ratio": round(self.calculate_compression_ratio(english_clean), 3),
                "lexical_diversity": self.calculate_lexical_diversity(english_clean)
            },
            "quality_flags": {
                "low_word_entropy": self.calculate_entropy(latin_clean, 'word') < 5.0,
                "high_compression": self.calculate_compression_ratio(latin_clean) < 0.25,
                "low_diversity": self.calculate_lexical_diversity(latin_clean)["ttr"] < 0.3
            },
            "expected_values": {
                "latin_char_entropy": "~3.8 bits/char",
                "latin_word_entropy": "~9.5 bits/word",
                "english_char_entropy": "~4.1 bits/char",
                "english_word_entropy": "~10.0 bits/word"
            }
        }
    
    def translate_folio_file(self, folio_path: Path, context: str = None, section: str = None) -> Dict:
        """Translate a folio from its cached file"""
        # Reset unknown words tracking for this folio
        self.translator.unknown_words = set()
        
        with open(folio_path, 'r') as f:
            text = f.read()
        
        # Parse folio
        folio_data = self.downloader.parse_folio_text(text, str(folio_path))
        
        # Override section if provided (fix for cached files)
        if section:
            from download_folios import SECTION_MAP
            folio_data["section"] = SECTION_MAP.get(section, section)
        
        # Auto-detect context if not provided
        if context is None:
            context = self.translator.infer_context_from_section(folio_data["section"])
        
        # Translate each word
        all_results = []
        for word in folio_data["voynich_words"]:
            result = self.translator.translate_word(word, context)
            all_results.append({
                "original": result.original,
                "latin": result.latin,
                "confidence": result.confidence,
                "notes": result.notes
            })
        
        # Full text translation
        full_voynich = " ".join(folio_data["voynich_words"])
        full_latin = self.translator.translate_to_latin(full_voynich, context)
        full_english = self.translator.translate_latin_to_english(full_latin, context)
        
        # Get statistics
        result_objects = self.translator.translate_phrase(full_voynich, context)
        stats = self.translator.get_translation_stats(result_objects)
        
        # Calculate validation metrics if enabled
        validation_metrics = None
        if self.include_validation:
            validation_metrics = self.calculate_validation_metrics(
                full_voynich, full_latin, full_english
            )
        
        result = {
            "folio_id": folio_data["folio_id"],
            "section": folio_data["section"],
            "context": context,
            "voynich_text": full_voynich,
            "latin_text": full_latin,
            "english_text": full_english,
            "word_translations": all_results,
            "statistics": stats,
            "unknown_words": self.translator.get_unknown_words(),
            "translated_at": datetime.now().isoformat()
        }
        
        # Add validation metrics if calculated
        if validation_metrics:
            result["validation_metrics"] = validation_metrics
        
        return result
    
    def translate_and_save(self, section: str, folio_id: str, context: str = None, force: bool = False) -> Dict:
        """Translate a folio and save results"""
        # Get folio path
        folio_path = self.downloader.get_folio_path(section, folio_id)
        
        # Fallback: Try direct file path for non-standard folios (like Q14)
        if not folio_path or not folio_path.exists():
            direct_path = Path(f"data/folios/{section}/f{folio_id}.txt")
            if direct_path.exists():
                folio_path = direct_path
            else:
                raise FileNotFoundError(f"Folio not found: {section}/f{folio_id}. Download it first.")
        
        print(f"\n🔤 Translating: {section}/f{folio_id}")
        
        # Translate with section info
        result = self.translate_folio_file(folio_path, context, section)
        
        # Save translation
        output_file = self.output_dir / f"{section}_f{folio_id}_translation.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✓ Translation saved: {output_file}")
        
        # Print summary
        stats = result["statistics"]
        print(f"\n📊 Statistics:")
        print(f"   • Section: {result['section']}")
        print(f"   • Context: {result['context']}")
        print(f"   • Total words: {stats['total']}")
        print(f"   • Known: {stats['known']} ({stats['coverage']:.1%})")
        print(f"   • Unknown: {stats['unknown']}")
        print(f"   • Avg confidence: {stats['avg_confidence']:.2f}")
        
        # Print validation metrics if available
        if 'validation_metrics' in result:
            vm = result['validation_metrics']
            print(f"\n🔬 Validation Metrics:")
            print(f"   • Latin word entropy: {vm['latin']['word_entropy']} bits/word (expected: ~9.5)")
            print(f"   • English word entropy: {vm['english']['word_entropy']} bits/word (expected: ~10.0)")
            print(f"   • Lexical diversity (TTR): {vm['latin']['lexical_diversity']['ttr']:.3f}")
            
            # Show quality warnings
            flags = vm['quality_flags']
            if flags['low_word_entropy']:
                print(f"   ⚠️  WARNING: Low word entropy (excessive repetition)")
            if flags['high_compression']:
                print(f"   ⚠️  WARNING: High compression (too predictable)")
            if flags['low_diversity']:
                print(f"   ⚠️  WARNING: Low lexical diversity (limited vocabulary)")
        
        if result["unknown_words"]:
            print(f"\n❓ Unknown words ({len(result['unknown_words'])}):")
            for word in result["unknown_words"][:10]:  # Show first 10
                print(f"   • {word}")
            if len(result["unknown_words"]) > 10:
                print(f"   ... and {len(result['unknown_words']) - 10} more")
        
        return result
    
    def batch_translate(self, section: str, start: int, end: int, context: str = None, force: bool = False):
        """Translate multiple folios"""
        print(f"\n📚 Batch translating {section} folios {start}-{end}")
        
        results = []
        for i in range(start, end + 1):
            for side in ['r', 'v']:
                folio_id = f"{i:03d}{side}"
                try:
                    result = self.translate_and_save(section, folio_id, context, force)
                    results.append(result)
                except FileNotFoundError as e:
                    print(f"⚠️  Skipping {folio_id}: {e}")
                except Exception as e:
                    print(f"❌ Error translating {folio_id}: {e}")
        
        # Summary statistics
        if results:
            avg_coverage = sum(r["statistics"]["coverage"] for r in results) / len(results)
            all_unknown = set()
            for r in results:
                all_unknown.update(r["unknown_words"])
            
            print(f"\n✅ Batch complete:")
            print(f"   • Translated: {len(results)} folios")
            print(f"   • Average coverage: {avg_coverage:.1%}")
            print(f"   • Total unique unknown words: {len(all_unknown)}")
        
        return results
    
    def show_translation(self, section: str, folio_id: str):
        """Display a saved translation"""
        output_file = self.output_dir / f"{section}_f{folio_id}_translation.json"
        
        if not output_file.exists():
            print(f"❌ Translation not found: {output_file}")
            print("   Run translation first.")
            return
        
        with open(output_file, 'r') as f:
            result = json.load(f)
        
        print(f"\n📖 Folio: {result['folio_id']} ({result['section']})")
        print(f"Context: {result['context']}")
        print(f"\n🔤 Voynichese:")
        print(f"   {result['voynich_text'][:200]}...")
        print(f"\n🏛️  Latin:")
        print(f"   {result['latin_text'][:200]}...")
        
        stats = result["statistics"]
        print(f"\n📊 Coverage: {stats['coverage']:.1%} ({stats['known']}/{stats['total']} words)")


def main():
    parser = argparse.ArgumentParser(description="Translate Voynich manuscript folios")
    parser.add_argument("--section", default="q02", help="Section code (q01, q02, etc.)")
    parser.add_argument("--folio", help="Single folio ID (e.g., '014v')")
    parser.add_argument("--start", type=int, help="Start folio number for batch")
    parser.add_argument("--end", type=int, help="End folio number for batch")
    parser.add_argument("--context", help="Translation context (herbal, astronomical, etc.)")
    parser.add_argument("--show", help="Show existing translation for folio ID")
    parser.add_argument("--force", action="store_true", help="Force re-translation")
    
    args = parser.parse_args()
    
    translator = FolioTranslator()
    
    if args.show:
        translator.show_translation(args.section, args.show)
    elif args.folio:
        translator.translate_and_save(args.section, args.folio, args.context, args.force)
    elif args.start and args.end:
        translator.batch_translate(args.section, args.start, args.end, args.context, args.force)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

