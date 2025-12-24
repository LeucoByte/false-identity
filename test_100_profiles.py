#!/usr/bin/env python3
"""
Exhaustive test of 100 profiles stratified by age group.
Analyzes EACH profile for coherence issues.
"""

import sys
sys.path.insert(0, '/home/leucocito/false-identity/src')

from generator import IdentityGenerator
from data_loader import DataLoader
import random
import json
from datetime import datetime

# Initialize
data_loader = DataLoader()
generator = IdentityGenerator(data_loader)
current_year = 2025

# Age groups
AGE_GROUPS = {
    "VERY YOUNG (18-25)": (18, 25),
    "YOUNG ADULT (26-35)": (26, 35),
    "MIDDLE AGE (36-50)": (36, 50),
    "MATURE (51-65)": (51, 65),
    "ELDERLY (66-85)": (66, 85)
}

def parse_date(date_str):
    """Parse DD/MM/YYYY date string to year"""
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            return int(parts[2])
    except:
        pass
    return None

def check_profile(identity, profile_num, age_group_name):
    """Check a single profile for ALL coherence issues"""
    issues = []
    warnings = []

    age = identity.age
    job = identity.job or "Unknown"
    education = identity.education or ""
    family = identity.family or {}
    regional_chars = identity.regional_characteristics or []

    # Load job requirements for validation
    job_requirements = data_loader.load_job_education_requirements()

    # ========================================================================
    # CHECK 1: PROFESSION vs EDUCATION vs AGE
    # ========================================================================
    if job in job_requirements:
        min_level, field, min_age = job_requirements[job]

        # Check age requirement
        if age < min_age:
            issues.append(f"  ❌ JOB-AGE: {job} requires min age {min_age}, but person is {age}")

        # Check education requirement
        education_levels_order = ["none", "primary", "secondary", "vocational", "bachelor", "master", "doctorate"]

        # Determine actual education level from string
        actual_level = "none"
        edu_lower = education.lower()
        if "doctorate" in edu_lower or "phd" in edu_lower:
            actual_level = "doctorate"
        elif "master" in edu_lower:
            actual_level = "master"
        elif "bachelor" in edu_lower:
            actual_level = "bachelor"
        elif "vocational" in edu_lower:
            actual_level = "vocational"
        elif "secondary" in edu_lower or "high school" in edu_lower:
            actual_level = "secondary"
        elif "primary" in edu_lower:
            actual_level = "primary"

        # Compare levels
        try:
            required_idx = education_levels_order.index(min_level)
            actual_idx = education_levels_order.index(actual_level)
            if actual_idx < required_idx:
                issues.append(f"  ❌ JOB-EDU: {job} requires {min_level}, but person has {actual_level} ({education})")
        except ValueError:
            pass

    # ========================================================================
    # CHECK 2: CHILDREN vs BIOLOGICAL LIMITS (mother age 18-45 at birth)
    # ========================================================================
    children = family.get('children', [])
    gender = identity.gender

    for child in children:
        child_name = child.get('name', 'Unknown')
        child_birth_str = child.get('birth_date', '')
        birth_year = parse_date(child_birth_str)

        if birth_year:
            # Calculate person's age when child was born
            person_age_at_birth = age - (current_year - birth_year)

            # For females (mothers) - strict biological limit
            if gender == 'female':
                if person_age_at_birth < 18:
                    issues.append(f"  ❌ CHILD-AGE: Mother was {person_age_at_birth} when {child_name} was born (min 18)")
                elif person_age_at_birth > 45:
                    issues.append(f"  ❌ CHILD-AGE: Mother was {person_age_at_birth} when {child_name} was born (max 45)")

            # For males (fathers) - wider range but still check extremes
            else:
                if person_age_at_birth < 16:
                    issues.append(f"  ❌ CHILD-AGE: Father was {person_age_at_birth} when {child_name} was born (min 16)")
                elif person_age_at_birth > 65:
                    warnings.append(f"  ⚠️  CHILD-AGE: Father was {person_age_at_birth} when {child_name} was born (unusual)")

    # ========================================================================
    # CHECK 3: DIVORCES - all should have Ended/Lasted
    # ========================================================================
    ex_partners = family.get('ex_partners', [])
    for ex in ex_partners:
        ex_name = ex.get('name', 'Unknown')
        if not ex.get('end_date'):
            issues.append(f"  ❌ DIVORCE: Ex-partner {ex_name} missing 'end_date'")
        if 'duration' not in ex:
            issues.append(f"  ❌ DIVORCE: Ex-partner {ex_name} missing 'duration'")

    # ========================================================================
    # CHECK 4: STUDIES "in progress" only for <35
    # ========================================================================
    if "in progress" in education.lower():
        if age >= 35:
            issues.append(f"  ❌ EDUCATION: '{education}' at age {age} (in progress only realistic <35)")

    # ========================================================================
    # CHECK 5: HISTORICAL TAGS coherent with age
    # ========================================================================
    for char in regional_chars:
        char_lower = char.lower()

        # Check 15-M movement (2011) - should be 28+ in 2025
        if "15-m" in char_lower or "indignados" in char_lower:
            if age < 28:
                issues.append(f"  ❌ TAG: '{char}' at age {age} (15-M in 2011, needs 28+ in 2025)")

        # Check 2008 crisis - should be 30+ in 2025 (at least 13 in 2008)
        if "2008" in char_lower and "crisis" in char_lower:
            if age < 30:
                issues.append(f"  ❌ TAG: '{char}' at age {age} (2008 crisis, needs 30+ in 2025)")

        # Check Madrid bombings (2004) - should be 33+ in 2025 (at least 12 in 2004)
        if "2004" in char_lower and "madrid" in char_lower:
            if age < 33:
                issues.append(f"  ❌ TAG: '{char}' at age {age} (2004 bombings, needs 33+ in 2025)")

    # ========================================================================
    # CHECK 6: RELATIONSHIPS - both parties ≥16 at start
    # ========================================================================
    current_partner = family.get('partner')
    marital_status = family.get('marital_status', 'Single')

    if current_partner and marital_status in ("Girlfriend", "Boyfriend", "Married"):
        start_date = current_partner.get('start_date', '')
        partner_age = current_partner.get('current_age', 0)
        start_year = parse_date(start_date)

        if start_year:
            # Calculate ages at relationship start
            person_age_at_start = age - (current_year - start_year)
            partner_age_at_start = partner_age - (current_year - start_year)

            MIN_AGE = 16 if marital_status in ("Girlfriend", "Boyfriend") else 18

            if person_age_at_start < MIN_AGE:
                issues.append(f"  ❌ RELATIONSHIP: Person was {person_age_at_start} when relationship started (min {MIN_AGE})")
            if partner_age_at_start < MIN_AGE:
                issues.append(f"  ❌ RELATIONSHIP: Partner was {partner_age_at_start} when relationship started (min {MIN_AGE})")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    status = "✅ VERDE" if len(issues) == 0 and len(warnings) == 0 else "🟨 AMARILLO" if len(issues) == 0 else "🔴 ROJO"

    return {
        'profile_num': profile_num,
        'age_group': age_group_name,
        'name': identity.full_name,
        'age': age,
        'job': job,
        'education': education,
        'issues': issues,
        'warnings': warnings,
        'status': status
    }

# ============================================================================
# MAIN TEST
# ============================================================================

print("="*120)
print("EXHAUSTIVE TEST: 100 PROFILES STRATIFIED BY AGE GROUP")
print("="*120)
print()

all_results = []
total_issues = 0
total_warnings = 0

for age_group_name, (min_age, max_age) in AGE_GROUPS.items():
    print(f"\n{'='*120}")
    print(f"TESTING {age_group_name} (20 profiles)")
    print('='*120)

    group_results = []

    for i in range(1, 21):
        # Generate random age in range
        age = random.randint(min_age, max_age)
        gender = random.choice(['male', 'female'])

        # Generate identity
        identity = generator.generate(country='spain', gender=gender, min_age=age, max_age=age)

        # Check profile
        result = check_profile(identity, i, age_group_name)
        group_results.append(result)
        all_results.append(result)

        # Count issues
        num_issues = len(result['issues'])
        num_warnings = len(result['warnings'])
        total_issues += num_issues
        total_warnings += num_warnings

        # Print result
        status_symbol = result['status'].split()[0]
        print(f"\nPROFIL #{i} [{age_group_name}]: {result['name']} ({result['age']} años)")
        print(f"  Job: {result['job']}")
        print(f"  Education: {result['education']}")

        if num_issues > 0:
            print(f"  [🔴] Profesión-EDU-EDAD: {num_issues} issue(s)")
            for issue in result['issues']:
                print(issue)
        else:
            print(f"  [✓] Profesión-EDU-EDAD: OK")

        if num_warnings > 0:
            for warning in result['warnings']:
                print(warning)

        print(f"  [✓] Coherencia general: {result['status']}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "="*120)
print("RESUMEN FINAL")
print("="*120)

verde_count = sum(1 for r in all_results if "VERDE" in r['status'])
amarillo_count = sum(1 for r in all_results if "AMARILLO" in r['status'])
rojo_count = sum(1 for r in all_results if "ROJO" in r['status'])

print(f"\nTotal profiles tested: 100")
print(f"  🟢 VERDE (perfect): {verde_count}/100")
print(f"  🟨 AMARILLO (warnings only): {amarillo_count}/100")
print(f"  🔴 ROJO (has issues): {rojo_count}/100")
print(f"\nTotal issues found: {total_issues}")
print(f"Total warnings found: {total_warnings}")
print()

if total_issues == 0:
    print("🎉🎉🎉 PERFECTO! {verde_count}/100 PERFILES 100% COHERENTES! 🎉🎉🎉")
    print("\n✅ CONFIRMACIÓN: Sistema listo para producción")
else:
    print(f"⚠️  REFACTORIZACIÓN NECESARIA: {total_issues} issues encontrados")
    print("\nProfiles with issues:")
    for r in all_results:
        if "ROJO" in r['status']:
            print(f"  - {r['name']} ({r['age_group']}): {len(r['issues'])} issues")

print()
