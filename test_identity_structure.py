#!/usr/bin/env python3
"""Check identity object structure"""

import sys
sys.path.insert(0, '/home/leucocito/false-identity/src')

from generator import IdentityGenerator
from data_loader import DataLoader

# Initialize
data_loader = DataLoader()
generator = IdentityGenerator(data_loader)

print("=" * 80)
print("CHECKING IDENTITY OBJECT STRUCTURE")
print("=" * 80)
print()

identity = generator.generate(country='russia', min_age=20, max_age=22)

print(f"Identity type: {type(identity)}")
print(f"Identity dir: {[attr for attr in dir(identity) if not attr.startswith('_')]}")
print()

# Check common attributes
attrs_to_check = ['full_name', 'age', 'employment', 'education', 'marital_status',
                  'family', 'job', 'current_job', 'occupation']

for attr in attrs_to_check:
    if hasattr(identity, attr):
        value = getattr(identity, attr)
        print(f"✓ {attr}: {type(value).__name__} = {str(value)[:100]}")
    else:
        print(f"✗ {attr}: NOT FOUND")

print()
print("=" * 80)

# Try to print the whole identity as dict if possible
if hasattr(identity, '__dict__'):
    print("Full identity.__dict__:")
    import json
    try:
        print(json.dumps(identity.__dict__, indent=2, default=str))
    except:
        print(identity.__dict__)
