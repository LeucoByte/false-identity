#!/usr/bin/env python3
"""Test specifically for student education levels"""

import sys
sys.path.insert(0, '/home/leucocito/false-identity/src')

from generator import IdentityGenerator
from data_loader import DataLoader

# Initialize
data_loader = DataLoader()
generator = IdentityGenerator(data_loader)

print("=" * 80)
print("TESTING STUDENT EDUCATION LEVELS")
print("=" * 80)
print()

students_found = 0
education_issues = []

# Generate young profiles (18-25) which are more likely to be students
for i in range(50):
    identity = generator.generate(country='russia', min_age=18, max_age=25)

    if hasattr(identity, 'employment') and identity.employment:
        current_job = identity.employment.get('current_job') if isinstance(identity.employment, dict) else None

        if current_job and 'Student' in current_job:
            students_found += 1

            education_level = None
            if hasattr(identity, 'education') and identity.education:
                education_level = identity.education.get('level') if isinstance(identity.education, dict) else None

            print(f"\nStudent #{students_found}: {identity.full_name} ({identity.age} years)")
            print(f"  Job: {current_job}")
            print(f"  Education: {education_level}")

            # Check for university programs
            university_keywords = ['Engineering', 'Medicine', 'Law', 'Computer Science',
                                  'Economics', 'Business', 'Architecture', 'Psychology',
                                  'Biology', 'Chemistry', 'Physics', 'Mathematics',
                                  'Pharmacy', 'Veterinary', 'Dentistry', 'Sociology',
                                  'Philosophy', 'History', 'Political Science']

            is_university_program = any(keyword in current_job for keyword in university_keywords)

            if is_university_program:
                # Should be Bachelor's degree (in progress), NOT Secondary
                if education_level and 'Secondary' in education_level:
                    print(f"  ❌ BUG: University student with Secondary education!")
                    education_issues.append({
                        'name': identity.full_name,
                        'age': identity.age,
                        'job': current_job,
                        'education': education_level
                    })
                elif education_level and 'Bachelor' in education_level:
                    print(f"  ✅ Correct: University student with Bachelor's degree")
                else:
                    print(f"  ⚠️  Unknown education type for university student")

print("\n" + "=" * 80)
print(f"Total students found: {students_found}")
print(f"Education issues found: {len(education_issues)}")
print("=" * 80)

if education_issues:
    print("\n❌ EDUCATION LEVEL BUGS:")
    for issue in education_issues:
        print(f"  - {issue['name']} ({issue['age']})")
        print(f"    Job: {issue['job']}")
        print(f"    Education: {issue['education']}")
else:
    print("\n✅ All student education levels are correct!")
