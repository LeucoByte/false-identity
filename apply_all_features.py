#!/usr/bin/env python3
"""
Script to apply all remaining features systematically.
This will be executed once to implement all changes.
"""

import re
from pathlib import Path

def main():
    print("="*80)
    print("APPLYING ALL FINAL FEATURES")
    print("="*80)
    print()

    base_dir = Path(__file__).parent

    # Feature implementations
    features_applied = []

    # 1. Remove landline phone logic from rules
    print("1. Removing landline phones from rules...")
    spain_rules = base_dir / "data" / "countries" / "spain" / "rules.txt"
    if spain_rules.exists():
        with open(spain_rules, 'r') as f:
            rules_content = f.read()

        # Remove landline references
        rules_content = re.sub(r'landline_probability=.*\n', '', rules_content)
        rules_content = re.sub(r'landline_prefix=.*\n', '', rules_content)

        with open(spain_rules, 'w') as f:
            f.write(rules_content)

        features_applied.append("✓ Removed landline phones")

    print()
    for feature in features_applied:
        print(feature)

    print()
    print("="*80)
    print(f"Applied {len(features_applied)} features successfully")
    print("="*80)

if __name__ == "__main__":
    main()
