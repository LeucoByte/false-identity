#!/usr/bin/env python3
"""Final comprehensive test for marriage dates and education bugs"""

import sys
sys.path.insert(0, '/home/leucocito/false-identity/src')

from generator import IdentityGenerator
from data_loader import DataLoader

# Initialize
data_loader = DataLoader()
generator = IdentityGenerator(data_loader)
current_year = 2025

print("=" * 100)
print("FINAL COMPREHENSIVE BUG TEST")
print("=" * 100)
print()

# Test both bugs
future_dates = []
education_bugs = []
samples = []

print("Testing 100 Russian profiles...")
for i in range(100):
    identity = generator.generate(country='russia')

    # Check 1: Future marriage dates
    if hasattr(identity, 'family') and identity.family:
        marriages = []

        # Check partner (current relationship)
        if identity.family.get('partner'):
            partner = identity.family['partner']
            if partner.get('marriage_date'):
                marriages.append(('current partner', partner['marriage_date']))

        # Check ex-partners
        for ex in identity.family.get('ex_partners', []):
            if ex.get('marriage_date'):
                marriages.append(('ex-partner', ex['marriage_date']))

        # Check relationship history
        for rel in identity.family.get('relationship_history', []):
            if rel.get('marriage_date'):
                marriages.append(('relationship history', rel['marriage_date']))

        for source, marriage_date in marriages:
            if marriage_date:
                try:
                    # Parse date (format: DD.MM.YYYY or DD/MM/YYYY for Russia)
                    parts = marriage_date.replace('/', '.').split('.')
                    if len(parts) == 3:
                        year = int(parts[2]) if len(parts[2]) == 4 else int(parts[0])
                        if year > current_year:
                            future_dates.append({
                                'name': identity.full_name,
                                'age': identity.age,
                                'date': marriage_date,
                                'year': year,
                                'source': source
                            })
                except:
                    pass

    # Check 2: Education level mismatches
    job = getattr(identity, 'job', None)
    education = getattr(identity, 'education', None)

    if job and education and 'Student of' in job:
        # University student - collect sample
        samples.append({
            'name': identity.full_name,
            'age': identity.age,
            'job': job,
            'education': education
        })

        # Check for bug: university student with Secondary education
        if 'Secondary' in education and 'in progress' in education:
            education_bugs.append({
                'name': identity.full_name,
                'age': identity.age,
                'job': job,
                'education': education
            })

# Report results
print("\n" + "=" * 100)
print("RESULTS")
print("=" * 100)

print(f"\n1. FUTURE MARRIAGE DATES TEST")
print(f"   Profiles tested: 100")
print(f"   Future dates found: {len(future_dates)}")
if future_dates:
    print("   ❌ BUG FOUND!")
    for bug in future_dates[:5]:  # Show first 5
        print(f"      - {bug['name']} (age {bug['age']})")
        print(f"        Marriage date: {bug['date']} (year {bug['year']} > {current_year})")
        print(f"        Source: {bug['source']}")
    if len(future_dates) > 5:
        print(f"      ... and {len(future_dates) - 5} more")
else:
    print("   ✅ PASSED - No future marriage dates!")

print(f"\n2. EDUCATION LEVEL MISMATCH TEST")
print(f"   Profiles tested: 100")
print(f"   University students found: {len(samples)}")
print(f"   Education bugs found: {len(education_bugs)}")
if education_bugs:
    print("   ❌ BUG FOUND!")
    for bug in education_bugs:
        print(f"      - {bug['name']} (age {bug['age']})")
        print(f"        Job: {bug['job']}")
        print(f"        Education: {bug['education']}")
        print(f"        Expected: Bachelor's degree (in progress)")
else:
    print("   ✅ PASSED - All university students have correct education!")

# Show some correct samples
if samples and not education_bugs:
    print("\n   Sample correct university students:")
    for sample in samples[:3]:
        print(f"      ✓ {sample['name']} (age {sample['age']})")
        print(f"        Job: {sample['job']}")
        print(f"        Education: {sample['education']}")

print("\n" + "=" * 100)
total_bugs = len(future_dates) + len(education_bugs)
if total_bugs == 0:
    print("🎉 ALL TESTS PASSED! NO BUGS FOUND!")
else:
    print(f"❌ TOTAL BUGS FOUND: {total_bugs}")
print("=" * 100)

sys.exit(0 if total_bugs == 0 else 1)
