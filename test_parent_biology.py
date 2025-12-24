#!/usr/bin/env python3
"""
Test to verify PARENT BIOLOGICAL AGES are always valid
Critical bug: Mother/Father must have valid age when ALL children (person + siblings) were born
"""

import sys
sys.path.insert(0, '/home/leucocito/false-identity/src')

from generator import IdentityGenerator
from data_loader import DataLoader
import random

# Initialize
data_loader = DataLoader()
generator = IdentityGenerator(data_loader)
current_year = 2025

# Spain fertility rules
FERTILITY_MIN = 18
FERTILITY_MAX = 45
MIN_FATHER_AGE = 16
MAX_FATHER_AGE = 70

def parse_year(date_str):
    """Parse year from date string"""
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            # DD/MM/YYYY or MM/DD/YYYY (year is last)
            if len(parts[0]) <= 2:
                return int(parts[2])
            # YYYY/MM/DD (year is first)
            else:
                return int(parts[0])
    except:
        pass
    return None

print("="*100)
print("TEST: PARENT BIOLOGICAL AGES - VERIFY FERTILITY RULES FOR ALL CHILDREN")
print("="*100)
print()

issues = []
total_tested = 0
total_siblings_checked = 0

# Test 100 profiles, focusing on older people (70-85) where bug was most common
for i in range(1, 101):
    age = random.randint(70, 85)
    gender = random.choice(['male', 'female'])

    identity = generator.generate(country='spain', gender=gender, min_age=age, max_age=age)
    total_tested += 1

    # Get person's birth year
    person_birth_year = current_year - age

    # Get mother's and father's birth year
    if hasattr(identity, 'family') and identity.family:
        mother = identity.family.get('mother')
        father = identity.family.get('father')
        siblings = identity.family.get('siblings', [])

        if mother:
            mother_birth_date = mother.get('birth_date', '')
            mother_birth_year = parse_year(mother_birth_date)

            if mother_birth_year:
                # Check mother's age when person was born
                mother_age_at_person_birth = person_birth_year - mother_birth_year

                if mother_age_at_person_birth < FERTILITY_MIN:
                    issues.append({
                        'name': identity.full_name,
                        'age': age,
                        'problem': f"Mother was {mother_age_at_person_birth} years old when person was born (MIN: {FERTILITY_MIN})",
                        'mother_birth': mother_birth_year,
                        'person_birth': person_birth_year
                    })
                elif mother_age_at_person_birth > FERTILITY_MAX:
                    issues.append({
                        'name': identity.full_name,
                        'age': age,
                        'problem': f"Mother was {mother_age_at_person_birth} years old when person was born (MAX: {FERTILITY_MAX})",
                        'mother_birth': mother_birth_year,
                        'person_birth': person_birth_year
                    })

                # Check mother's age when each sibling was born
                for sibling in siblings:
                    total_siblings_checked += 1
                    sibling_birth_date = sibling.get('birth_date', '')
                    sibling_birth_year = parse_year(sibling_birth_date)

                    if sibling_birth_year:
                        mother_age_at_sibling_birth = sibling_birth_year - mother_birth_year

                        if mother_age_at_sibling_birth < FERTILITY_MIN:
                            issues.append({
                                'name': identity.full_name,
                                'age': age,
                                'problem': f"Mother was {mother_age_at_sibling_birth} years old when sibling {sibling.get('name', 'Unknown')} was born (MIN: {FERTILITY_MIN})",
                                'mother_birth': mother_birth_year,
                                'sibling_birth': sibling_birth_year,
                                'sibling_name': sibling.get('name', 'Unknown')
                            })
                        elif mother_age_at_sibling_birth > FERTILITY_MAX:
                            issues.append({
                                'name': identity.full_name,
                                'age': age,
                                'problem': f"Mother was {mother_age_at_sibling_birth} years old when sibling {sibling.get('name', 'Unknown')} was born (MAX: {FERTILITY_MAX})",
                                'mother_birth': mother_birth_year,
                                'sibling_birth': sibling_birth_year,
                                'sibling_name': sibling.get('name', 'Unknown')
                            })

        if father:
            father_birth_date = father.get('birth_date', '')
            father_birth_year = parse_year(father_birth_date)

            if father_birth_year:
                # Check father's age when person was born
                father_age_at_person_birth = person_birth_year - father_birth_year

                if father_age_at_person_birth < MIN_FATHER_AGE:
                    issues.append({
                        'name': identity.full_name,
                        'age': age,
                        'problem': f"Father was {father_age_at_person_birth} years old when person was born (MIN: {MIN_FATHER_AGE})",
                        'father_birth': father_birth_year,
                        'person_birth': person_birth_year
                    })
                elif father_age_at_person_birth > MAX_FATHER_AGE:
                    issues.append({
                        'name': identity.full_name,
                        'age': age,
                        'problem': f"Father was {father_age_at_person_birth} years old when person was born (MAX: {MAX_FATHER_AGE})",
                        'father_birth': father_birth_year,
                        'person_birth': person_birth_year
                    })

                # Check father's age when each sibling was born
                for sibling in siblings:
                    sibling_birth_date = sibling.get('birth_date', '')
                    sibling_birth_year = parse_year(sibling_birth_date)

                    if sibling_birth_year:
                        father_age_at_sibling_birth = sibling_birth_year - father_birth_year

                        if father_age_at_sibling_birth < MIN_FATHER_AGE:
                            issues.append({
                                'name': identity.full_name,
                                'age': age,
                                'problem': f"Father was {father_age_at_sibling_birth} years old when sibling {sibling.get('name', 'Unknown')} was born (MIN: {MIN_FATHER_AGE})",
                                'father_birth': father_birth_year,
                                'sibling_birth': sibling_birth_year,
                                'sibling_name': sibling.get('name', 'Unknown')
                            })
                        elif father_age_at_sibling_birth > MAX_FATHER_AGE:
                            issues.append({
                                'name': identity.full_name,
                                'age': age,
                                'problem': f"Father was {father_age_at_sibling_birth} years old when sibling {sibling.get('name', 'Unknown')} was born (MAX: {MAX_FATHER_AGE})",
                                'father_birth': father_birth_year,
                                'sibling_birth': sibling_birth_year,
                                'sibling_name': sibling.get('name', 'Unknown')
                            })

print(f"Tested {total_tested} elderly profiles (ages 70-85)")
print(f"Checked {total_siblings_checked} sibling birth dates")
print()

if issues:
    print(f"🔴 FAILED: Found {len(issues)} biological impossibilities!")
    print()
    for issue in issues[:10]:  # Show first 10
        print(f"❌ {issue['name']} ({issue['age']} años)")
        print(f"   {issue['problem']}")
        if 'mother_birth' in issue:
            print(f"   Mother born: {issue['mother_birth']}")
        if 'father_birth' in issue:
            print(f"   Father born: {issue['father_birth']}")
        if 'person_birth' in issue:
            print(f"   Person born: {issue['person_birth']}")
        if 'sibling_birth' in issue:
            print(f"   Sibling born: {issue['sibling_birth']}")
        print()
    if len(issues) > 10:
        print(f"... and {len(issues) - 10} more issues")
else:
    print("✅ PERFECTO! All parent biological ages are valid!")
    print()
    print("🎉 ALL PARENTS HAD VALID AGE WHEN ALL CHILDREN WERE BORN!")
    print()
    print(f"   Mother age at birth: {FERTILITY_MIN}-{FERTILITY_MAX} years ✓")
    print(f"   Father age at birth: {MIN_FATHER_AGE}-{MAX_FATHER_AGE} years ✓")
    print()

print("\n" + "="*100)
print("SAMPLE: Elderly person with siblings (for manual verification)")
print("="*100)

# Generate one example to show
for _ in range(10):
    identity = generator.generate('spain', min_age=80, max_age=85)
    if hasattr(identity, 'family') and identity.family:
        siblings = identity.family.get('siblings', [])
        if siblings:
            mother = identity.family.get('mother')
            father = identity.family.get('father')

            print(f"\nPerson: {identity.full_name} ({identity.age} años, born {current_year - identity.age})")

            if mother:
                mother_birth_year = parse_year(mother.get('birth_date', ''))
                if mother_birth_year:
                    mother_age_at_birth = (current_year - identity.age) - mother_birth_year
                    print(f"Mother: Born {mother_birth_year} (age {mother_age_at_birth} when person born)")

            if father:
                father_birth_year = parse_year(father.get('birth_date', ''))
                if father_birth_year:
                    father_age_at_birth = (current_year - identity.age) - father_birth_year
                    print(f"Father: Born {father_birth_year} (age {father_age_at_birth} when person born)")

            print(f"\nSiblings ({len(siblings)}):")
            for sib in siblings:
                sib_birth_year = parse_year(sib.get('birth_date', ''))
                if sib_birth_year and mother_birth_year:
                    mother_age = sib_birth_year - mother_birth_year
                    print(f"  - {sib.get('name', 'Unknown')}: Born {sib_birth_year} (mother age {mother_age})")
            break

print()
