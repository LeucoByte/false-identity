#!/usr/bin/env python3
"""Check what jobs are being generated for young people"""

import sys
sys.path.insert(0, '/home/leucocito/false-identity/src')

from generator import IdentityGenerator
from data_loader import DataLoader
from collections import Counter

# Initialize
data_loader = DataLoader()
generator = IdentityGenerator(data_loader)

print("=" * 80)
print("CHECKING JOBS FOR YOUNG PEOPLE (18-25) IN RUSSIA")
print("=" * 80)
print()

job_counts = Counter()
no_employment_attr = 0
employment_is_none = 0
employment_no_current_job = 0

for i in range(100):
    identity = generator.generate(country='russia', min_age=18, max_age=25)

    if not hasattr(identity, 'employment'):
        no_employment_attr += 1
    elif identity.employment is None:
        employment_is_none += 1
    elif isinstance(identity.employment, dict):
        current_job = identity.employment.get('current_job')
        if current_job:
            job_counts[current_job] += 1
        else:
            employment_no_current_job += 1
    else:
        print(f"Unknown employment type: {type(identity.employment)}")

print(f"Generated 100 young Russian profiles (ages 18-25)")
print()
print("Jobs found:")
print("-" * 80)
for job, count in job_counts.most_common():
    print(f"{count:3d} - {job}")

print()
print("=" * 80)
print(f"Total unique jobs: {len(job_counts)}")
print(f"Student jobs: {sum(count for job, count in job_counts.items() if 'Student' in job)}")
print()
print("DEBUG:")
print(f"  No employment attribute: {no_employment_attr}")
print(f"  Employment is None: {employment_is_none}")
print(f"  Employment exists but no current_job: {employment_no_current_job}")
print("=" * 80)
