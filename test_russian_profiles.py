#!/usr/bin/env python3
"""
Generate Russian profiles of different ages to test the new data
"""

import sys
sys.path.insert(0, 'src')
from generator import IdentityGenerator
from data_loader import DataLoader

loader = DataLoader()
gen = IdentityGenerator(loader)

print("="*100)
print("RUSSIAN IDENTITY PROFILES - TESTING ALL AGES")
print("="*100)

# Test different age groups
ages_to_test = [
    (20, "Very Young - Modern Russia"),
    (30, "Young Adult - Post-Soviet"),
    (45, "Adult - Transition Generation"),
    (60, "Older Adult - Late Soviet"),
    (70, "Senior - Soviet Era"),
    (80, "Elderly - Stalin Era")
]

for age, description in ages_to_test:
    print("\n" + "="*100)
    print(f"{description} ({age} years old)")
    print("="*100)

    identity = gen.generate('russia', min_age=age, max_age=age)

    # Show basic info
    print(f"\nName: {identity.full_name}")
    print(f"Age: {identity.age}")
    print(f"Gender: {identity.gender}")
    print(f"City: {identity.city}")
    print(f"Job: {identity.job}")
    print(f"Education: {identity.education}")

    # Show phone
    if hasattr(identity, 'phone'):
        print(f"Phone: {identity.phone}")

    # Show regional characteristics (historical/cultural)
    if identity.regional_characteristics:
        print(f"\nHistorical/Cultural Context:")
        for char in identity.regional_characteristics[:5]:
            print(f"  - {char}")

    # Show hobbies
    if identity.hobbies:
        print(f"\nHobbies ({len(identity.hobbies)}):")
        for hobby in identity.hobbies[:6]:
            print(f"  - {hobby}")

    # Show family
    if hasattr(identity, 'family') and identity.family:
        marital = identity.family.get('marital_status', 'Unknown')
        print(f"\nMarital Status: {marital}")

        if identity.family.get('mother'):
            mother = identity.family['mother']
            mother_status = "Deceased" if mother.get('deceased') else "Alive"
            print(f"Mother: {mother_status}")

        if identity.family.get('father'):
            father = identity.family['father']
            father_status = "Deceased" if father.get('deceased') else "Alive"
            print(f"Father: {father_status}")

        siblings = identity.family.get('siblings', [])
        if siblings:
            print(f"Siblings: {len(siblings)}")

    # Show employment
    if hasattr(identity, 'employment') and identity.employment:
        current_job = identity.employment.get('current_job')
        start_date = identity.employment.get('start_date')
        if current_job and start_date:
            print(f"\nCurrent Job: {current_job} (since {start_date})")

        prev_positions = identity.employment.get('previous_positions', [])
        if prev_positions:
            print(f"Previous positions: {len(prev_positions)}")
            for i, pos in enumerate(prev_positions[:2], 1):
                job = pos.get('job', 'Unknown')
                dates = f"{pos.get('start_date', '?')} - {pos.get('end_date', '?')}"
                print(f"  {i}. {job} ({dates})")

print("\n" + "="*100)
print("TESTING COMPLETE")
print("="*100)
