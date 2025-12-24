#!/usr/bin/env python3
"""
Generate a single elderly person and show detailed parent info
"""

import sys
sys.path.insert(0, '/home/leucocito/false-identity/src')

from generator import IdentityGenerator
from data_loader import DataLoader

loader = DataLoader()
gen = IdentityGenerator(loader)
current_year = 2025

def parse_year(date_str):
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            if len(parts[0]) <= 2:
                return int(parts[2])
            else:
                return int(parts[0])
    except:
        pass
    return None

# Generate one 70-year old person
for _ in range(5):
    print("\n" + "="*80)
    identity = gen.generate('spain', min_age=70, max_age=70)

    person_birth_year = current_year - identity.age

    print(f"Person: {identity.full_name} ({identity.age} años, born {person_birth_year})")

    if hasattr(identity, 'family') and identity.family:
        mother = identity.family.get('mother')
        father = identity.family.get('father')

        if mother:
            mother_birth_date = mother.get('birth_date', '')
            mother_birth_year = parse_year(mother_birth_date)
            if mother_birth_year:
                mother_age_at_birth = person_birth_year - mother_birth_year
                status = "✅" if mother_age_at_birth >= 18 else "🔴"
                print(f"{status} Mother: Born {mother_birth_year}, age {mother_age_at_birth} when person born")

        if father:
            father_birth_date = father.get('birth_date', '')
            father_birth_year = parse_year(father_birth_date)
            if father_birth_year:
                father_age_at_birth = person_birth_year - father_birth_year
                status = "✅" if father_age_at_birth >= 16 else "🔴"
                print(f"{status} Father: Born {father_birth_year}, age {father_age_at_birth} when person born")

print("\n")
