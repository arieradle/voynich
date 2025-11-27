#!/usr/bin/env python3
"""
Batch Dictionary Updater
Interactive and batch mode for updating voynich.yaml dictionary
"""

import argparse
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class DictionaryUpdater:
    """Update dictionary with new vocabulary entries"""
    
    def __init__(self, dictionary_path: str = "voynich.yaml"):
        self.dictionary_path = Path(dictionary_path)
        self.dictionary = {}
        self.vocab_list = []
        self.polysemy_list = []
        self.changes_made = []
        
        self.load_dictionary()
    
    def load_dictionary(self):
        """Load current dictionary"""
        if not self.dictionary_path.exists():
            print(f"❌ Dictionary not found: {self.dictionary_path}")
            return False
        
        with open(self.dictionary_path, 'r') as f:
            self.dictionary = yaml.safe_load(f)
        
        rules = self.dictionary.get("voynich_decipherment_rules", {})
        self.vocab_list = rules.get("vocab", [])
        self.polysemy_list = rules.get("polysemy", [])
        
        print(f"✓ Loaded dictionary with {len(self.vocab_list)} entries")
        return True
    
    def create_backup(self):
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = self.dictionary_path.parent / f"voynich.yaml.backup-{timestamp}"
        
        shutil.copy2(self.dictionary_path, backup_path)
        print(f"✓ Backup created: {backup_path}")
        return backup_path
    
    def word_exists(self, word: str) -> bool:
        """Check if word already in dictionary"""
        for entry in self.vocab_list:
            if entry.get("word") == word:
                return True
        return False
    
    def validate_entry(self, entry: Dict) -> Tuple[bool, List[str]]:
        """Validate dictionary entry format"""
        errors = []
        
        # Required fields
        if not entry.get("word"):
            errors.append("Missing 'word' field")
        if not entry.get("latin"):
            errors.append("Missing 'latin' field")
        if not entry.get("description"):
            errors.append("Missing 'description' field")
        
        # Field format validation
        word = entry.get("word", "")
        if word:
            if not word.islower():
                errors.append(f"Word '{word}' should be lowercase")
            if not word.isalpha():
                errors.append(f"Word '{word}' should contain only letters")
        
        # Check for duplicate
        if word and self.word_exists(word):
            errors.append(f"Word '{word}' already in dictionary")
        
        return len(errors) == 0, errors
    
    def add_entry(self, word: str, latin: str, description: str, 
                  context: str = None) -> bool:
        """Add single vocabulary entry"""
        entry = {
            "word": word,
            "latin": latin,
            "description": description
        }
        
        if context:
            entry["context"] = context
        
        # Validate
        valid, errors = self.validate_entry(entry)
        if not valid:
            print(f"❌ Validation failed for '{word}':")
            for error in errors:
                print(f"   • {error}")
            return False
        
        # Add to vocab list
        self.vocab_list.append(entry)
        self.changes_made.append(f"Added: {word} → {latin}")
        
        print(f"✓ Added: {word} → {latin}")
        return True
    
    def add_polysemy_entry(self, word: str, meanings: List[Dict], 
                          base: str) -> bool:
        """Add polysemous entry"""
        entry = {
            "word": word,
            "meanings": meanings,
            "base": base
        }
        
        # Check if word exists
        if not self.word_exists(word):
            print(f"⚠️  Word '{word}' not in vocabulary yet")
            print(f"   Add to vocabulary first, then add polysemy")
            return False
        
        # Check if polysemy entry already exists
        for poly in self.polysemy_list:
            if poly.get("word") == word:
                print(f"⚠️  Polysemy entry for '{word}' already exists")
                return False
        
        self.polysemy_list.append(entry)
        self.changes_made.append(f"Added polysemy: {word}")
        
        print(f"✓ Added polysemy for: {word}")
        return True
    
    def import_from_file(self, file_path: str) -> int:
        """Import entries from JSON or CSV file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 0
        
        if file_path.suffix == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            print(f"❌ Unsupported file format: {file_path.suffix}")
            return 0
        
        # Handle different JSON formats
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict) and "words" in data:
            entries = data["words"]
        else:
            entries = [data]
        
        added = 0
        for entry in entries:
            word = entry.get("word", "")
            latin = entry.get("latin", entry.get("suggested_latin", ""))
            description = entry.get("description", entry.get("reasoning", ""))
            context = entry.get("context", None)
            
            if word and latin and description:
                if self.add_entry(word, latin, description, context):
                    added += 1
        
        print(f"\n✓ Imported {added} entries from {file_path}")
        return added
    
    def save_dictionary(self) -> bool:
        """Save updated dictionary"""
        try:
            # Update the dictionary structure
            self.dictionary["voynich_decipherment_rules"]["vocab"] = self.vocab_list
            self.dictionary["voynich_decipherment_rules"]["polysemy"] = self.polysemy_list
            
            # Write to file
            with open(self.dictionary_path, 'w') as f:
                yaml.dump(self.dictionary, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            
            print(f"\n✓ Dictionary saved to {self.dictionary_path}")
            return True
        except Exception as e:
            print(f"\n❌ Error saving dictionary: {e}")
            return False
    
    def interactive_mode(self):
        """Interactive mode for adding words"""
        print("\n" + "="*70)
        print("📝 INTERACTIVE DICTIONARY UPDATE")
        print("="*70)
        print("\nEnter vocabulary entries (or 'done' to finish):")
        print("Format: word|latin|description")
        print("Example: kokaiin|maturat|appears near fruits/seeds\n")
        
        while True:
            try:
                user_input = input("➤ ").strip()
                
                if user_input.lower() in ['done', 'exit', 'quit', '']:
                    break
                
                if '|' not in user_input:
                    print("⚠️  Invalid format. Use: word|latin|description")
                    continue
                
                parts = user_input.split('|')
                if len(parts) < 3:
                    print("⚠️  Need at least 3 fields: word|latin|description")
                    continue
                
                word = parts[0].strip()
                latin = parts[1].strip()
                description = parts[2].strip()
                context = parts[3].strip() if len(parts) > 3 else None
                
                self.add_entry(word, latin, description, context)
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
        
        # Summary
        print(f"\n✓ Added {len(self.changes_made)} entries")
        if self.changes_made:
            print("\nChanges:")
            for change in self.changes_made:
                print(f"   • {change}")
    
    def show_summary(self):
        """Show summary of changes"""
        if not self.changes_made:
            print("\n⚠️  No changes made")
            return
        
        print("\n" + "="*70)
        print("📊 CHANGES SUMMARY")
        print("="*70)
        print(f"\nTotal changes: {len(self.changes_made)}")
        print("\nChanges made:")
        for change in self.changes_made:
            print(f"   • {change}")
        print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description="Update Voynich dictionary with new vocabulary",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  %(prog)s --interactive --backup
  
  # Import from JSON file
  %(prog)s --import-file data/approved_words.json --backup
  
  # Add single word
  %(prog)s --add-word kokaiin --latin maturat --description "ripens"
  
  # Validate only (no changes)
  %(prog)s --import-file words.json --validate-only
        """
    )
    
    parser.add_argument("--interactive", action="store_true",
                       help="Interactive mode for adding words")
    parser.add_argument("--import-file", help="Import from JSON file")
    parser.add_argument("--add-word", help="Add single word")
    parser.add_argument("--latin", help="Latin translation for single word")
    parser.add_argument("--description", help="Description for single word")
    parser.add_argument("--backup", action="store_true",
                       help="Create backup before changes")
    parser.add_argument("--validate-only", action="store_true",
                       help="Validate without saving")
    parser.add_argument("--yes", action="store_true",
                       help="Auto-approve changes (non-interactive)")
    
    args = parser.parse_args()
    
    updater = DictionaryUpdater()
    
    # Create backup if requested
    if args.backup and not args.validate_only:
        updater.create_backup()
    
    # Different modes
    if args.interactive:
        updater.interactive_mode()
    
    elif args.import_file:
        updater.import_from_file(args.import_file)
    
    elif args.add_word:
        if not args.latin or not args.description:
            print("❌ --latin and --description required with --add-word")
            return 1
        updater.add_entry(args.add_word, args.latin, args.description)
    
    else:
        parser.print_help()
        return 0
    
    # Show summary
    updater.show_summary()
    
    # Save if not validate-only
    if not args.validate_only:
        if updater.changes_made:
            if args.yes:
                response = 'yes'
                print("\n✓ Auto-approving changes (--yes flag)")
            else:
                print("\nSave changes? (yes/no): ", end='')
                response = input().strip().lower()
            
            if response in ['yes', 'y']:
                if updater.save_dictionary():
                    print("\n✓ Dictionary updated successfully!")
                else:
                    print("\n❌ Failed to save dictionary")
                    return 1
            else:
                print("\n⚠️  Changes discarded")
        else:
            print("\n⚠️  No changes to save")
    else:
        print("\n✓ Validation complete (no changes saved)")


if __name__ == "__main__":
    main()

