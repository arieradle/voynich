#!/usr/bin/env python3
"""
Interactive tool for reviewing translation gaps and updating dictionary

This script helps you:
1. Review unknown words from translations
2. Research patterns and context
3. Add new entries to voynich.yaml
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter


class DictionaryUpdater:
    """Interactive dictionary updater"""
    
    def __init__(self, config_path: str = "voynich.yaml", suggestions_path: str = "data/dictionary_suggestions.json"):
        self.config_path = Path(config_path)
        self.suggestions_path = Path(suggestions_path)
        self.config = self._load_config()
        self.suggestions = self._load_suggestions()
    
    def _load_config(self) -> Dict:
        """Load current configuration"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_suggestions(self) -> List[Dict]:
        """Load suggestions if available"""
        if self.suggestions_path.exists():
            with open(self.suggestions_path, 'r') as f:
                return json.load(f)
        return []
    
    def show_suggestions(self, limit: int = 10):
        """Display top suggestions"""
        print("\n" + "="*70)
        print("📋 DICTIONARY UPDATE SUGGESTIONS")
        print("="*70)
        
        if not self.suggestions:
            print("\n⚠️  No suggestions found. Run analyze_gaps.py first.")
            return
        
        for i, sug in enumerate(self.suggestions[:limit], 1):
            print(f"\n{i}. Word: {sug['word']}")
            print(f"   Frequency: {sug['frequency']}x")
            print(f"   Contexts: {', '.join(sug['suggested_contexts'])}")
            print(f"   Suggested: {sug['suggested_latin']}")
            print(f"   Reasoning: {sug['reasoning']}")
    
    def add_vocabulary_entry(self, word: str, latin: str, description: str):
        """Add a new vocabulary entry to config"""
        vocab = self.config["voynich_decipherment_rules"].get("vocab", [])
        
        # Check if already exists
        for entry in vocab:
            if entry.get("word") == word:
                print(f"⚠️  Word '{word}' already exists. Update manually if needed.")
                return False
        
        # Add new entry
        new_entry = {
            "word": word,
            "description": description,
            "latin": latin
        }
        vocab.append(new_entry)
        
        print(f"✓ Added: {word} → {latin}")
        return True
    
    def add_polysemy_entry(self, word: str, meanings: List[Dict], base: str):
        """Add a polysemous word"""
        polysemy = self.config["voynich_decipherment_rules"].get("polysemy", [])
        
        # Check if already exists
        for entry in polysemy:
            if entry.get("word") == word:
                print(f"⚠️  Polysemy for '{word}' already exists. Update manually if needed.")
                return False
        
        # Add new entry
        new_entry = {
            "word": word,
            "meanings": meanings,
            "base": base
        }
        polysemy.append(new_entry)
        
        print(f"✓ Added polysemy: {word} (base: {base})")
        return True
    
    def save_config(self):
        """Save updated configuration"""
        # Create backup
        backup_path = self.config_path.with_suffix('.yaml.bak')
        with open(self.config_path, 'r') as f:
            content = f.read()
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✓ Backup created: {backup_path}")
        
        # Save updated config
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        print(f"✓ Dictionary updated: {self.config_path}")
    
    def quick_add_examples(self):
        """Add example entries based on README analysis"""
        print("\n🔧 Adding example entries from manual analysis...")
        
        # Based on the README examples and deterministic_translator.py
        examples = [
            # High priority from folio 14v analysis
            ("oty", "ex", "source, appears in multiple folios"),
            ("shy", "hic", "location marker, frequent"),
            ("dy", "et", "conjunction, very frequent"),
            ("chy", "in", "preposition for containment"),
            ("cthy", "terra", "earth/soil in herbal context"),
            ("chol", "caulis", "stem in herbal context"),
            ("ty", "ad", "direction marker"),
            ("ychy", "crescit", "growth verb"),
            ("oky", "extendit", "extends, spreads"),
            ("ksho", "multum", "much, many"),
            ("ykshy", "saepe", "often"),
            ("darody", "materia", "material/substance"),
            ("chky", "altum", "tall, high"),
            ("cthor", "caelum", "sky, heaven"),
            ("choky", "magnus", "large, great"),
            ("choty", "parvus", "small"),
            ("odyd", "movet", "moves"),
            ("kchy", "facit", "makes, does"),
            ("dshy", "hic", "here (variant)"),
            ("dardy", "est", "is (variant)"),
            ("dair", "gratia", "for benefit"),
            ("dam", "finis", "end, completion"),
        ]
        
        added = 0
        for word, latin, desc in examples:
            if self.add_vocabulary_entry(word, latin, desc):
                added += 1
        
        print(f"\n✓ Added {added} new vocabulary entries")
    
    def interactive_mode(self):
        """Interactive review mode"""
        print("\n" + "="*70)
        print("🎯 INTERACTIVE DICTIONARY UPDATE")
        print("="*70)
        print("\nCommands:")
        print("  show [n]     - Show top n suggestions (default: 10)")
        print("  add          - Add a new word")
        print("  examples     - Add example entries from analysis")
        print("  save         - Save changes")
        print("  quit         - Exit without saving")
        
        while True:
            try:
                cmd = input("\n>>> ").strip().lower()
                
                if not cmd:
                    continue
                
                if cmd == "quit" or cmd == "q":
                    print("👋 Exiting without saving")
                    break
                
                elif cmd == "save" or cmd == "s":
                    self.save_config()
                    print("✓ Changes saved!")
                
                elif cmd.startswith("show"):
                    parts = cmd.split()
                    limit = int(parts[1]) if len(parts) > 1 else 10
                    self.show_suggestions(limit)
                
                elif cmd == "add" or cmd == "a":
                    word = input("  Word: ").strip()
                    latin = input("  Latin: ").strip()
                    desc = input("  Description: ").strip()
                    
                    if word and latin:
                        self.add_vocabulary_entry(word, latin, desc)
                
                elif cmd == "examples" or cmd == "ex":
                    self.quick_add_examples()
                
                else:
                    print(f"❓ Unknown command: {cmd}")
            
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Review and update dictionary")
    parser.add_argument("--show", type=int, help="Show top N suggestions")
    parser.add_argument("--add-examples", action="store_true", help="Add example entries")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    updater = DictionaryUpdater()
    
    if args.add_examples:
        updater.quick_add_examples()
        updater.save_config()
    elif args.show:
        updater.show_suggestions(args.show)
    elif args.interactive:
        updater.interactive_mode()
    else:
        # Default: show suggestions
        updater.show_suggestions(10)
        print("\n💡 Tip: Use --interactive for interactive mode")
        print("        Use --add-examples to add curated examples")


if __name__ == "__main__":
    main()

