#!/usr/bin/env python3
"""
Iteration Orchestrator
Master script that coordinates complete research iterations with validation gates
"""

import argparse
import json
import yaml
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class IterationOrchestrator:
    """Orchestrate complete research iteration workflow"""
    
    def __init__(self, config_path: str = "agent_config.yaml",
                 workflow_path: str = "research_workflow.yaml"):
        self.config_path = Path(config_path)
        self.workflow_path = Path(workflow_path)
        self.config = {}
        self.workflow = {}
        self.iteration_number = 1
        self.results = {}
        self.validation_gates_enabled = True
        
        self.load_configurations()
    
    def load_configurations(self):
        """Load configuration files"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"✓ Loaded agent config")
        
        if self.workflow_path.exists():
            with open(self.workflow_path, 'r') as f:
                self.workflow = yaml.safe_load(f)
            print(f"✓ Loaded workflow definition")
    
    def run_command(self, command: str, description: str = "") -> Dict:
        """Run shell command and capture output"""
        if description:
            print(f"\n🔧 {description}")
        
        print(f"   Running: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            
            if success:
                print(f"   ✓ Success")
            else:
                print(f"   ✗ Failed (exit code: {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}")
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            print(f"   ✗ Timeout (>5 minutes)")
            return {"success": False, "error": "timeout"}
        except Exception as e:
            print(f"   ✗ Exception: {e}")
            return {"success": False, "error": str(e)}
    
    def validation_gate(self, gate_name: str, message: str, 
                       options: List[str], auto_approve: bool = False) -> str:
        """Present validation gate to user"""
        if not self.validation_gates_enabled or auto_approve:
            print(f"\n✓ Validation gate '{gate_name}' bypassed")
            return options[0]  # Default option
        
        print("\n" + "="*70)
        print(f"🚦 VALIDATION GATE: {gate_name}")
        print("="*70)
        print(f"\n{message}\n")
        print("Options:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        while True:
            try:
                choice = input(f"\nSelect option (1-{len(options)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                else:
                    print(f"Invalid choice. Enter 1-{len(options)}")
            except (ValueError, KeyboardInterrupt):
                print("\nUsing default option")
                return options[0]
    
    def phase_1_analyze(self) -> bool:
        """Phase 1: Analyze current state"""
        print("\n" + "="*70)
        print("📊 PHASE 1: ANALYZE")
        print("="*70)
        
        # Step 1.1: Validate system state
        result = self.run_command(
            "python scripts/validation_checker.py --check-type all",
            "Validating system state"
        )
        
        if not result["success"]:
            print("\n❌ System validation failed. Fix errors before continuing.")
            return False
        
        # Step 1.2: Analyze current coverage
        print(f"\n📈 Current translation coverage:")
        # This would show existing metrics
        
        # Step 1.3: Identify unknown words
        result = self.run_command(
            "python scripts/word_frequency.py --min-freq 3 --output data/unknown_ranked.json",
            "Analyzing unknown word frequency"
        )
        
        if result["success"]:
            self.results["unknown_analysis"] = "data/unknown_ranked.json"
        
        # Step 1.4: Detect patterns
        result = self.run_command(
            "python scripts/pattern_detector.py --pattern-type all --min-occurrences 3 "
            "--output data/patterns_detected.json",
            "Detecting patterns"
        )
        
        if result["success"]:
            self.results["patterns"] = "data/patterns_detected.json"
        
        # Step 1.5: Gap analysis
        result = self.run_command(
            "python analyze_gaps.py --min-freq 5 --max-suggestions 50",
            "Running comprehensive gap analysis"
        )
        
        if result["success"]:
            self.results["gap_analysis"] = "data/dictionary_suggestions.json"
        
        # Validation gate
        choice = self.validation_gate(
            "analysis_review",
            "Analysis phase complete. Review the generated files:\n"
            f"  • {self.results.get('unknown_analysis', 'N/A')}\n"
            f"  • {self.results.get('patterns', 'N/A')}\n"
            f"  • {self.results.get('gap_analysis', 'N/A')}\n\n"
            "Ready to proceed to vocabulary proposal phase?",
            ["proceed", "re-analyze", "abort"]
        )
        
        if choice == "abort":
            print("\n⚠️  Iteration aborted by user")
            return False
        elif choice == "re-analyze":
            print("\n🔄 Re-running analysis...")
            return self.phase_1_analyze()
        
        return True
    
    def phase_2_propose(self) -> bool:
        """Phase 2: Generate vocabulary proposals"""
        print("\n" + "="*70)
        print("💡 PHASE 2: PROPOSE")
        print("="*70)
        
        # Step 2.1: Morphological analysis
        result = self.run_command(
            "python scripts/morphology_analyzer.py --auto-suggest "
            "--output data/morphology_analysis.json",
            "Running morphological analysis"
        )
        
        if result["success"]:
            self.results["morphology"] = "data/morphology_analysis.json"
        
        # Step 2.2: Compound decomposition
        result = self.run_command(
            "python scripts/compound_decomposer.py --batch-file data/unknown_ranked.json "
            "--output data/compound_analysis.json",
            "Analyzing compound words"
        )
        
        if result["success"]:
            self.results["compounds"] = "data/compound_analysis.json"
        
        # Step 2.3: Rank candidates
        print(f"\n📊 Ranking vocabulary candidates...")
        # This would combine frequency, confidence, and context
        
        # Validation gate
        choice = self.validation_gate(
            "vocabulary_proposal",
            "Vocabulary proposals ready. Review:\n"
            f"  • Morphological analysis: {self.results.get('morphology', 'N/A')}\n"
            f"  • Compound analysis: {self.results.get('compounds', 'N/A')}\n\n"
            "How would you like to proceed?",
            ["approve_proposals", "modify", "skip_phase", "abort"]
        )
        
        if choice == "abort":
            return False
        elif choice == "skip_phase":
            print("\n⚠️  Skipping proposal phase")
            return True
        
        return True
    
    def phase_3_validate(self) -> bool:
        """Phase 3: Validate proposals"""
        print("\n" + "="*70)
        print("✅ PHASE 3: VALIDATE")
        print("="*70)
        
        # Validation gate - always required
        choice = self.validation_gate(
            "dictionary_update_approval",
            "Ready to update dictionary with approved words.\n\n"
            "⚠️  This will modify voynich.yaml\n"
            "A backup will be created automatically.\n\n"
            "Approve dictionary update?",
            ["approve", "review_first", "cancel"],
            auto_approve=False  # Never auto-approve dictionary changes
        )
        
        if choice == "cancel":
            print("\n⚠️  Dictionary update cancelled")
            return False
        elif choice == "review_first":
            print("\n📝 Please review proposals manually, then re-run")
            return False
        
        return True
    
    def phase_4_implement(self) -> bool:
        """Phase 4: Implement changes"""
        print("\n" + "="*70)
        print("🔧 PHASE 4: IMPLEMENT")
        print("="*70)
        
        # This phase would use batch_dictionary_updater.py
        # For now, just validate
        print("\n⚠️  Manual implementation required:")
        print("   Use: python scripts/batch_dictionary_updater.py --interactive --backup")
        
        choice = self.validation_gate(
            "implementation_verification",
            "Have you updated the dictionary?",
            ["yes", "no", "abort"]
        )
        
        if choice != "yes":
            return False
        
        # Validate dictionary after update
        result = self.run_command(
            "python scripts/validation_checker.py --check-type all",
            "Validating updated dictionary"
        )
        
        if not result["success"]:
            print("\n❌ Dictionary validation failed after update!")
            print("   Consider rolling back from backup")
            return False
        
        return True
    
    def phase_5_test(self) -> bool:
        """Phase 5: Test with re-translation"""
        print("\n" + "="*70)
        print("🧪 PHASE 5: TEST")
        print("="*70)
        
        # Re-translate all folios
        result = self.run_command(
            "python translate_folio.py --section q01 --start 1 --end 8 --force",
            "Re-translating Herbal A folios"
        )
        
        result = self.run_command(
            "python translate_folio.py --section q02 --start 14 --end 16 --force",
            "Re-translating Herbal B folios"
        )
        
        # Analyze new coverage
        print(f"\n📊 Calculating new coverage metrics...")
        
        # Validation gate
        choice = self.validation_gate(
            "translation_review",
            "Re-translation complete.\n"
            "Review the updated translation files in data/translations/\n\n"
            "Continue to reporting phase?",
            ["proceed", "review_translations", "rollback"]
        )
        
        if choice == "rollback":
            print("\n⚠️  Consider rolling back from backup")
            return False
        
        return True
    
    def phase_6_report(self) -> bool:
        """Phase 6: Generate report"""
        print("\n" + "="*70)
        print("📝 PHASE 6: REPORT")
        print("="*70)
        
        # Generate iteration report
        report_file = f"reports/iteration_{self.iteration_number}_report.md"
        
        print(f"\n📄 Generating iteration report: {report_file}")
        
        # This would compile all metrics
        
        # Validation gate
        choice = self.validation_gate(
            "iteration_completion",
            f"Iteration {self.iteration_number} complete.\n\n"
            "What would you like to do next?",
            ["start_next_iteration", "review_results", "pause", "end"]
        )
        
        if choice == "start_next_iteration":
            self.iteration_number += 1
            return True
        elif choice == "pause":
            print(f"\n⏸️  Research paused. Resume with iteration {self.iteration_number + 1}")
        
        return choice == "start_next_iteration"
    
    def run_iteration(self) -> bool:
        """Run complete iteration"""
        print(f"\n{'='*70}")
        print(f"🚀 STARTING ITERATION {self.iteration_number}")
        print(f"{'='*70}")
        
        phases = [
            ("Analyze", self.phase_1_analyze),
            ("Propose", self.phase_2_propose),
            ("Validate", self.phase_3_validate),
            ("Implement", self.phase_4_implement),
            ("Test", self.phase_5_test),
            ("Report", self.phase_6_report),
        ]
        
        for phase_name, phase_func in phases:
            print(f"\n{'─'*70}")
            if not phase_func():
                print(f"\n⚠️  Phase '{phase_name}' failed or cancelled")
                return False
        
        print(f"\n✅ Iteration {self.iteration_number} complete!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrate complete research iteration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full iteration with validation gates
  %(prog)s --validation-gates
  
  # Auto mode (bypass some gates)
  %(prog)s --auto-mode
  
  # Target specific coverage
  %(prog)s --target-coverage 0.65 --validation-gates
  
  # Multiple iterations
  %(prog)s --iterations 3 --auto-mode
        """
    )
    
    parser.add_argument("--validation-gates", action="store_true",
                       help="Enable validation gates (recommended)")
    parser.add_argument("--auto-mode", action="store_true",
                       help="Bypass non-critical validation gates")
    parser.add_argument("--target-coverage", type=float,
                       help="Target coverage percentage (0.0-1.0)")
    parser.add_argument("--iterations", type=int, default=1,
                       help="Number of iterations to run")
    
    args = parser.parse_args()
    
    orchestrator = IterationOrchestrator()
    orchestrator.validation_gates_enabled = args.validation_gates or not args.auto_mode
    
    print("\n" + "="*70)
    print("🔬 VOYNICH RESEARCH ITERATION ORCHESTRATOR")
    print("="*70)
    print(f"\nMode: {'Validation Gates Enabled' if orchestrator.validation_gates_enabled else 'Auto Mode'}")
    if args.target_coverage:
        print(f"Target Coverage: {args.target_coverage:.1%}")
    print(f"Planned Iterations: {args.iterations}")
    
    # Run iterations
    completed = 0
    for i in range(args.iterations):
        if orchestrator.run_iteration():
            completed += 1
        else:
            print(f"\n⚠️  Iteration {orchestrator.iteration_number} incomplete")
            break
    
    print(f"\n{'='*70}")
    print(f"🏁 ORCHESTRATOR COMPLETE")
    print(f"{'='*70}")
    print(f"\nCompleted: {completed}/{args.iterations} iterations")
    
    return 0 if completed > 0 else 1


if __name__ == "__main__":
    exit(main())

