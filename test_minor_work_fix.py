#!/usr/bin/env python3
"""
Test to verify NO MINORS have work histories after fix.
Focus on young adults (18-25) where the bug was most likely.
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

def parse_date(date_str):
    """Parse date string to year"""
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            return int(parts[2])
    except:
        pass
    return None

print("="*100)
print("TEST: VERIFY NO MINORS HAVE WORK HISTORIES")
print("="*100)
print()

issues = []
total_tested = 0

# Test 50 young adults (18-25) where bug was most likely
for i in range(1, 51):
    age = random.randint(18, 25)
    gender = random.choice(['male', 'female'])

    identity = generator.generate(country='spain', gender=gender, min_age=age, max_age=age)
    total_tested += 1

    birth_year = current_year - age

    # Check current job start date
    if hasattr(identity, 'employment') and identity.employment:
        current_job = identity.employment.get('current_job')
        current_start = identity.employment.get('start_date', '')

        if current_start and current_job and current_job not in ["Student", "Unemployed", None]:
            start_year = parse_date(current_start)
            if start_year:
                age_when_started = start_year - birth_year

                if age_when_started < 16:
                    issues.append({
                        'name': identity.full_name,
                        'age': age,
                        'job': current_job,
                        'start_date': current_start,
                        'age_when_started': age_when_started,
                        'type': 'CURRENT JOB'
                    })

        # Check previous job start dates
        prev_positions = identity.employment.get('previous_positions', [])
        if prev_positions:
            for prev in prev_positions:
                prev_job = prev.get('job', '')
                prev_start = prev.get('start_date', '')

                if prev_start:
                    start_year = parse_date(prev_start)
                    if start_year:
                        age_when_started = start_year - birth_year

                        # Internships can be 18+, other jobs should be 16+
                        min_age = 18 if 'Intern' in prev_job else 16

                        if age_when_started < min_age:
                            issues.append({
                                'name': identity.full_name,
                                'age': age,
                                'job': prev_job,
                                'start_date': prev_start,
                                'age_when_started': age_when_started,
                                'type': 'PREVIOUS JOB',
                                'min_required': min_age
                            })

print(f"Tested {total_tested} profiles (ages 18-25)")
print()

if issues:
    print(f"🔴 FAILED: Found {len(issues)} instances of minors working!")
    print()
    for issue in issues:
        print(f"❌ {issue['name']} ({issue['age']} años)")
        print(f"   {issue['type']}: {issue['job']}")
        print(f"   Started: {issue['start_date']}")
        print(f"   Age when started: {issue['age_when_started']} years old")
        if 'min_required' in issue:
            print(f"   Minimum required: {issue['min_required']} years")
        print()
else:
    print("✅ PERFECTO! All employment histories respect minimum working age!")
    print()
    print("🎉 NO MINORS WORKING - Bug fixed successfully!")
    print()

# Also show a few sample profiles for manual verification
print("\n" + "="*100)
print("SAMPLE PROFILES FOR MANUAL VERIFICATION (first 5)")
print("="*100)

for i in range(1, 6):
    age = random.randint(19, 22)
    gender = random.choice(['male', 'female'])
    identity = generator.generate(country='spain', gender=gender, min_age=age, max_age=age)

    birth_year = current_year - age

    print(f"\nProfile #{i}: {identity.full_name} ({age} años, born {birth_year})")

    if hasattr(identity, 'employment') and identity.employment:
        current_job = identity.employment.get('current_job')
        current_start = identity.employment.get('start_date', '')

        print(f"  Current Job: {current_job}")
        if current_start:
            start_year = parse_date(current_start)
            if start_year:
                age_when_started = start_year - birth_year
                print(f"  Started: {current_start} (age {age_when_started})")

        prev_positions = identity.employment.get('previous_positions', [])
        if prev_positions:
            for prev in prev_positions:
                prev_job = prev.get('job', '')
                prev_start = prev.get('start_date', '')
                prev_end = prev.get('end_date', '')

                print(f"  Previous: {prev_job}")
                if prev_start:
                    start_year = parse_date(prev_start)
                    if start_year:
                        age_when_started = start_year - birth_year
                        print(f"    {prev_start} - {prev_end} (started at age {age_when_started})")

print()
