#!/usr/bin/env python3
"""Test for critical bugs: future marriage dates and education level mismatch"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generator import IdentityGenerator
from data_loader import DataLoader
from datetime import datetime

def test_marriage_dates_and_education():
    """Generate profiles and check for future dates and education mismatches"""

    data_loader = DataLoader()
    gen = IdentityGenerator(data_loader)
    current_year = 2025

    print("Generating 30 Russian profiles to test marriage dates and education levels...")
    print("=" * 80)

    future_dates_found = []
    education_mismatches = []

    for i in range(30):
        try:
            identity = gen.generate(country='russia')

            # Check for future marriage dates
            if hasattr(identity, 'marital_status') and identity.marital_status:
                marriages = identity.marital_status.get('marriages', []) if isinstance(identity.marital_status, dict) else []
                for marriage in marriages:
                    marriage_date = marriage.get('marriage_date', '')
                    if marriage_date:
                        # Parse date (format: DD.MM.YYYY for Russia)
                        try:
                            parts = marriage_date.replace('/', '.').split('.')
                            if len(parts) == 3:
                                year = int(parts[2])
                                if year > current_year:
                                    future_dates_found.append({
                                        'profile': i+1,
                                        'name': identity.full_name if hasattr(identity, 'full_name') else 'Unknown',
                                        'age': identity.age if hasattr(identity, 'age') else 'Unknown',
                                        'date': marriage_date,
                                        'year': year
                                    })
                        except:
                            pass

            # Check for education level mismatches
            current_job = None
            education = None

            if hasattr(identity, 'employment') and identity.employment:
                current_job = identity.employment.get('current_job') if isinstance(identity.employment, dict) else None

            if hasattr(identity, 'education') and identity.education:
                education = identity.education.get('level') if isinstance(identity.education, dict) else None

            if current_job and education:
                # Check if student of university program with wrong education level
                university_keywords = ['Engineering', 'Medicine', 'Law', 'Computer Science',
                                      'Economics', 'Business', 'Architecture', 'Psychology',
                                      'Biology', 'Chemistry', 'Physics', 'Mathematics',
                                      'Pharmacy', 'Veterinary', 'Dentistry']

                is_university_student = any(keyword in current_job for keyword in university_keywords) and 'Student' in current_job

                if is_university_student:
                    # Should have "Bachelor's degree (in progress)" or similar, NOT "Secondary education"
                    if 'Secondary' in education and 'in progress' in education:
                        education_mismatches.append({
                            'profile': i+1,
                            'name': identity.full_name if hasattr(identity, 'full_name') else 'Unknown',
                            'age': identity.age if hasattr(identity, 'age') else 'Unknown',
                            'job': current_job,
                            'education': education
                        })
        except Exception as e:
            print(f"Error generating profile {i+1}: {e}")

    # Report results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    print(f"\n1. FUTURE MARRIAGE DATES: {len(future_dates_found)} found")
    if future_dates_found:
        print("   ❌ CRITICAL BUG STILL PRESENT!")
        for bug in future_dates_found:
            print(f"   - Profile #{bug['profile']}: {bug['name']} (age {bug['age']})")
            print(f"     Marriage date: {bug['date']} (year {bug['year']} > {current_year})")
    else:
        print("   ✅ No future marriage dates found!")

    print(f"\n2. EDUCATION LEVEL MISMATCHES: {len(education_mismatches)} found")
    if education_mismatches:
        print("   ❌ BUG PRESENT!")
        for bug in education_mismatches:
            print(f"   - Profile #{bug['profile']}: {bug['name']} (age {bug['age']})")
            print(f"     Job: {bug['job']}")
            print(f"     Education: {bug['education']}")
            print(f"     Expected: Bachelor's degree (in progress) or similar")
    else:
        print("   ✅ No education mismatches found!")

    print("\n" + "=" * 80)
    print(f"Total profiles tested: 30")
    print(f"Bugs found: {len(future_dates_found) + len(education_mismatches)}")
    print("=" * 80)

    return len(future_dates_found) == 0 and len(education_mismatches) == 0

if __name__ == '__main__':
    success = test_marriage_dates_and_education()
    sys.exit(0 if success else 1)
