"""
Janani AI - Demo Mode Switcher
Quick CLI utility to switch between demo modes

Usage:
    python switch_mode.py
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_demo import DemoMode, set_demo_mode, print_current_config, MODE_CONFIGS


def main():
    print("\n" + "=" * 60)
    print("🎯 JANANI DEMO MODE SWITCHER")
    print("=" * 60)
    print("\nSelect a mode:\n")
    
    print("  1. 🚀 SPEED MODE (3-5s responses)")
    print("     └── Best for: 2-minute hackathon demo")
    print("     └── Features: Core only, fast responses")
    print()
    
    print("  2. ⚖️  BALANCED MODE (8-10s responses)")
    print("     └── Best for: Mixed demo with some features")
    print("     └── Features: Dialect, Memory, Empathy")
    print()
    
    print("  3. 🔬 FULL MODE (15-20s responses)")
    print("     └── Best for: Q&A deep dive, feature showcase")
    print("     └── Features: ALL features enabled")
    print()
    
    print("-" * 60)
    
    try:
        choice = input("\nEnter your choice (1/2/3): ").strip()
        
        if choice == "1":
            config = set_demo_mode(DemoMode.SPEED)
            print("\n🚀 SPEED MODE ACTIVATED!")
            print("   → Responses will be fast (3-5s)")
            print("   → Perfect for 2-minute demo")
            
        elif choice == "2":
            config = set_demo_mode(DemoMode.BALANCED)
            print("\n⚖️  BALANCED MODE ACTIVATED!")
            print("   → Responses will be medium (8-10s)")
            print("   → Dialect + Memory + Empathy enabled")
            
        elif choice == "3":
            config = set_demo_mode(DemoMode.FULL)
            print("\n🔬 FULL MODE ACTIVATED!")
            print("   → Responses will be thorough (15-20s)")
            print("   → ALL features enabled for showcase")
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
            return
        
        print("\n" + "-" * 60)
        print("⚠️  IMPORTANT: Restart the server for changes to take effect!")
        print("   Run: python main.py")
        print("-" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
