#!/usr/bin/env python3
"""
Voynich Manuscript Translator
Deterministic translation engine using voynich.yaml configuration
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TranslationResult:
    """Result of translating a word or phrase"""
    original: str
    latin: str
    confidence: float  # 0.0 to 1.0
    context: str
    notes: str = ""


class VoynichTranslator:
    """Deterministic Voynich-to-Latin translator"""
    
    def __init__(self, config_path: str = "voynich.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.vocab = self._build_vocab_dict()
        self.polysemy = self._build_polysemy_dict()
        self.glyph_map = self.config.get("voynich_decipherment_rules", {}).get("glyph_mapping", {})
        self.unknown_words = set()
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _build_vocab_dict(self) -> Dict[str, Dict]:
        """Build vocabulary lookup dictionary"""
        vocab_list = self.config.get("voynich_decipherment_rules", {}).get("vocab", [])
        vocab_dict = {}
        
        for entry in vocab_list:
            word = entry.get("word", "")
            if word:
                vocab_dict[word] = {
                    "latin": entry.get("latin", ""),
                    "description": entry.get("description", "")
                }
        
        return vocab_dict
    
    def _build_polysemy_dict(self) -> Dict[str, List[Dict]]:
        """Build polysemy lookup dictionary"""
        polysemy_list = self.config.get("voynich_decipherment_rules", {}).get("polysemy", [])
        polysemy_dict = {}
        
        for entry in polysemy_list:
            word = entry.get("word", "")
            if word:
                polysemy_dict[word] = {
                    "meanings": entry.get("meanings", []),
                    "base": entry.get("base", "")
                }
        
        return polysemy_dict
    
    def preprocess_word(self, word: str) -> str:
        """Apply preprocessing rules (null removal, etc.)"""
        if not word:
            return word
        
        # Remove 'o' as null in prefixes (qo-, ko-, po-, to-, co-)
        if word.startswith("o") and len(word) > 1 and word[1] in "kptc":
            word = word[1:]
        
        # Handle standalone 'o' as exclamation
        if word == "o":
            return "!"
        
        return word
    
    def resolve_polysemy(self, word: str, context: str) -> Tuple[str, float, str]:
        """
        Resolve word meaning based on context
        
        Returns: (latin_word, confidence, notes)
        """
        processed_word = self.preprocess_word(word)
        
        # Check if word has polysemous meanings
        if processed_word in self.polysemy:
            polysemy_data = self.polysemy[processed_word]
            meanings = polysemy_data["meanings"]
            
            # Try to match context
            for meaning in meanings:
                meaning_context = meaning.get("context", "").lower()
                if context.lower() in meaning_context or "all sections" in meaning_context:
                    return meaning.get("latin", ""), 0.8, f"polysemy:{meaning_context}"
            
            # Fallback to base meaning
            base = polysemy_data.get("base", "")
            if base:
                return base, 0.6, "polysemy:base"
        
        # Check regular vocabulary
        if processed_word in self.vocab:
            vocab_entry = self.vocab[processed_word]
            return vocab_entry["latin"], 0.9, vocab_entry["description"]
        
        # Word not found
        self.unknown_words.add(word)
        return f"[{word}]", 0.0, "unknown"
    
    def handle_repetition(self, words: List[str]) -> List[str]:
        """Handle repeated words (e.g., 'qokedy qokedy' -> 'valde qokedy')"""
        if len(words) < 2:
            return words
        
        result = []
        i = 0
        while i < len(words):
            if i < len(words) - 1 and words[i] == words[i + 1]:
                # Repeated word - add 'valde' intensifier
                result.append("valde")
                result.append(words[i])
                i += 2
            else:
                result.append(words[i])
                i += 1
        
        return result
    
    def handle_qo_prefix(self, word: str, context: str) -> Tuple[str, float, str]:
        """Handle 'qo-' intensifier prefix"""
        if word.startswith("qo") and len(word) > 2:
            # Try full word first (might be in dictionary)
            latin, conf, notes = self.resolve_polysemy(word, context)
            if conf > 0.5:
                return latin, conf, notes
            
            # Try stripping 'qo-' and adding 'valde'
            base_word = word[2:]  # Remove 'qo'
            base_latin, base_conf, base_notes = self.resolve_polysemy(base_word, context)
            
            if base_conf > 0.5:
                return f"valde {base_latin}", base_conf * 0.9, f"qo-prefix:{base_notes}"
        
        return self.resolve_polysemy(word, context)
    
    def translate_word(self, word: str, context: str) -> TranslationResult:
        """Translate a single Voynichese word"""
        # Strip whitespace from word
        word = word.strip()
        original = word
        
        # Handle empty
        if not word:
            return TranslationResult(original, "", 1.0, context, "empty")
        
        # Handle qo- prefix
        latin, confidence, notes = self.handle_qo_prefix(word, context)
        
        return TranslationResult(
            original=original,
            latin=latin,
            confidence=confidence,
            context=context,
            notes=notes
        )
    
    def translate_phrase(self, text: str, context: str = "herbal") -> List[TranslationResult]:
        """Translate a phrase or sentence"""
        # Split into words
        words = re.split(r'\s+', text.strip())
        
        # Handle repetitions
        words = self.handle_repetition(words)
        
        # Translate each word
        results = []
        for word in words:
            if word:
                result = self.translate_word(word, context)
                results.append(result)
        
        return results
    
    def translate_to_latin(self, text: str, context: str = "herbal") -> str:
        """Translate Voynichese text to Latin"""
        results = self.translate_phrase(text, context)
        latin_words = [r.latin for r in results if r.latin]
        
        # Basic grammar smoothing
        sentence = " ".join(latin_words)
        # Remove redundant 'et'
        sentence = re.sub(r'\bet\s+et\b', 'et', sentence)
        # Clean up spacing
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        
        return sentence
    
    def translate_latin_to_english(self, latin_text: str, context: str = "herbal") -> str:
        """
        Translate Latin text to English
        Simple word-by-word translation with basic grammar adjustments
        """
        # Latin to English mapping (botanical/herbal context focused)
        latin_to_english = {
            # Plants and parts
            "planta": "plant", "plantam": "plant", "plantae": "plants",
            "herba": "herb", "herbam": "herb", "herbae": "herbs",
            "caulis": "stem", "caulem": "stem",
            "ramus": "branch", "ramum": "branch", "rami": "branches",
            "ramulus": "twig", "ramulum": "twig",
            "ramusculus": "small twig",
            "radix": "root", "radicem": "root", "radices": "roots",
            "folium": "leaf", "folia": "leaves",
            "flos": "flower", "flores": "flowers",
            "fructus": "fruit",
            "semen": "seed", "semina": "seeds",
            "cortex": "bark",
            "lignum": "wood",
            "stipes": "stalk",
            "pars": "part",
            "corpus": "body",
            "columna": "column",
            "ductus": "duct",
            "via": "path",
            
            # Growth and actions
            "crescit": "grows", "crescere": "to grow",
            "floret": "flowers", "florere": "to flower",
            "germinat": "sprouts",
            "maturat": "ripens",
            "producit": "produces",
            "praebet": "presents",
            "dat": "gives",
            "facit": "makes",
            "habet": "has",
            "tenet": "holds",
            "continet": "contains",
            "tangit": "touches",
            "percipit": "perceives",
            "contingit": "happens",
            "extendit": "extends",
            "tendit": "stretches",
            "movetur": "moves",
            "movet": "moves",
            "variat": "varies",
            "ordinat": "arranges",
            "inspicit": "examines",
            "ramificat": "branches",
            
            # Properties and descriptions
            "magnus": "large", "magna": "large", "magnum": "large",
            "parvus": "small", "parva": "small", "parvum": "small",
            "altus": "tall", "alta": "tall", "altum": "tall",
            "longus": "long", "longa": "long", "longum": "long",
            "latus": "wide", "lata": "wide",
            "robur": "strong", "robustus": "robust",
            "siccus": "dry", "sicca": "dry",
            "viridis": "green",
            "albus": "white", "alba": "white",
            
            # Locations and directions
            "in": "in",
            "ex": "from",
            "ad": "to",
            "de": "from",
            "per": "through",
            "versus": "toward",
            "intra": "within",
            "inter": "among",
            "hic": "here",
            "ille": "that",
            "iste": "this",
            "locus": "place",
            "spatium": "space",
            "regio": "region",
            "terra": "earth",
            
            # Quantities and connectors
            "et": "and",
            "que": "and",
            "cum": "with",
            "vel": "or",
            "sed": "but",
            "item": "also",
            "valde": "very",
            "multum": "much",
            "saepe": "often",
            "omnis": "all",
            "modo": "manner",
            
            # States
            "est": "is",
            "erat": "was",
            "esse": "to be",
            
            # Time
            "nunc": "now",
            "deinde": "then",
            
            # Elements
            "elementum": "element",
            "materia": "matter",
            "resina": "resin",
            
            # Other
            "ordo": "order",
            "nomen": "name",
            "gratia": "grace",
            "donum": "gift",
            "ala": "wing",
            "quidem": "indeed",
            "stella": "star",
            "magnitudo": "magnitude",
        }
        
        # Split into words
        words = latin_text.split()
        english_words = []
        
        for word in words:
            # Clean word
            clean_word = word.strip("[]().,;:!?")
            
            # Check if it's an unknown word marker
            if word.startswith("[") and word.endswith("]"):
                english_words.append(word)  # Keep unknown markers
                continue
            
            # Try to translate
            if clean_word.lower() in latin_to_english:
                english_words.append(latin_to_english[clean_word.lower()])
            else:
                # Try without case endings (simple stem matching)
                found = False
                for latin_stem, english in latin_to_english.items():
                    if clean_word.lower().startswith(latin_stem):
                        english_words.append(english)
                        found = True
                        break
                if not found:
                    english_words.append(f"[{clean_word}]")  # Mark untranslated
        
        # Join and do basic grammar cleanup
        english_text = " ".join(english_words)
        
        # Capitalize first letter
        if english_text:
            english_text = english_text[0].upper() + english_text[1:]
        
        # Add period if not present
        if english_text and not english_text.endswith("."):
            english_text += "."
        
        return english_text
    
    def get_translation_stats(self, results: List[TranslationResult]) -> Dict:
        """Get statistics about a translation"""
        total = len(results)
        if total == 0:
            return {"total": 0, "known": 0, "unknown": 0, "avg_confidence": 0.0}
        
        known = sum(1 for r in results if r.confidence > 0.5)
        unknown = total - known
        avg_confidence = sum(r.confidence for r in results) / total
        
        return {
            "total": total,
            "known": known,
            "unknown": unknown,
            "avg_confidence": avg_confidence,
            "coverage": known / total if total > 0 else 0.0
        }
    
    def get_unknown_words(self) -> List[str]:
        """Get list of unknown words encountered"""
        return sorted(list(self.unknown_words))
    
    def infer_context_from_section(self, section: str) -> str:
        """Infer translation context from section name"""
        section_lower = section.lower()
        
        if "herbal" in section_lower:
            return "herbal"
        elif "astro" in section_lower or "star" in section_lower:
            return "astronomical"
        elif "bio" in section_lower:
            return "biological"
        elif "pharma" in section_lower:
            return "pharmaceutical"
        elif "cosmo" in section_lower:
            return "cosmological"
        else:
            return "all"


def main():
    """Test translator"""
    translator = VoynichTranslator()
    
    # Test cases from README
    test_cases = [
        ("fachys ykal ar ataiin olis shy", "herbal"),
        ("okeey okeey qokeey daiin cthey", "astronomical"),
        ("qokaiin otaiin okaiin shol cphy", "biological"),
    ]
    
    print("🔤 Voynich Translator Test\n")
    
    for voynich_text, context in test_cases:
        print(f"Context: {context}")
        print(f"Original: {voynich_text}")
        
        results = translator.translate_phrase(voynich_text, context)
        latin = translator.translate_to_latin(voynich_text, context)
        stats = translator.get_translation_stats(results)
        
        print(f"Latin: {latin}")
        print(f"Stats: {stats['known']}/{stats['total']} words known ({stats['coverage']:.1%} coverage)")
        print()


if __name__ == "__main__":
    main()

