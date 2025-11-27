#!/usr/bin/env python3
"""
Validation Checker
Validates dictionary consistency and translation quality
"""

import argparse
import json
import yaml
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple


class ValidationChecker:
    """Validate dictionary and system integrity"""
    
    def __init__(self, dictionary_path: str = "voynich.yaml"):
        self.dictionary_path = Path(dictionary_path)
        self.dictionary = {}
        self.vocab_list = []
        self.polysemy_list = []
        self.errors = []
        self.warnings = []
        self.info = []
        
    def load_dictionary(self) -> bool:
        """Load dictionary for validation"""
        if not self.dictionary_path.exists():
            self.errors.append(f"Dictionary not found: {self.dictionary_path}")
            return False
        
        try:
            with open(self.dictionary_path, 'r') as f:
                self.dictionary = yaml.safe_load(f)
            
            rules = self.dictionary.get("voynich_decipherment_rules", {})
            self.vocab_list = rules.get("vocab", [])
            self.polysemy_list = rules.get("polysemy", [])
            
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error loading dictionary: {e}")
            return False
    
    def check_yaml_syntax(self) -> bool:
        """Validate YAML syntax"""
        try:
            with open(self.dictionary_path, 'r') as f:
                yaml.safe_load(f)
            self.info.append("✓ YAML syntax valid")
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"YAML syntax error: {e}")
            return False
    
    def check_duplicates(self) -> bool:
        """Check for duplicate word entries"""
        words = [entry.get("word", "") for entry in self.vocab_list]
        word_counts = Counter(words)
        
        duplicates = {word: count for word, count in word_counts.items() 
                     if count > 1 and word}
        
        if duplicates:
            for word, count in duplicates.items():
                self.errors.append(f"Duplicate entry: '{word}' appears {count} times")
            return False
        else:
            self.info.append(f"✓ No duplicates found ({len(words)} unique entries)")
            return True
    
    def check_required_fields(self) -> bool:
        """Check all entries have required fields"""
        issues = []
        
        for i, entry in enumerate(self.vocab_list):
            word = entry.get("word", f"[entry {i}]")
            
            if not entry.get("word"):
                issues.append(f"Entry {i}: missing 'word' field")
            
            if not entry.get("latin"):
                issues.append(f"Word '{word}': missing 'latin' field")
            
            if not entry.get("description"):
                issues.append(f"Word '{word}': missing 'description' field")
        
        if issues:
            for issue in issues:
                self.errors.append(issue)
            return False
        else:
            self.info.append(f"✓ All entries have required fields")
            return True
    
    def check_field_formats(self) -> bool:
        """Validate field formats"""
        issues = []
        
        for entry in self.vocab_list:
            word = entry.get("word", "")
            latin = entry.get("latin", "")
            
            # Word should be lowercase letters only
            if word and not word.islower():
                self.warnings.append(f"Word '{word}': should be lowercase")
            
            if word and not all(c.isalpha() or c in ['-', '!'] for c in word):
                self.warnings.append(f"Word '{word}': contains non-alphabetic characters")
            
            # Latin should be reasonable
            if latin and len(latin) > 100:
                self.warnings.append(f"Word '{word}': latin translation very long ({len(latin)} chars)")
        
        if not self.warnings:
            self.info.append("✓ Field formats look good")
        
        return len(self.errors) == 0
    
    def check_polysemy_format(self) -> bool:
        """Validate polysemy entries"""
        issues = []
        
        # Get all vocabulary words
        vocab_words = {entry.get("word") for entry in self.vocab_list}
        
        for entry in self.polysemy_list:
            word = entry.get("word", "")
            
            if not word:
                issues.append("Polysemy entry missing 'word' field")
                continue
            
            # Check word exists in vocabulary
            if word not in vocab_words:
                self.warnings.append(f"Polysemy word '{word}' not in vocabulary")
            
            # Check has meanings
            meanings = entry.get("meanings", [])
            if not meanings:
                issues.append(f"Polysemy word '{word}': no meanings defined")
            
            # Check base meaning
            if not entry.get("base"):
                self.warnings.append(f"Polysemy word '{word}': no base meaning")
            
            # Validate meaning format
            for meaning in meanings:
                if not meaning.get("latin"):
                    issues.append(f"Polysemy word '{word}': meaning missing 'latin' field")
                if not meaning.get("context"):
                    self.warnings.append(f"Polysemy word '{word}': meaning missing 'context' field")
        
        if issues:
            for issue in issues:
                self.errors.append(issue)
            return False
        else:
            self.info.append(f"✓ {len(self.polysemy_list)} polysemy entries validated")
            return True
    
    def check_consistency(self) -> bool:
        """Check for logical consistency"""
        # Check if polysemy base meanings exist in vocabulary
        vocab_words_latin = {entry.get("word"): entry.get("latin") 
                            for entry in self.vocab_list}
        
        for poly_entry in self.polysemy_list:
            word = poly_entry.get("word", "")
            base = poly_entry.get("base", "")
            
            if word in vocab_words_latin:
                vocab_latin = vocab_words_latin[word]
                # Base should match or be similar to one of the meanings
                meanings_latin = [m.get("latin") for m in poly_entry.get("meanings", [])]
                
                if base not in meanings_latin and vocab_latin not in meanings_latin:
                    self.warnings.append(
                        f"Polysemy '{word}': base '{base}' doesn't match "
                        f"vocabulary '{vocab_latin}' or meanings"
                    )
        
        self.info.append("✓ Consistency checks complete")
        return True
    
    def check_translations_quality(self, translations_dir: str = "data/translations"):
        """Check translation files for quality issues"""
        translations_path = Path(translations_dir)
        
        if not translations_path.exists():
            self.warnings.append(f"Translations directory not found: {translations_dir}")
            return
        
        total_coverage = []
        total_unknowns = set()
        
        for file_path in translations_path.glob("*_translation.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                coverage = data.get("statistics", {}).get("coverage", 0)
                total_coverage.append(coverage)
                
                unknowns = data.get("unknown_words", [])
                total_unknowns.update(unknowns)
                
            except Exception as e:
                self.warnings.append(f"Error reading {file_path.name}: {e}")
        
        if total_coverage:
            avg_coverage = sum(total_coverage) / len(total_coverage)
            self.info.append(f"✓ Average coverage: {avg_coverage:.1%} across {len(total_coverage)} folios")
            self.info.append(f"✓ Total unique unknowns: {len(total_unknowns)}")
            
            if avg_coverage < 0.5:
                self.warnings.append(f"Coverage below 50%: {avg_coverage:.1%}")
            elif avg_coverage < 0.6:
                self.info.append(f"Coverage could be improved: {avg_coverage:.1%}")
    
    def run_all_checks(self) -> bool:
        """Run all validation checks"""
        if not self.load_dictionary():
            return False
        
        checks = [
            ("YAML Syntax", self.check_yaml_syntax),
            ("Duplicates", self.check_duplicates),
            ("Required Fields", self.check_required_fields),
            ("Field Formats", self.check_field_formats),
            ("Polysemy Format", self.check_polysemy_format),
            ("Consistency", self.check_consistency),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            if not check_func():
                all_passed = False
        
        return all_passed
    
    def generate_report(self, output_file: str = None):
        """Generate validation report"""
        report = {
            "timestamp": Path(self.dictionary_path).stat().st_mtime,
            "dictionary_size": len(self.vocab_list),
            "polysemy_entries": len(self.polysemy_list),
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "passed": len(self.errors) == 0
        }
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"✓ Report saved to {output_path}")
        
        return report
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*70)
        print("🔍 VALIDATION REPORT")
        print("="*70)
        
        print(f"\n📊 Dictionary Stats:")
        print(f"   • Vocabulary entries: {len(self.vocab_list)}")
        print(f"   • Polysemy entries: {len(self.polysemy_list)}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"   • {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings)-10} more warnings")
        
        if self.info:
            print(f"\n✓ Info:")
            for info in self.info:
                print(f"   {info}")
        
        print("\n" + "="*70)
        
        if len(self.errors) == 0:
            print("✅ VALIDATION PASSED")
        else:
            print("❌ VALIDATION FAILED")
        
        print("="*70)


def main():
    parser = argparse.ArgumentParser(
        description="Validate Voynich dictionary and translations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all checks
  %(prog)s --check-type all
  
  # Check only dictionary
  %(prog)s --check-type dictionary
  
  # Check and generate report
  %(prog)s --check-type all --report-file data/validation_report.json
  
  # Auto-fix issues (if possible)
  %(prog)s --check-type all --fix-auto
        """
    )
    
    parser.add_argument("--check-type",
                       choices=['all', 'dictionary', 'translations', 'consistency'],
                       default='all',
                       help="Type of validation to perform")
    parser.add_argument("--report-file", help="Save report to JSON file")
    parser.add_argument("--fix-auto", action="store_true",
                       help="Automatically fix issues if possible")
    
    args = parser.parse_args()
    
    checker = ValidationChecker()
    
    if args.check_type in ['all', 'dictionary', 'consistency']:
        checker.run_all_checks()
    
    if args.check_type in ['all', 'translations']:
        checker.check_translations_quality()
    
    # Generate report
    if args.report_file:
        checker.generate_report(args.report_file)
    
    # Print summary
    checker.print_summary()
    
    # Return exit code
    return 0 if len(checker.errors) == 0 else 1


if __name__ == "__main__":
    exit(main())

