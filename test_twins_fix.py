#!/usr/bin/env python3
"""
Test to verify twins/duplicate children bug is fixed
"""

import sys
sys.path.insert(0, 'src')
from generator import IdentityGenerator
from data_loader import DataLoader

loader = DataLoader()
gen = IdentityGenerator(loader)

print("="*100)
print("TEST: VERIFY NO DUPLICATE CHILDREN (SAME YEAR, DIFFERENT DATES)")
print("="*100)
print()

issues = []
total_tested = 0
total_with_children = 0

# Test 100 profiles with high probability of having children
for i in range(1, 101):
    # Test ages 35-50 (more likely to have multiple children)
    age = 40
    gender = 'female'  # Mothers more likely to show children

    identity = gen.generate('spain', gender=gender, min_age=age, max_age=age)
    total_tested += 1

    if hasattr(identity, 'family') and identity.family:
        children = identity.family.get('children', [])

        if len(children) >= 2:
            total_with_children += 1

            # Check for duplicate birth years with different dates
            birth_years = {}  # year -> list of (name, birth_date)

            for child in children:
                if not child.get('deceased') and child.get('birth_date'):
                    birth_date = child['birth_date']
                    name = child.get('name', 'Unknown')

                    # Extract year from DD/MM/YYYY format
                    try:
                        parts = birth_date.split('/')
                        if len(parts) == 3:
                            year = int(parts[2])

                            if year not in birth_years:
                                birth_years[year] = []

                            birth_years[year].append((name, birth_date))
                    except:
                        pass

            # Check for same year with different dates
            for year, children_in_year in birth_years.items():
                if len(children_in_year) > 1:
                    # Multiple children born same year
                    dates = [date for _, date in children_in_year]
                    unique_dates = set(dates)

                    if len(unique_dates) > 1:
                        # TWINS/TRIPLETS WITH DIFFERENT DATES! This is the bug!
                        issues.append({
                            'name': identity.full_name,
                            'age': age,
                            'year': year,
                            'children': children_in_year
                        })

print(f"Tested {total_tested} profiles")
print(f"Profiles with 2+ children: {total_with_children}")
print()

if issues:
    print(f"🔴 BUG FOUND: {len(issues)} cases of twins with different birth dates!")
    print()
    for issue in issues[:5]:
        print(f"❌ {issue['name']} ({issue['age']} years)")
        print(f"   Children born in {issue['year']}:")
        for child_name, birth_date in issue['children']:
            print(f"     - {child_name}: {birth_date}")
        print()
else:
    print("✅ PERFECTO! No duplicate children with different dates!")
    print()
    print("🎉 BUG FIXED - All twins/triplets have same birth date!")
    print()

# Show a sample profile with twins if any exist
print("\n" + "="*100)
print("SAMPLE: Profile with twins (if any)")
print("="*100)

for _ in range(20):
    identity = gen.generate('spain', gender='female', min_age=40, max_age=45)

    if hasattr(identity, 'family') and identity.family:
        children = identity.family.get('children', [])

        # Look for twins (same birth date)
        if len(children) >= 2:
            birth_dates = {}
            for child in children:
                if not child.get('deceased') and child.get('birth_date'):
                    bd = child['birth_date']
                    if bd not in birth_dates:
                        birth_dates[bd] = []
                    birth_dates[bd].append(child.get('name', 'Unknown'))

            for bd, names in birth_dates.items():
                if len(names) >= 2:
                    print(f"\n{identity.full_name} has TWINS:")
                    for name in names:
                        print(f"  - {name} (born {bd})")
                    break
            else:
                continue
            break

print()
