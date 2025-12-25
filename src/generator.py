#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Identity generation logic for the Synthetic Identity Generator.
Contains DataLoader and IdentityGenerator classes.
"""

import random
import secrets
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from models import Identity, CountryRules, translate
from config import DATA_DIR
from data_loader import DataLoader


class IdentityGenerator:
    """
    Generates synthetic identities based on country-specific rules.

    Uses cryptographically secure randomness for realistic identity generation.
    """

    def __init__(self, data_loader: DataLoader):
        """
        Initialize IdentityGenerator.

        Args:
            data_loader: DataLoader instance for accessing data files
        """
        self.loader = data_loader
        # Seed random with cryptographically secure randomness
        random.seed(secrets.randbits(256))

    def _generate_death_info_for_parent(self, person_age: int, current_year: int, date_format: str,
                                         rules: CountryRules, min_death_age: int, identity_age: int,
                                         birth_year: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate death information for a parent, ensuring they died at a realistic age and time.

        Args:
            person_age: Age the parent would have if alive
            current_year: Current year
            date_format: Date format string from rules
            rules: CountryRules object
            min_death_age: Minimum age at which parent must have died
            identity_age: Age of the main identity (used to determine realistic death timing)
            birth_year: Optional pre-calculated birth year (if None, will be calculated from person_age)

        Returns:
            Dict with birth_date, death_date, age_at_death, cause_of_death
        """
        # Use provided birth year or calculate from person_age
        if birth_year is None:
            birth_year = current_year - person_age
        life_expectancy = rules.get_life_expectancy()

        # REALISTIC DEATH AGE AND TIMING CALCULATION
        # Parents rarely live beyond life expectancy, and if identity is old, parents died long ago

        # Calculate how many years ago the parent should have died based on identity's age
        if identity_age >= 70:
            # Old identity: parent died long ago (10-30 years ago)
            years_since_death = random.randint(10, 30)
        elif identity_age >= 50:
            # Middle-aged identity: parent died 5-20 years ago
            years_since_death = random.randint(5, 20)
        elif identity_age >= 35:
            # Adult identity: parent could have died recently or years ago
            years_since_death = random.randint(0, 15)
        else:
            # Young identity: if parent died, it was more random (accident, illness)
            max_years = max(0, min(identity_age - 5, 20))
            years_since_death = random.randint(0, max_years) if max_years > 0 else 0

        # Calculate death year (must be in the past, not future)
        death_year = current_year - years_since_death

        # Parent's age at death = death_year - birth_year
        age_at_death = death_year - birth_year

        # Ensure age at death is realistic and meets minimum requirements
        # Parent must have been at least min_death_age when they died
        if age_at_death < min_death_age:
            # If calculated death is too early, adjust to minimum
            age_at_death = min_death_age
            death_year = birth_year + age_at_death
            # But ensure this doesn't make death too recent for old identities
            if identity_age >= 60:
                # Force death to be at least 5 years ago
                max_death_year = current_year - 5
                if death_year > max_death_year:
                    death_year = current_year - random.randint(5, 20)
                    age_at_death = death_year - birth_year

        # Cap age at death to realistic maximum (life expectancy + small margin)
        max_realistic_death_age = life_expectancy + random.randint(-5, 10)
        if age_at_death > max_realistic_death_age:
            age_at_death = max_realistic_death_age
            death_year = birth_year + age_at_death

        # Final safety: ensure death_year is not in the future and not too recent for old identities
        if death_year > current_year:
            death_year = current_year - random.randint(0, 5)
            age_at_death = death_year - birth_year

        # For old identities (60+), ensure death wasn't THIS year (feels unrealistic)
        if identity_age >= 60 and death_year >= current_year - 1:
            death_year = current_year - random.randint(2, 10)
            age_at_death = death_year - birth_year

        # Generate dates
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Safe for all months
        death_month = random.randint(1, 12)
        death_day = random.randint(1, 28)

        # Format dates according to country rules
        if date_format == "DD/MM/YYYY":
            birth_date = f"{birth_day:02d}/{birth_month:02d}/{birth_year}"
            death_date = f"{death_day:02d}/{death_month:02d}/{death_year}"
        elif date_format == "MM/DD/YYYY":
            birth_date = f"{birth_month:02d}/{birth_day:02d}/{birth_year}"
            death_date = f"{death_month:02d}/{death_day:02d}/{death_year}"
        else:  # YYYY/MM/DD or other
            birth_date = f"{birth_year}/{birth_month:02d}/{birth_day:02d}"
            death_date = f"{death_year}/{death_month:02d}/{death_day:02d}"

        # Get appropriate death cause based on age at death
        causes = self.loader.load_death_causes(age_at_death)
        cause_of_death = random.choice(causes) if causes else "Natural causes"

        return {
            "birth_date": birth_date,
            "death_date": death_date,
            "age_at_death": age_at_death,
            "cause_of_death": cause_of_death
        }

    def _generate_death_info(self, person_age: int, current_year: int, date_format: str, rules: CountryRules) -> Optional[Dict[str, Any]]:
        """
        Generate death information for a family member including dates and cause.

        Args:
            person_age: Current age of the person (if alive) or age at death
            current_year: Current year
            date_format: Date format string from rules
            rules: CountryRules object

        Returns:
            Dict with birth_date, death_date, age_at_death, cause_of_death, or None if alive
        """
        # Generate birth year
        birth_year = current_year - person_age

        # Determine if person should be deceased (already determined by caller)
        # This function generates the death details

        # Death occurred between birth and now
        # Random age at death between reasonable range
        age_at_death = random.randint(max(1, person_age - 30), person_age)
        death_year = birth_year + age_at_death

        # Generate dates
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Safe for all months
        death_month = random.randint(1, 12)
        death_day = random.randint(1, 28)

        # Format dates according to country rules
        if date_format == "DD/MM/YYYY":
            birth_date = f"{birth_day:02d}/{birth_month:02d}/{birth_year}"
            death_date = f"{death_day:02d}/{death_month:02d}/{death_year}"
        elif date_format == "MM/DD/YYYY":
            birth_date = f"{birth_month:02d}/{birth_day:02d}/{birth_year}"
            death_date = f"{death_month:02d}/{death_day:02d}/{death_year}"
        else:  # YYYY/MM/DD or other
            birth_date = f"{birth_year}/{birth_month:02d}/{birth_day:02d}"
            death_date = f"{death_year}/{death_month:02d}/{death_day:02d}"

        # Get appropriate death cause based on age at death
        causes = self.loader.load_death_causes(age_at_death)
        cause_of_death = random.choice(causes) if causes else "Natural causes"

        return {
            "birth_date": birth_date,
            "death_date": death_date,
            "age_at_death": age_at_death,
            "cause_of_death": cause_of_death
        }

    def _generate_birth_date(self, person_age: int, current_year: int, date_format: str) -> Tuple[str, int]:
        """
        Generate birth date for a living person.

        Args:
            person_age: Current age of the person
            current_year: Current year
            date_format: Date format string from rules

        Returns:
            Tuple of (birth_date, current_age)
        """
        birth_year = current_year - person_age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)

        # Format date according to country rules
        if date_format == "DD/MM/YYYY":
            birth_date = f"{birth_day:02d}/{birth_month:02d}/{birth_year}"
        elif date_format == "MM/DD/YYYY":
            birth_date = f"{birth_month:02d}/{birth_day:02d}/{birth_year}"
        else:
            birth_date = f"{birth_year}/{birth_month:02d}/{birth_day:02d}"

        return birth_date, person_age

    def _get_age_bucket_from_age(self, age: int, rules: CountryRules) -> str:
        """
        Get the age bucket for a given age.

        Args:
            age: Age in years
            rules: CountryRules object

        Returns:
            Age bucket name (very_young, young_adults, adults, middle_aged, older_adults, seniors, elderly)
        """
        min_age = rules.get_min_age()
        life_expectancy = rules.get_life_expectancy()

        if age < min_age + 5:
            return "very_young"
        elif age < min_age + 16:
            return "young_adults"
        elif age < 40:
            return "adults"
        elif age < 50:
            return "middle_aged"
        elif age < 65:
            return "older_adults"
        elif age < life_expectancy - 10:
            return "seniors"
        else:
            return "elderly"

    def _generate_fake_email(self, first_name: str, surnames: List[str], dob: str, country: str = "unknown") -> str:
        """
        Generate a realistic fake email based on identity information.

        Uses common email patterns without dots (more realistic).
        Transliterates non-Latin names to Latin alphabet for email compatibility.

        Args:
            first_name: Person's first name
            surnames: List of surnames
            dob: Date of birth string
            country: Country code for proper transliteration

        Returns:
            Fake email address
        """
        # Available domains from fakemailgenerator.com
        domains = [
            'armyspy.com', 'cuvox.de', 'dayrep.com', 'einrot.com',
            'fleckens.hu', 'gustr.com', 'jourrapide.com', 'rhyta.com',
            'superrito.com', 'teleworm.us'
        ]

        def clean_text(text):
            """Remove accents, convert to ASCII lowercase, and keep only alphanumeric characters."""
            # Normalize unicode characters
            text = unicodedata.normalize('NFD', text)
            text = text.encode('ascii', 'ignore').decode('utf-8')
            text = text.lower().strip()
            # Remove all non-alphanumeric characters
            text = ''.join(c for c in text if c.isalnum())
            return text

        # Transliterate names to Latin alphabet first (for non-Latin scripts)
        transliterated_first = translate(first_name, country)
        transliterated_surnames = [translate(s, country) for s in surnames]

        # Clean transliterated names
        clean_first = clean_text(transliterated_first)
        clean_surnames = [clean_text(s) for s in transliterated_surnames]

        # Extract year from date of birth
        year = ''
        if '/' in dob:
            parts = dob.split('/')
            for part in parts:
                if len(part) == 4:
                    year = part[-2:]
                    break

        # Get initials and short forms
        first_initial = clean_first[0] if clean_first else 'x'
        first_short = clean_first[:3] if len(clean_first) >= 3 else clean_first
        surname1_short = clean_surnames[0][:4] if len(clean_surnames[0]) >= 4 else clean_surnames[0]
        surname2_short = clean_surnames[1][:3] if len(clean_surnames) > 1 and len(clean_surnames[1]) >= 3 else ""

        # Generate realistic email patterns (NO dots)
        patterns = [
            f"{clean_first}{clean_surnames[0]}",
            f"{first_initial}{clean_surnames[0]}",
            f"{first_short}{clean_surnames[0]}",
            f"{first_initial}{surname1_short}",
            f"{first_short}{surname1_short}",
            f"{clean_first}{year}",
            f"{first_short}{surname1_short}{year}",
            f"{first_initial}{surname1_short}{year}",
            f"{clean_surnames[0]}{clean_first}",
            f"{surname1_short}{first_short}",
        ]

        # Add variations with both surnames if available
        if len(clean_surnames) > 1 and surname2_short:
            patterns.extend([
                f"{first_initial}{surname1_short}{surname2_short}",
                f"{first_short}{surname1_short}{surname2_short}",
                f"{first_initial}{surname1_short}{surname2_short}{year}",
            ])

        # Select random pattern and domain
        local_part = random.choice(patterns)
        domain = random.choice(domains)

        return f"{local_part}@{domain}"

    def _weighted_choice(self, options: Dict[str, float]) -> str:
        """
        Select an option based on weighted probabilities.

        Args:
            options: Dict of {option: probability_weight}

        Returns:
            Selected option string
        """
        # Filter out zero probabilities
        valid_options = {k: v for k, v in options.items() if v > 0}
        if not valid_options:
            return list(options.keys())[0] if options else "Unknown"

        items = list(valid_options.keys())
        weights = list(valid_options.values())

        return random.choices(items, weights=weights, k=1)[0]

    def _generate_dob(self, date_format: str, min_age: int = 18, max_age: int = 80) -> Tuple[str, int]:
        """
        Generate a random date of birth.

        Args:
            date_format: Format string from rules (e.g., "DD/MM/YYYY")
            min_age: Minimum age
            max_age: Maximum age

        Returns:
            Tuple of (formatted_date_string, age)
        """
        today = date.today()

        # Calculate date range
        min_date = today - timedelta(days=max_age * 365)
        max_date = today - timedelta(days=min_age * 365)

        # Random date in range
        days_diff = (max_date - min_date).days
        random_days = random.randint(0, days_diff)
        dob = min_date + timedelta(days=random_days)

        # Calculate age
        age = today.year - dob.year
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            age -= 1

        # Format according to rules
        formatted = self._format_date(dob, date_format)

        return formatted, age

    def _format_date(self, date_obj: date, format_str: str) -> str:
        """
        Format a date according to the format string.

        Args:
            date_obj: Date object
            format_str: Format like "DD/MM/YYYY" or "MM/DD/YYYY"

        Returns:
            Formatted date string
        """
        format_str = format_str.replace('DD', '%d')
        format_str = format_str.replace('MM', '%m')
        format_str = format_str.replace('YYYY', '%Y')
        format_str = format_str.replace('YY', '%y')

        return date_obj.strftime(format_str)

    def _parse_city_line(self, line: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Parse a city line.

        Format can be:
        - "Madrid|28001" (city|postal_code)
        - "Alcalá de Henares, Madrid|28801" (city with postal code, nearby province/capital)

        IMPORTANT: Postal code ALWAYS corresponds to the FIRST part (before comma).
        The SECOND part (after comma) is the nearby capital or province.

        Returns:
            Tuple of (city, nearby_town_or_none, postal_code_or_none)
        """
        postal_code = None

        # Extract postal code if present
        if '|' in line:
            line, postal_code = line.split('|')
            line = line.strip()
            postal_code = postal_code.strip()

        # Parse city and nearby town
        # Format: "City, Nearby|CP" where CP belongs to City
        if ',' in line:
            parts = [p.strip() for p in line.split(',')]
            return parts[0], parts[1], postal_code  # (city_with_CP, nearby_capital, postal_code)
        else:
            return line, None, postal_code

    def _generate_phone(self, rules: CountryRules) -> str:
        """
        Generate a phone number according to country rules.

        Args:
            rules: CountryRules object

        Returns:
            Formatted phone number with country code
        """
        country_code = rules.get_phone_country_code()
        length = rules.get_phone_length()
        prefixes = rules.get_phone_prefixes()
        phone_format = rules.get_phone_format()

        # Select prefix
        prefix = random.choice(prefixes)

        # Generate remaining digits
        remaining_length = length - len(prefix)
        rest = ''.join([str(random.randint(0, 9)) for _ in range(remaining_length)])

        # Combine
        full_number = prefix + rest

        # Apply format
        formatted = self._apply_phone_format(full_number, phone_format)

        return f"{country_code} {formatted}"

    def _apply_phone_format(self, number: str, format_str: str) -> str:
        """
        Apply phone format pattern.

        Args:
            number: Raw number string (e.g., "612345678")
            format_str: Format pattern (e.g., "### ## ## ##")

        Returns:
            Formatted number (e.g., "612 34 56 78")
        """
        result = []
        num_idx = 0

        for char in format_str:
            if char == '#':
                if num_idx < len(number):
                    result.append(number[num_idx])
                    num_idx += 1
            else:
                result.append(char)

        return ''.join(result)

    def _build_full_name(self, components: Dict[str, Any], name_order: List[str], country: str = None, gender: str = None) -> str:
        """
        Build full name according to name_order rules.

        Args:
            components: Dict with 'first', 'surname1', 'surname2', etc.
            name_order: List like ['first', 'surname1', 'surname2']
            country: Optional country code for special handling
            gender: Optional gender for special handling

        Returns:
            Full name string
        """
        parts = []
        for component in name_order:
            if component in components:
                parts.append(components[component])
            elif component == 'surname' and 'surname1' in components:
                # Handle 'surname' -> 'surname1' mapping for single-surname countries
                parts.append(components['surname1'])

        # Vietnam: Add gender marker between surname and first name
        if country and country.lower() == 'vietnam' and gender:
            # Vietnamese name structure: Surname + Gender_Marker + Given_Name
            # For females: Add "Thị" (traditional female marker)
            # For males: Add "Văn" (common male marker), but also allow no marker or other markers

            if len(parts) >= 2:
                # parts[0] is surname, parts[1] is given name
                surname = parts[0]
                given_name = parts[1]

                if gender.lower() == 'female':
                    # Always add Thị for females (traditional)
                    parts = [surname, 'Thị', given_name]
                else:
                    # For males: 70% chance of adding Văn, 30% no marker
                    if random.random() < 0.7:
                        parts = [surname, 'Văn', given_name]
                    # else: keep as is (no middle name)

        return ' '.join(parts)

    def _filter_jobs_by_age(self, jobs: List[str], age: int, age_requirements: Dict[str, int]) -> List[str]:
        """
        Filter jobs list to only include jobs the person is old enough for.

        Args:
            jobs: List of all available jobs
            age: Person's current age
            age_requirements: Dictionary of job -> minimum age

        Returns:
            Filtered list of age-appropriate jobs
        """
        if not age_requirements:
            return jobs

        age_appropriate_jobs = []
        for job in jobs:
            min_age = age_requirements.get(job, 18)  # Default minimum age is 18
            if age >= min_age:
                age_appropriate_jobs.append(job)

        # If filtering removed all jobs, return low-skill jobs only
        if not age_appropriate_jobs:
            # Return only jobs with no age requirement
            age_appropriate_jobs = [job for job in jobs if job not in age_requirements]
            if not age_appropriate_jobs:
                # Ultimate fallback
                age_appropriate_jobs = jobs

        return age_appropriate_jobs

    def _get_job_for_age(self, age: int, jobs: List[str], rules: Any, gender: str, age_bucket: str,
                         country: str, marital_status: str = "Single", has_children: bool = False) -> Tuple[str, Optional[str]]:
        """
        Get appropriate job based on age, considering unemployment, students, housewives, and retirement.

        Args:
            age: Person's age
            jobs: List of available jobs
            rules: CountryRules object
            gender: Person's gender
            age_bucket: Age bucket (very_young, young_adults, etc.)
            country: Country code
            marital_status: Marital status
            has_children: Whether person has children

        Returns:
            Tuple of (current_job, previous_job)
            - current_job: Current occupation or status
            - previous_job: Previous job if unemployed/retired, None otherwise
        """
        unemployment_rate = rules.get_unemployment_rate()
        jobless_rate = rules.get_jobless_rate()

        # Load age requirements from BOTH sources and filter jobs
        age_requirements = self.loader.load_job_age_requirements()

        # CRITICAL: Also load complete job requirements (includes education + age minimums)
        complete_job_requirements = self.loader.load_job_education_requirements()

        # Merge age requirements: use the more restrictive (higher) minimum age
        for job, (min_level, field, min_age_from_complete) in complete_job_requirements.items():
            if job in age_requirements:
                # Use the higher of the two age requirements
                age_requirements[job] = max(age_requirements[job], min_age_from_complete)
            else:
                # Add from complete requirements
                age_requirements[job] = min_age_from_complete

        age_appropriate_jobs = self._filter_jobs_by_age(jobs, age, age_requirements)

        # Retired (65+)
        if age >= 65:
            previous_job = random.choice(age_appropriate_jobs)
            return "Retired", previous_job

        # Very young: high probability of being students
        if age_bucket == "very_young":
            # If under 18, MUST be student (legal working age is 18 in most countries)
            if age < 18:
                student_fields = self.loader.load_student_fields(country)
                if student_fields:
                    field = random.choice(student_fields)
                    return f"Student of {field}", None
                else:
                    return "Student", None

            # Age 18+: 70% student, 20% employed, 10% unemployed/jobless
            rand = random.random()
            if rand < 0.70:
                # Student
                student_fields = self.loader.load_student_fields(country)
                if student_fields:
                    field = random.choice(student_fields)
                    return f"Student of {field}", None
                else:
                    return "Student", None
            elif rand < 0.90:
                # Employed - only if there are age-appropriate jobs
                if age_appropriate_jobs:
                    return random.choice(age_appropriate_jobs), None
                else:
                    # No appropriate jobs, fallback to student
                    return "Student", None
            else:
                # Unemployed - only if there are age-appropriate jobs
                if age_appropriate_jobs:
                    previous_job = random.choice(age_appropriate_jobs)
                    return "Unemployed", previous_job
                else:
                    # No appropriate jobs, fallback to student
                    return "Student", None

        # Housewife probability for non-very_young females
        # Only if married/divorced with children, or married without children (less common)
        if gender == "female" and age_bucket != "very_young":
            housewife_probability = 0.0
            if marital_status == "Married" and has_children:
                housewife_probability = 0.15  # 15% if married with children
            elif marital_status == "Married":
                housewife_probability = 0.05  # 5% if married without children
            elif marital_status == "Divorced" and has_children:
                housewife_probability = 0.08  # 8% if divorced with children

            if random.random() < housewife_probability:
                return "Housewife", None

        # Unemployed (actively looking for work - "en paro")
        if random.random() < (unemployment_rate / 100.0):
            previous_job = random.choice(age_appropriate_jobs)
            return "Unemployed", previous_job

        # Jobless (not looking for work - "desempleado")
        if random.random() < (jobless_rate / 100.0):
            return "Jobless", None

        # Employed
        current_job = random.choice(age_appropriate_jobs)

        # People 40+ should have a previous job (career history)
        previous_job = None
        if age >= 40:
            # 80% chance of having a previous job
            if random.random() < 0.8:
                # Choose a different job as previous
                available_prev_jobs = [j for j in age_appropriate_jobs if j != current_job]
                if available_prev_jobs:
                    previous_job = random.choice(available_prev_jobs)

        return current_job, previous_job

    def _adjust_hair_color_for_age(self, age: int, hair_colors: Dict[str, float]) -> str:
        """
        Adjust hair color based on age.

        Older people are more likely to have gray/white hair.

        Args:
            age: Person's age
            hair_colors: Dict of hair colors with their base probabilities

        Returns:
            Selected hair color
        """
        adjusted_colors = hair_colors.copy()

        if age >= 60:
            # Seniors: 70% chance of gray/white
            if random.random() < 0.7:
                for color in adjusted_colors:
                    if 'Gray' in color or 'White' in color:
                        adjusted_colors[color] = adjusted_colors.get(color, 0) * 100
                    else:
                        adjusted_colors[color] = adjusted_colors.get(color, 0) * 0.1
        elif age >= 45:
            # Middle-aged: 30% chance of some gray
            if random.random() < 0.3:
                for color in adjusted_colors:
                    if 'Gray' in color:
                        adjusted_colors[color] = adjusted_colors.get(color, 0) * 50
                    else:
                        adjusted_colors[color] = adjusted_colors.get(color, 0) * 0.5

        return self._weighted_choice(adjusted_colors)

    def _generate_physical_characteristics(
        self,
        country: str,
        gender: str,
        age: int,
        rules: CountryRules
    ) -> Tuple[int, int, str, str, str]:
        """
        Generate height, weight, hair color, eye color, and skin tone.

        Applies age-based adjustments for realistic characteristics.

        Args:
            country: Country code
            gender: 'male' or 'female'
            age: Person's age
            rules: CountryRules object

        Returns:
            Tuple of (height_cm, weight_kg, hair_color, eye_color, skin_tone)
        """
        # Load height ranges
        heights = self.loader.load_heights(country, gender)

        # Select height category with age-based probabilities
        if age >= 80:
            # Very elderly: much more likely to be short
            if gender == 'female':
                # 80% Short, 19% Average, 1% Tall
                rand = random.random()
                if rand < 0.80:
                    height_category = "Short"
                elif rand < 0.99:
                    height_category = "Average"
                else:
                    height_category = "Tall"
            else:
                # 65% Short, 33% Average, 2% Tall
                rand = random.random()
                if rand < 0.65:
                    height_category = "Short"
                elif rand < 0.98:
                    height_category = "Average"
                else:
                    height_category = "Tall"
        elif age >= 60:
            # Elderly: More likely to be short/average
            if gender == 'female':
                # 60% Short, 38% Average, 2% Tall
                rand = random.random()
                if rand < 0.60:
                    height_category = "Short"
                elif rand < 0.98:
                    height_category = "Average"
                else:
                    height_category = "Tall"
            else:
                # 50% Short, 48% Average, 2% Tall
                rand = random.random()
                if rand < 0.50:
                    height_category = "Short"
                elif rand < 0.98:
                    height_category = "Average"
                else:
                    height_category = "Tall"
        else:
            # Adults under 60: 15% Short, 70% Average, 15% Tall
            rand = random.random()
            if rand < 0.15:
                height_category = "Short"
            elif rand < 0.85:
                height_category = "Average"
            else:
                height_category = "Tall"

        # Generate height within category
        min_h, max_h = heights[height_category]
        height_cm = random.randint(min_h, max_h)

        # Apply age-based height reduction (people lose height as they age)
        if age >= 60:
            decades_over_60 = (age - 60) / 10.0
            reduction_per_decade = 2 if gender == 'female' else 1.5
            height_reduction = int(decades_over_60 * reduction_per_decade)
            height_cm = max(height_cm - height_reduction, min_h - 5)

        # Load weight ranges
        weights = self.loader.load_weights(country, gender)

        # Select weight category strictly matching height category
        if height_category == "Short":
            allowed_weight_categories = [f"Short_Normal", f"Short_Underweight", f"Short_Overweight", f"Short_Obese"]
        elif height_category == "Average":
            allowed_weight_categories = [f"Average_Normal", f"Average_Underweight", f"Average_Overweight", f"Average_Obese"]
        else:  # Tall
            allowed_weight_categories = [f"Tall_Normal", f"Tall_Underweight", f"Tall_Overweight", f"Tall_Obese"]
        # Probabilidades: 70% Normal, 20% Underweight, 8% Overweight, 2% Obese (si existe)
        rand = random.random()
        if rand < 0.70:
            weight_category = allowed_weight_categories[0]
        elif rand < 0.90:
            weight_category = allowed_weight_categories[1]
        elif rand < 0.98:
            weight_category = allowed_weight_categories[2]
        else:
            weight_category = allowed_weight_categories[3] if len(allowed_weight_categories) > 3 else allowed_weight_categories[2]
        min_w, max_w = weights[weight_category]
        weight_kg = random.randint(min_w, max_w)

        # Physical characteristics with weighted probabilities
        hair_colors = rules.get_hair_colors()
        eye_colors = rules.get_eye_colors()
        skin_tones = rules.get_skin_tones()

        hair_color = self._adjust_hair_color_for_age(age, hair_colors)
        eye_color = self._weighted_choice(eye_colors)
        skin_tone = self._weighted_choice(skin_tones)

        return height_cm, weight_kg, hair_color, eye_color, skin_tone

    def _generate_family(
        self,
        country: str,
        age: int,
        gender: str,
        surnames: List[str],
        rules: Any,
        social_class: str = "Middle"
    ) -> Dict[str, Any]:
        """
        Generate realistic family information based on age.
        Supports multiple divorces, remarriage, and relationship history.

        Args:
            country: Country code for name generation
            age: Person's age
            gender: Person's gender
            surnames: Person's surnames (for children)
            rules: CountryRules object

        Returns:
            Dictionary with marital_status, partner, ex_partners (list), relationship_history, father, mother, children
        """
        # Age-based probabilities for marital status and children
        if age < 25:
            # Young adults: mostly single, very low chance of children
            has_partner_prob = 0.20
            has_children_prob = 0.05
            is_divorced_prob = 0.01
            multiple_divorces_prob = 0.0
        elif age < 35:
            # Young professionals: increasing family probability
            has_partner_prob = 0.50
            has_children_prob = 0.30
            is_divorced_prob = 0.05
            multiple_divorces_prob = 0.01
        elif age < 50:
            # Middle age: high probability of family
            has_partner_prob = 0.70
            has_children_prob = 0.65
            is_divorced_prob = 0.15
            multiple_divorces_prob = 0.05
        elif age < 65:
            # Late middle age: very high probability, some divorced
            has_partner_prob = 0.65
            has_children_prob = 0.75
            is_divorced_prob = 0.20
            multiple_divorces_prob = 0.10
        else:
            # Elderly: high probability, many may be widowed (treated as single here)
            has_partner_prob = 0.55
            has_children_prob = 0.85
            is_divorced_prob = 0.15
            multiple_divorces_prob = 0.15

        # Add girlfriend/boyfriend status for young people
        if age < 30:
            has_gf_bf_prob = 0.45
        elif age < 40:
            has_gf_bf_prob = 0.25
        elif age < 50:
            has_gf_bf_prob = 0.10
        elif age < 65:
            has_gf_bf_prob = 0.03
        else:
            has_gf_bf_prob = 0.0  # Elderly: never assign 'Girlfriend'/'Boyfriend' status

        # Determine base marital status
        rand = random.random()
        if rand < is_divorced_prob:
            marital_status = "Divorced"
        elif rand < (is_divorced_prob + has_gf_bf_prob):
            marital_status = "Girlfriend" if gender == 'male' else "Boyfriend"
        elif rand < (is_divorced_prob + has_gf_bf_prob + has_partner_prob):
            marital_status = "Married"
        else:
            marital_status = "Single"

        # Determine number of divorces for divorced people
        num_divorces = 1
        if marital_status == "Divorced" and random.random() < multiple_divorces_prob:
            # Multiple divorces (more likely for older people)
            if age >= 65:
                num_divorces = random.randint(2, 3)
            elif age >= 50:
                num_divorces = random.randint(2, 3)
            else:
                num_divorces = 2

        # Generate current year and date format (needed for partners)
        from datetime import datetime
        current_year = datetime.now().year
        date_format = rules.get_date_format()

        # Initialize partner and ex_partners list
        partner = None
        ex_partners = []  # List of all ex-partners (for multiple divorces)
        relationship_history = []  # Past relationships for singles
        surname_count = rules.get_surname_count() if hasattr(rules, 'get_surname_count') else 1
        opposite_gender = 'female' if gender == 'male' else 'male'
        partner_surnames_list = self.loader.load_surnames(country, opposite_gender)

        # Helper function to generate a partner/ex-partner
        def generate_partner_info(is_current_partner=False, for_marriage_num=None):
            """Generate partner information with all required fields."""
            partner_age = age + random.randint(-5, 5)
            if partner_age < 18:
                partner_age = 18
            partner_name = self.loader.load_name_by_age(country, opposite_gender, partner_age)

            if surname_count == 2:
                partner_surnames = []
                while len(partner_surnames) < 2:
                    s = random.choice(partner_surnames_list)
                    if s not in partner_surnames:
                        partner_surnames.append(s)
                partner_surname_str = f"{partner_surnames[0]} {partner_surnames[1]}"
            else:
                partner_surnames = [random.choice(partner_surnames_list)]
                partner_surname_str = partner_surnames[0]

            return {
                "name": partner_name,
                "surname": partner_surname_str,
                "gender": opposite_gender,
                "surnames": partner_surnames,
                "age": partner_age
            }

        # Helper function to generate marriage/divorce dates
        def generate_marriage_dates(marriage_num, total_marriages, current_age, is_current_marriage=False):
            """Generate realistic marriage and divorce dates.

            Args:
                marriage_num: Which marriage this is (1, 2, 3, etc.)
                total_marriages: Total number of marriages person has had
                current_age: Person's current age
                is_current_marriage: True if this marriage is still ongoing (not divorced)
            """
            # Calculate years per marriage roughly
            years_since_18 = current_age - 18
            avg_years_per_marriage = years_since_18 / total_marriages if total_marriages > 0 else 5

            # First marriage: typically between age 20-35
            if marriage_num == 1:
                max_marriage_age = max(20, min(35, current_age - 2))
                marriage_age = random.randint(min(20, max_marriage_age), max_marriage_age)
            else:
                # Later marriages: after previous divorce + some time
                prev_divorce_age = (marriage_num - 1) * avg_years_per_marriage + 18
                marriage_age = int(prev_divorce_age + random.randint(1, 4))
                marriage_age = min(marriage_age, current_age - 1)

            # CRITICAL: Marriage age can NEVER be >= current age (would create future dates)
            if marriage_age >= current_age:
                marriage_age = max(18, current_age - 1)

            # Marriage duration: 2-15 years typically
            if is_current_marriage:
                # Current/ongoing marriage - no divorce
                divorce_age = None
                marriage_duration = current_age - marriage_age
            else:
                # Ended in divorce - ALWAYS has end_date
                max_duration = max(2, min(15, current_age - marriage_age))
                marriage_duration = random.randint(2, max_duration) if max_duration >= 2 else 1
                divorce_age = marriage_age + marriage_duration

            # Generate actual dates
            marriage_year = current_year - (current_age - marriage_age)

            # CRITICAL: Final safety check - year can NEVER be in the future
            if marriage_year > current_year:
                marriage_year = current_year - random.randint(0, 3)
            marriage_month = random.randint(1, 12)
            marriage_day = random.randint(1, 28)

            if date_format == "DD/MM/YYYY":
                marriage_date = f"{marriage_day:02d}/{marriage_month:02d}/{marriage_year}"
            elif date_format == "MM/DD/YYYY":
                marriage_date = f"{marriage_month:02d}/{marriage_day:02d}/{marriage_year}"
            else:
                marriage_date = f"{marriage_year}/{marriage_month:02d}/{marriage_day:02d}"

            divorce_date = None
            if divorce_age is not None:
                divorce_year = current_year - (current_age - divorce_age)
                divorce_month = random.randint(1, 12)
                divorce_day = random.randint(1, 28)

                if date_format == "DD/MM/YYYY":
                    divorce_date = f"{divorce_day:02d}/{divorce_month:02d}/{divorce_year}"
                elif date_format == "MM/DD/YYYY":
                    divorce_date = f"{divorce_month:02d}/{divorce_day:02d}/{divorce_year}"
                else:
                    divorce_date = f"{divorce_year}/{divorce_month:02d}/{divorce_day:02d}"

            return marriage_date, divorce_date, marriage_duration

        # Current partner for Married/Girlfriend/Boyfriend
        if marital_status in ("Married", "Girlfriend", "Boyfriend"):
            partner_info = generate_partner_info(is_current_partner=True)
            birth_date, current_age = self._generate_birth_date(partner_info["age"], current_year, date_format)

            # Generate start date for relationship
            if marital_status in ("Girlfriend", "Boyfriend"):
                # Dating relationship - typically shorter duration
                max_duration = max(1, min(5, age - 18))  # Ensure at least 1
                relationship_duration = random.randint(1, max_duration)
                years_ago = min(relationship_duration, max(1, age - 18))

                # CRITICAL: Ensure BOTH people were at least 16 when relationship started
                # Calculate how old each person was at relationship start
                person_age_at_start = age - years_ago
                partner_age_at_start = current_age - years_ago

                # If either was under 16, adjust years_ago so both are at least 16
                MIN_RELATIONSHIP_AGE = 16
                if person_age_at_start < MIN_RELATIONSHIP_AGE:
                    years_ago = age - MIN_RELATIONSHIP_AGE
                if partner_age_at_start < MIN_RELATIONSHIP_AGE:
                    years_ago = min(years_ago, current_age - MIN_RELATIONSHIP_AGE)

                # Ensure years_ago is at least 1 (can't start in the future)
                years_ago = max(1, years_ago)

                start_year = current_year - years_ago

                # CRITICAL: FINAL SAFETY CHECK - start year can NEVER be in future or current year
                if start_year >= current_year:
                    start_year = current_year - 1

                start_month = random.randint(1, 12)
                start_day = random.randint(1, 28)

                if date_format == "DD/MM/YYYY":
                    start_date = f"{start_day:02d}/{start_month:02d}/{start_year}"
                elif date_format == "MM/DD/YYYY":
                    start_date = f"{start_month:02d}/{start_day:02d}/{start_year}"
                else:
                    start_date = f"{start_year}/{start_month:02d}/{start_day:02d}"
            else:
                # Married - use marriage date
                # CRITICAL: Both people must be at least 18 when married (legal age in Spain)
                # BUT: Marriage <22 is statistically rare in modern Spain, avoid unless specific context
                MIN_LEGAL_AGE = 18
                MIN_REALISTIC_AGE = 22  # More realistic minimum for most marriages

                # CRITICAL: max_marriage_age MUST be less than current age (can't marry in future/present)
                max_marriage_age = min(40, age - 2)  # At least 2 years ago

                # Ensure max_marriage_age is valid
                if max_marriage_age < MIN_LEGAL_AGE:
                    max_marriage_age = min(MIN_LEGAL_AGE, age - 1)

                # Determine realistic minimum based on social class and context
                # Only allow early marriage (18-21) for high/upper-middle class
                if social_class in ["High", "Upper-middle"]:
                    # High class can marry younger (family wealth, stability)
                    min_marriage_age = max(MIN_LEGAL_AGE, min(20, max_marriage_age))
                else:
                    # Low/middle class: marriage typically 22+ (need financial stability)
                    min_marriage_age = max(MIN_REALISTIC_AGE, min(24, max_marriage_age))

                # CRITICAL: Ensure min_marriage_age < max_marriage_age and both < age
                min_marriage_age = min(min_marriage_age, max_marriage_age - 1)
                if min_marriage_age >= age:
                    min_marriage_age = max(MIN_LEGAL_AGE, age - 3)
                if max_marriage_age >= age:
                    max_marriage_age = age - 1

                # FINAL SAFETY: marriage_age MUST be at least 1 year less than current age
                marriage_age = random.randint(min_marriage_age, max(min_marriage_age, max_marriage_age))
                if marriage_age >= age:
                    marriage_age = max(MIN_LEGAL_AGE, age - 1)

                years_married = age - marriage_age

                # CRITICAL: Verify years_married is positive
                if years_married <= 0:
                    years_married = 1
                    marriage_age = age - 1

                # Verify partner was also at least 18 when married
                partner_age_at_marriage = current_age - years_married
                if partner_age_at_marriage < MIN_LEGAL_AGE:
                    # Adjust: marriage happened more recently so partner was at least 18
                    years_married = current_age - MIN_LEGAL_AGE
                    marriage_age = age - years_married

                marriage_year = current_year - years_married

                # CRITICAL: FINAL SAFETY CHECK - marriage year can NEVER be in future or current year
                if marriage_year >= current_year:
                    marriage_year = current_year - random.randint(1, 3)

                marriage_month = random.randint(1, 12)
                marriage_day = random.randint(1, 28)

                if date_format == "DD/MM/YYYY":
                    start_date = f"{marriage_day:02d}/{marriage_month:02d}/{marriage_year}"
                elif date_format == "MM/DD/YYYY":
                    start_date = f"{marriage_month:02d}/{marriage_day:02d}/{marriage_year}"
                else:
                    start_date = f"{marriage_year}/{marriage_month:02d}/{marriage_day:02d}"

            partner = {
                "name": partner_info["name"],
                "surname": partner_info["surname"],
                "gender": opposite_gender,
                "surnames": partner_info["surnames"],
                "deceased": False,
                "birth_date": birth_date,
                "current_age": current_age,
                "start_date": start_date,
                "marriage_date": start_date if marital_status == "Married" else None
            }

        # Generate ex-partners for divorced people (support multiple divorces)
        if marital_status == "Divorced":
            # After divorce, person might have remarried
            remarried = random.random() < 0.40  # 40% chance of remarriage after divorce

            if remarried:
                # Change status to Married and generate current partner
                marital_status = "Married"
                partner_info = generate_partner_info(is_current_partner=True)
                birth_date, current_age = self._generate_birth_date(partner_info["age"], current_year, date_format)

                # Current marriage is the most recent (still ongoing)
                marriage_date, _, _ = generate_marriage_dates(num_divorces + 1, num_divorces + 1, age, is_current_marriage=True)

                partner = {
                    "name": partner_info["name"],
                    "surname": partner_info["surname"],
                    "gender": opposite_gender,
                    "surnames": partner_info["surnames"],
                    "deceased": False,
                    "birth_date": birth_date,
                    "current_age": current_age,
                    "start_date": marriage_date,
                    "marriage_date": marriage_date
                }

            # Generate all ex-partners (previous marriages)
            for marriage_num in range(1, num_divorces + 1):
                ex_info = generate_partner_info(for_marriage_num=marriage_num)

                # 10% chance ex-partner is deceased
                ex_deceased = random.random() < 0.10

                # Generate marriage and divorce dates
                marriage_date, divorce_date, duration = generate_marriage_dates(
                    marriage_num,
                    num_divorces if not remarried else num_divorces + 1,
                    age
                )

                if ex_deceased:
                    # Ex-partner died (which ended the marriage)
                    death_info = self._generate_death_info(ex_info["age"], current_year, date_format, rules)
                    divorce_cause = f"Death of spouse ({death_info['cause_of_death']})"
                    ex_partner = {
                        "name": ex_info["name"],
                        "surname": ex_info["surname"],
                        "gender": opposite_gender,
                        "surnames": ex_info["surnames"],
                        "deceased": True,
                        "marriage_date": marriage_date,
                        "end_date": divorce_date,
                        "duration": duration,
                        "divorce_cause": divorce_cause,
                        "marriage_number": marriage_num,
                        **death_info
                    }
                else:
                    # Ex-partner is alive, normal divorce
                    birth_date, current_age = self._generate_birth_date(ex_info["age"], current_year, date_format)

                    # Load breakup reasons and handle cheating with 50/50 distribution
                    breakup_reasons = self.loader.load_breakup_reasons()
                    divorce_cause = random.choice(breakup_reasons) if breakup_reasons else "Irreconcilable differences"

                    # Handle cheating with 50/50 gender distribution
                    if "cheated" in divorce_cause.lower():
                        if random.random() < 0.5:
                            # Person cheated on partner
                            pronoun_subject = "He" if gender == "male" else "She"
                            pronoun_object = "her" if opposite_gender == "female" else "him"
                            divorce_cause = f"{pronoun_subject} cheated on {pronoun_object}"
                        else:
                            # Partner cheated on person
                            pronoun_subject = "She" if opposite_gender == "female" else "He"
                            pronoun_object = "him" if gender == "male" else "her"
                            divorce_cause = f"{pronoun_subject} cheated on {pronoun_object}"

                    ex_partner = {
                        "name": ex_info["name"],
                        "surname": ex_info["surname"],
                        "gender": opposite_gender,
                        "surnames": ex_info["surnames"],
                        "deceased": False,
                        "birth_date": birth_date,
                        "current_age": current_age,
                        "marriage_date": marriage_date,
                        "end_date": divorce_date,
                        "duration": duration,
                        "divorce_cause": divorce_cause,
                        "marriage_number": marriage_num
                    }

                ex_partners.append(ex_partner)

        # Generate relationship history for singles (past boyfriends/girlfriends)
        if marital_status == "Single" and age >= 20:
            # 60% chance of having past relationships
            if random.random() < 0.60:
                max_past_rels = max(1, min(3, (age - 18) // 5))
                num_past_relationships = random.randint(1, max_past_rels)

                # Helper function to check for date range overlaps
                def dates_overlap(start1_year, end1_year, start2_year, end2_year):
                    """Check if two date ranges overlap."""
                    return not (end1_year < start2_year or end2_year < start1_year)

                used_date_ranges = []  # Track all used date ranges to prevent overlaps

                for i in range(num_past_relationships):
                    past_partner_info = generate_partner_info()
                    birth_date, current_age = self._generate_birth_date(past_partner_info["age"], current_year, date_format)

                    # Generate relationship duration and dates with overlap prevention
                    max_attempts = 10  # Try up to 10 times to find non-overlapping dates
                    found_valid_dates = False

                    for attempt in range(max_attempts):
                        max_rel_duration = max(1, min(5, age - 20))
                        relationship_duration = random.randint(1, max_rel_duration)
                        max_years_ago = max(1, min(10, age - 20))
                        years_ago_ended = random.randint(1, max_years_ago)

                        end_year = current_year - years_ago_ended
                        end_month = random.randint(1, 12)
                        end_day = random.randint(1, 28)

                        start_year = end_year - relationship_duration
                        start_month = random.randint(1, 12)
                        start_day = random.randint(1, 28)

                        # Check for overlaps with existing relationships
                        has_overlap = False
                        for existing_start_year, existing_end_year in used_date_ranges:
                            if dates_overlap(start_year, end_year, existing_start_year, existing_end_year):
                                has_overlap = True
                                break

                        if not has_overlap:
                            # Found valid non-overlapping dates
                            found_valid_dates = True
                            used_date_ranges.append((start_year, end_year))
                            break

                    # Skip this relationship if we couldn't find non-overlapping dates
                    if not found_valid_dates:
                        continue

                    if date_format == "DD/MM/YYYY":
                        start_date = f"{start_day:02d}/{start_month:02d}/{start_year}"
                        end_date = f"{end_day:02d}/{end_month:02d}/{end_year}"
                    elif date_format == "MM/DD/YYYY":
                        start_date = f"{start_month:02d}/{start_day:02d}/{start_year}"
                        end_date = f"{end_month:02d}/{end_day:02d}/{end_year}"
                    else:
                        start_date = f"{start_year}/{start_month:02d}/{start_day:02d}"
                        end_date = f"{end_year}/{end_month:02d}/{end_day:02d}"

                    # Load breakup reasons and handle cheating with 50/50 distribution
                    breakup_reasons = self.loader.load_breakup_reasons()
                    breakup_reason = random.choice(breakup_reasons) if breakup_reasons else "Grew apart"

                    # Handle cheating with 50/50 gender distribution
                    if "cheated" in breakup_reason.lower():
                        if random.random() < 0.5:
                            # Person cheated on partner
                            pronoun_subject = "He" if gender == "male" else "She"
                            pronoun_object = "her" if opposite_gender == "female" else "him"
                            breakup_reason = f"{pronoun_subject} cheated on {pronoun_object}"
                        else:
                            # Partner cheated on person
                            pronoun_subject = "She" if opposite_gender == "female" else "He"
                            pronoun_object = "him" if gender == "male" else "her"
                            breakup_reason = f"{pronoun_subject} cheated on {pronoun_object}"

                    relationship_history.append({
                        "name": past_partner_info["name"],
                        "surname": past_partner_info["surname"],
                        "gender": opposite_gender,
                        "surnames": past_partner_info["surnames"],
                        "birth_date": birth_date,
                        "current_age": current_age,
                        "start_date": start_date,
                        "end_date": end_date,
                        "duration": relationship_duration,
                        "breakup_reason": breakup_reason
                    })

        # Generate parents with death probability based on identity's age
        # Get identity's age bucket to determine death probability
        identity_age_bucket = self._get_age_bucket_from_age(age, rules)
        parent_death_prob = rules.get_death_probability("parents", identity_age_bucket)

        # Generate current year from identity's date of birth
        from datetime import datetime
        current_year = datetime.now().year
        date_format = rules.get_date_format()

        # Generate parents (father and mother)
        # Get parent age gap rules
        parent_min_gap = rules.get_parent_min_age_gap()
        parent_max_gap = rules.get_parent_max_age_gap()

        # Get life expectancy first (needed for realistic age caps)
        life_expectancy = rules.get_life_expectancy()

        # Father age: use min/max gap from rules
        # REALISTIC: Most living parents don't exceed 85-90 years
        # If they would be older, they're probably deceased
        MAX_REALISTIC_LIVING_PARENT_AGE = life_expectancy + random.randint(0, 5)  # 83-88 for Spain
        MAX_PARENT_AGE_DIFFERENCE = 15  # Maximum age difference between parents for credibility

        father_age = age + random.randint(parent_min_gap, parent_max_gap)
        # If father would be too old, cap at realistic max age
        if father_age > MAX_REALISTIC_LIVING_PARENT_AGE:
            father_age = MAX_REALISTIC_LIVING_PARENT_AGE

        # Mother age: respect fertility limits as well
        # Mother must have been between fertility_min and fertility_max when giving birth
        fertility_min = rules.get_female_fertility_min_age()
        fertility_max = rules.get_female_fertility_max_age()

        # Mother's age must be in range where she could have given birth
        # Min: age + fertility_min (she was at least fertility_min when giving birth)
        # Max: age + fertility_max (she was at most fertility_max when giving birth)
        mother_min_age = age + fertility_min
        mother_max_age = age + fertility_max

        # Also respect the general parent_max_gap rule
        mother_max_age = min(mother_max_age, age + parent_max_gap)

        # Cap mother's age at realistic maximum for living parents
        mother_max_age = min(mother_max_age, MAX_REALISTIC_LIVING_PARENT_AGE)

        # Limit the age difference between parents to be more realistic
        # Ensure mother is within MAX_PARENT_AGE_DIFFERENCE years of father
        mother_max_age = min(mother_max_age, father_age + MAX_PARENT_AGE_DIFFERENCE)
        mother_min_age = max(mother_min_age, father_age - MAX_PARENT_AGE_DIFFERENCE)

        # CRITICAL: Ensure mother_min_age doesn't exceed mother_max_age
        # If it does, it means parents MUST be deceased (person is too old for living parents with valid biology)
        if mother_min_age > mother_max_age:
            # Person is too old to have living parents with biologically valid ages
            # Force both parents to be deceased
            father_deceased = True
            mother_deceased = True

            # For deceased parents, calculate their ages ensuring BIOLOGICAL VALIDITY
            # Mother MUST have been between fertility_min and fertility_max when person was born
            # Mother's birth year = person's birth year - mother's age when person was born

            # Choose a realistic fertility age (weighted towards middle of range)
            fertility_age_at_birth = random.randint(fertility_min + 5, min(fertility_max - 5, fertility_min + 15))
            fertility_age_at_birth = max(fertility_min, min(fertility_age_at_birth, fertility_max))

            # Calculate mother's birth year based on when she had the person
            person_birth_year = current_year - age
            mother_birth_year = person_birth_year - fertility_age_at_birth

            # Mother's age if she were alive today (but she'll be marked as deceased)
            mother_age = current_year - mother_birth_year

            # Father should be slightly older (respecting parent age gap)
            father_age_gap = random.randint(2, min(MAX_PARENT_AGE_DIFFERENCE, 8))
            father_birth_year = mother_birth_year - father_age_gap
            father_age = current_year - father_birth_year
        else:
            # Normal case: valid age range for potentially living parents
            if mother_min_age == mother_max_age:
                mother_age = mother_min_age
            else:
                mother_age = random.randint(mother_min_age, mother_max_age)

        # CRITICAL: FINAL VALIDATION - Ensure biological validity
        # Calculate what mother's age was when person was born
        person_birth_year = current_year - age
        mother_birth_year = current_year - mother_age
        mother_age_at_person_birth = person_birth_year - mother_birth_year

        # If mother's age at birth violates fertility rules, FIX IT
        if mother_age_at_person_birth < fertility_min:
            # Mother was too young - make her older
            mother_age_at_person_birth = fertility_min + random.randint(0, 5)
            mother_birth_year = person_birth_year - mother_age_at_person_birth
            mother_age = current_year - mother_birth_year
            # Mother must be deceased if very old
            if mother_age > MAX_REALISTIC_LIVING_PARENT_AGE:
                mother_deceased = True
        elif mother_age_at_person_birth > fertility_max:
            # Mother was too old - make her younger
            mother_age_at_person_birth = fertility_max - random.randint(0, 5)
            mother_birth_year = person_birth_year - mother_age_at_person_birth
            mother_age = current_year - mother_birth_year

        # Similarly validate father's age
        father_birth_year = current_year - father_age
        father_age_at_person_birth = person_birth_year - father_birth_year
        MIN_FATHER_AGE = 16
        MAX_FATHER_AGE = 70

        if father_age_at_person_birth < MIN_FATHER_AGE:
            # Father was too young - make him older
            father_age_at_person_birth = MIN_FATHER_AGE + random.randint(2, 8)
            father_birth_year = person_birth_year - father_age_at_person_birth
            father_age = current_year - father_birth_year
            # Father must be deceased if very old
            if father_age > MAX_REALISTIC_LIVING_PARENT_AGE:
                father_deceased = True
        elif father_age_at_person_birth > MAX_FATHER_AGE:
            # Father was too old - make him younger
            father_age_at_person_birth = MAX_FATHER_AGE - random.randint(0, 10)
            father_birth_year = person_birth_year - father_age_at_person_birth
            father_age = current_year - father_birth_year

        # Use bucket offset +2 for parents (or clamp to max)
        father_name = self.loader.load_name_by_age(country, 'male', age, bucket_offset=2)
        mother_name = self.loader.load_name_by_age(country, 'female', age, bucket_offset=2)
        # Load gender-appropriate surnames for parents
        father_surnames_list = self.loader.load_surnames(country, 'male')
        mother_surnames_list = self.loader.load_surnames(country, 'female')

        # Father's first surname = person's first surname (convert to male version if needed)
        if surname_count == 1:
            # Single-surname system with gendered surnames (e.g., Russia)
            # Need to convert person's surname to father's gender
            if gender == 'male':
                # Person is male, surname is already masculine
                father_first_surname = surnames[0]
            else:
                # Person is female, need to convert surname to masculine
                female_surnames = self.loader.load_surnames(country, 'female')
                male_surnames = self.loader.load_surnames(country, 'male')
                try:
                    idx = female_surnames.index(surnames[0])
                    father_first_surname = male_surnames[idx] if idx < len(male_surnames) else surnames[0]
                except (ValueError, IndexError):
                    father_first_surname = random.choice(father_surnames_list)
        else:
            # Two-surname system (Spain) - no gender conversion needed
            father_first_surname = surnames[0] if surnames else random.choice(father_surnames_list)
        # Father's second surname is random
        father_second_surname = random.choice(father_surnames_list)
        # Ensure father's surnames are different
        while father_second_surname == father_first_surname:
            father_second_surname = random.choice(father_surnames_list)

        # Build parent surnames based on surname count
        if surname_count == 2:
            # Two-surname system (e.g., Spain)
            father_surname_str = f"{father_first_surname} {father_second_surname}"
            # Mother's first surname = person's second surname (if exists)
            mother_first_surname = surnames[1] if len(surnames) > 1 else random.choice(mother_surnames_list)
            mother_second_surname = random.choice(mother_surnames_list)
            while mother_second_surname == mother_first_surname:
                mother_second_surname = random.choice(mother_surnames_list)
            mother_surname_str = f"{mother_first_surname} {mother_second_surname}"
        else:
            # Single-surname system (e.g., Russia)
            father_surname_str = father_first_surname
            # Mother has her own maiden surname (random)
            mother_maiden_surname = random.choice(mother_surnames_list)
            # Ensure it's different from father's
            while mother_maiden_surname == father_first_surname:
                mother_maiden_surname = random.choice(mother_surnames_list)
            mother_surname_str = mother_maiden_surname

        # Determine if parents are deceased
        # CRITICAL: Parents MUST be dead if they exceed life expectancy
        # (life_expectancy already loaded above)

        # REALISTIC DEATH PROBABILITY BASED ON AGE
        # If parent is 80+, very high chance they're dead
        # If parent is 75-80, high chance they're dead
        # If identity is 60+, parents are almost certainly dead

        father_exceeds_life_expectancy = father_age > life_expectancy
        mother_exceeds_life_expectancy = mother_age > life_expectancy

        # Boost death probability for very old parents or old identities
        adjusted_parent_death_prob = parent_death_prob

        # If identity is old (60+), parents are almost certainly dead
        if age >= 70:
            adjusted_parent_death_prob = max(adjusted_parent_death_prob, 95)  # 95% chance
        elif age >= 60:
            adjusted_parent_death_prob = max(adjusted_parent_death_prob, 85)  # 85% chance
        elif age >= 50:
            adjusted_parent_death_prob = max(adjusted_parent_death_prob, 60)  # 60% chance

        # If parent age is very high, increase death probability
        if father_age >= 80 or mother_age >= 80:
            adjusted_parent_death_prob = max(adjusted_parent_death_prob, 85)

        if father_exceeds_life_expectancy and mother_exceeds_life_expectancy:
            # Both parents exceed life expectancy - MUST be dead
            father_deceased = True
            mother_deceased = True
        elif father_exceeds_life_expectancy:
            # Father exceeds life expectancy - MUST be dead
            father_deceased = True
            # Mother might be alive or dead based on adjusted probabilities
            mother_deceased = random.random() * 100 < adjusted_parent_death_prob
        elif mother_exceeds_life_expectancy:
            # Mother exceeds life expectancy - MUST be dead
            mother_deceased = True
            # Father might be alive or dead based on adjusted probabilities
            father_deceased = random.random() * 100 < adjusted_parent_death_prob
        else:
            # Neither parent exceeds life expectancy - use adjusted probabilities
            # Both parents dead should be less probable than one parent dead (unless identity is very old)
            if age >= 60:
                # Old identity: high chance both parents dead
                both_parents_dead_prob = adjusted_parent_death_prob * 0.7  # 70% of adjusted
                one_parent_dead_prob = adjusted_parent_death_prob * 0.25   # 25% of adjusted
            else:
                # Younger identity: normal distribution
                both_parents_dead_prob = adjusted_parent_death_prob * 0.3  # 30% of adjusted
                one_parent_dead_prob = adjusted_parent_death_prob * 0.7   # 70% of adjusted

            rand = random.random() * 100
            if rand < both_parents_dead_prob:
                # Both parents deceased
                father_deceased = True
                mother_deceased = True
            elif rand < (both_parents_dead_prob + one_parent_dead_prob):
                # One parent deceased (randomly choose which one)
                if random.random() < 0.5:
                    father_deceased = True
                    mother_deceased = False
                else:
                    father_deceased = False
                    mother_deceased = True
            else:
                # Both parents alive
                father_deceased = False
                mother_deceased = False

        # Build father dict
        if father_deceased:
            # For deceased parents, ensure they died at an age that makes sense
            # Father must have been at least parent_min_gap when identity was born
            # So minimum death age is: identity_age + parent_min_gap
            min_parent_death_age = age + parent_min_gap
            # Pass the validated birth_year to ensure biological validity
            death_info = self._generate_death_info_for_parent(father_age, current_year, date_format, rules, min_parent_death_age, age, birth_year=father_birth_year)
            father = {
                "name": father_name,
                "surname": father_surname_str,
                "deceased": True,
                **death_info
            }
        else:
            # For living fathers, use the validated birth_year
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            if date_format == "DD/MM/YYYY":
                birth_date = f"{birth_day:02d}/{birth_month:02d}/{father_birth_year}"
            elif date_format == "MM/DD/YYYY":
                birth_date = f"{birth_month:02d}/{birth_day:02d}/{father_birth_year}"
            else:
                birth_date = f"{father_birth_year}/{birth_month:02d}/{birth_day:02d}"

            father = {
                "name": father_name,
                "surname": father_surname_str,
                "deceased": False,
                "birth_date": birth_date,
                "current_age": father_age
            }

        # Build mother dict
        if mother_deceased:
            # For deceased mother, ensure she died at an age that makes sense
            # Mother must have been at least fertility_min when identity was born
            min_parent_death_age = age + fertility_min
            # Pass the validated birth_year to ensure biological validity
            death_info = self._generate_death_info_for_parent(mother_age, current_year, date_format, rules, min_parent_death_age, age, birth_year=mother_birth_year)

            # SPECIAL CASE: Mother died during childbirth (5% chance if died same year as birth)
            birth_year = current_year - age
            death_year = int(death_info['death_date'].split('/')[-1])  # Extract year from DD/MM/YYYY

            if death_year == birth_year and random.random() < 0.05:
                # Mother died in childbirth
                death_info['cause_of_death'] = "Childbirth complications"
                death_info['age_at_death'] = age + fertility_min  # Died giving birth

            mother = {
                "name": mother_name,
                "surname": mother_surname_str,
                "deceased": True,
                **death_info
            }
        else:
            # For living mothers, use the validated birth_year
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            if date_format == "DD/MM/YYYY":
                birth_date = f"{birth_day:02d}/{birth_month:02d}/{mother_birth_year}"
            elif date_format == "MM/DD/YYYY":
                birth_date = f"{birth_month:02d}/{birth_day:02d}/{mother_birth_year}"
            else:
                birth_date = f"{mother_birth_year}/{birth_month:02d}/{birth_day:02d}"

            mother = {
                "name": mother_name,
                "surname": mother_surname_str,
                "deceased": False,
                "birth_date": birth_date,
                "current_age": mother_age
            }

        # Generate children using country-specific rules
        children = []
        min_children = rules.get_min_children()
        max_children = rules.get_max_children()

        # Decide if this person will have children
        will_have_children = random.random() < has_children_prob

        # Dating relationships: can have children if together long enough and not too young
        # This is realistic - couples who've been together for years may have kids before marriage
        if marital_status in ("Girlfriend", "Boyfriend"):
            # Check relationship duration from partner info
            relationship_duration = 0
            if partner:
                # Calculate relationship duration from start_date
                start_date = partner.get("start_date", "")
                if start_date:
                    try:
                        # Parse DD/MM/YYYY format
                        parts = start_date.split('/')
                        if len(parts) == 3:
                            start_year = int(parts[2])
                            relationship_duration = current_year - start_year
                    except:
                        relationship_duration = 0

            # Allow children if:
            # - Together for 2+ years AND
            # - Person is 25+ years old AND
            # - Random chance (40%)
            if relationship_duration >= 2 and age >= 25 and random.random() < 0.4:
                # Can have children (usually just 1, rarely 2)
                will_have_children = True
                max_children = min(max_children, 2)  # Cap at 2 children for dating couples
            else:
                will_have_children = False

        # If single but will have children, must have had past marriage
        if will_have_children and marital_status == "Single" and not ex_partners:
            # Create a past marriage
            marital_status = "Divorced"
            ex_info = generate_partner_info()
            ex_deceased = random.random() < 0.10

            marriage_date, divorce_date, duration = generate_marriage_dates(1, 1, age)

            if ex_deceased:
                death_info = self._generate_death_info(ex_info["age"], current_year, date_format, rules)
                divorce_cause = f"Death of spouse ({death_info['cause_of_death']})"
                ex_partners.append({
                    "name": ex_info["name"],
                    "surname": ex_info["surname"],
                    "gender": opposite_gender,
                    "surnames": ex_info["surnames"],
                    "deceased": True,
                    "marriage_date": marriage_date,
                    "end_date": divorce_date,
                    "duration": duration,
                    "divorce_cause": divorce_cause,
                    "marriage_number": 1,
                    **death_info
                })
            else:
                birth_date, current_age = self._generate_birth_date(ex_info["age"], current_year, date_format)
                breakup_reasons = self.loader.load_breakup_reasons()
                divorce_cause = random.choice(breakup_reasons) if breakup_reasons else "Irreconcilable differences"

                # Handle cheating with 50/50 gender distribution
                if "cheated" in divorce_cause.lower():
                    if random.random() < 0.5:
                        pronoun_subject = "He" if gender == "male" else "She"
                        pronoun_object = "her" if opposite_gender == "female" else "him"
                        divorce_cause = f"{pronoun_subject} cheated on {pronoun_object}"
                    else:
                        pronoun_subject = "She" if opposite_gender == "female" else "He"
                        pronoun_object = "him" if gender == "male" else "her"
                        divorce_cause = f"{pronoun_subject} cheated on {pronoun_object}"

                ex_partners.append({
                    "name": ex_info["name"],
                    "surname": ex_info["surname"],
                    "gender": opposite_gender,
                    "surnames": ex_info["surnames"],
                    "deceased": False,
                    "birth_date": birth_date,
                    "current_age": current_age,
                    "marriage_date": marriage_date,
                    "end_date": divorce_date,
                    "duration": duration,
                    "divorce_cause": divorce_cause,
                    "marriage_number": 1
                })

        # Determine total number of marriages for child distribution
        # Include current partner relationship for Girlfriend/Boyfriend if they have children
        total_marriages = len(ex_partners) + (1 if marital_status in ("Married", "Girlfriend", "Boyfriend") else 0)

        # Assign children if married, has ex-partners, or in long-term dating relationship
        if will_have_children and (marital_status in ("Married", "Girlfriend", "Boyfriend") or ex_partners):
            avg_children = rules.get_average_children()

            # Determine total number of children
            if age < 30:
                total_children = random.randint(min_children, min(max_children, 2))
            else:
                total_children = random.randint(min_children, max_children)

            # Distribute children across marriages
            # Create a list to track how many children from each marriage
            children_per_marriage = {}

            if total_marriages == 1:
                # All children from single marriage
                children_per_marriage[1] = total_children
            elif total_marriages == 2:
                # Split children between two marriages (may be uneven)
                first_marriage_children = random.randint(0, total_children)
                children_per_marriage[1] = first_marriage_children
                children_per_marriage[2] = total_children - first_marriage_children
            elif total_marriages == 3:
                # Split between three marriages
                first = random.randint(0, total_children)
                remaining = total_children - first
                second = random.randint(0, remaining)
                third = remaining - second
                children_per_marriage[1] = first
                children_per_marriage[2] = second
                children_per_marriage[3] = third
            else:
                # More than 3 marriages - distribute randomly
                for i in range(1, total_marriages + 1):
                    children_per_marriage[i] = 0
                for _ in range(total_children):
                    marriage_num = random.randint(1, total_marriages)
                    children_per_marriage[marriage_num] += 1

            # Get children death probability
            children_death_prob = rules.get_death_probability("children", identity_age_bucket)

            # CRITICAL: Track used child ages to prevent impossible duplicates
            # If two children have same age, they MUST be twins with exact same birth date
            # LIMIT: Max 2 children per birth date (twins only, no triplets unless special case)
            used_child_ages = {}  # age -> birth_date (for twins tracking)
            birth_date_counts = {}  # birth_date -> count (to limit twins/triplets)
            used_child_names = set()  # NEVER allow duplicate child names
            used_child_pinyin = set()  # For China: also prevent same pinyin

            # Generate children for each marriage
            for marriage_num in range(1, total_marriages + 1):
                num_children_this_marriage = children_per_marriage.get(marriage_num, 0)

                # Determine which partner this marriage was with
                if marriage_num <= len(ex_partners):
                    # Child from ex-partner (past marriage)
                    marriage_partner = ex_partners[marriage_num - 1]
                else:
                    # Child from current partner
                    marriage_partner = partner

                if num_children_this_marriage == 0 or not marriage_partner:
                    continue

                for _ in range(num_children_this_marriage):
                    child_gender = random.choice(['male', 'female'])

                    # Generate unique child name (never duplicate, and for China never duplicate pinyin)
                    max_name_attempts = 50
                    for name_attempt in range(max_name_attempts):
                        child_name = self.loader.load_name_by_age(country, child_gender, age, bucket_offset=-2)

                        # Check exact name match
                        if child_name in used_child_names:
                            continue

                        # For China: also check pinyin
                        if country.lower() == 'china':
                            try:
                                from pypinyin import lazy_pinyin, Style
                                pinyin_list = lazy_pinyin(child_name, style=Style.NORMAL)
                                pinyin_name = ''.join([p for p in pinyin_list if p.strip()]).lower()

                                if pinyin_name in used_child_pinyin:
                                    continue
                                else:
                                    used_child_pinyin.add(pinyin_name)
                                    used_child_names.add(child_name)
                                    break
                            except:
                                used_child_names.add(child_name)
                                break
                        else:
                            used_child_names.add(child_name)
                            break
                    else:
                        # Fallback: add suffix to make unique
                        child_name = f"{child_name}{len(used_child_names)}"
                        used_child_names.add(child_name)

                    # Determine mother age from marriage partner
                    if gender == 'female':
                        mother_age = age
                    else:
                        # Mother is the marriage_partner
                        if marriage_partner.get('deceased'):
                            mother_age = marriage_partner.get('age_at_death', age)
                        else:
                            mother_age = marriage_partner.get('current_age', age)

                    # Get fertility limits
                    fertility_min = rules.get_female_fertility_min_age()
                    fertility_max = rules.get_female_fertility_max_age()
                    parent_min_gap = rules.get_parent_min_age_gap()

                    # Safety margins
                    FERTILITY_MIN_SAFE = fertility_min + 3  # e.g., 18 + 3 = 21
                    FERTILITY_MAX_SAFE = fertility_max - 3  # e.g., 45 - 3 = 42

                    # CRITICAL FIX: Calculate child age range correctly
                    # min_child_age = youngest possible child = mother gave birth at fertility_max
                    # max_child_age = oldest possible child = mother gave birth at fertility_min
                    min_child_age = max(0, mother_age - FERTILITY_MAX_SAFE)  # Youngest child
                    max_child_age = max(0, mother_age - FERTILITY_MIN_SAFE)  # Oldest child

                    # ABSOLUTE BIOLOGICAL LIMIT: No children born after mother turned 45
                    # If mother is currently > 45, youngest child must be at least (mother_age - 45) years old
                    if mother_age > 45:
                        absolute_min_child_age = mother_age - 45
                        min_child_age = max(min_child_age, absolute_min_child_age)

                    if age != mother_age:
                        max_child_age = min(max_child_age, age - parent_min_gap)

                    # Ensure valid range
                    if min_child_age > max_child_age:
                        min_child_age = max_child_age
                    if max_child_age < 0:
                        max_child_age = 0
                        min_child_age = 0

                    # CRITICAL: Limit child age based on marriage dates to ensure coherence
                    # Children must be born DURING the marriage (with 1 year margin)
                    if marriage_partner:
                        try:
                            # Get marriage start date
                            marriage_start_date = marriage_partner.get('marriage_date') or marriage_partner.get('start_date')
                            marriage_end_date = marriage_partner.get('end_date')  # None if current marriage

                            if marriage_start_date:
                                # Parse marriage start date (DD/MM/YYYY format)
                                start_parts = marriage_start_date.split('/')
                                if len(start_parts) == 3:
                                    marriage_start_year = int(start_parts[2])
                                    years_since_marriage = current_year - marriage_start_year

                                    # Child cannot be older than (years since marriage + 1)
                                    # +1 margin for conception before marriage
                                    max_child_age = min(max_child_age, years_since_marriage + 1)

                                    # If marriage has ended (divorce), limit by end date too
                                    if marriage_end_date:
                                        end_parts = marriage_end_date.split('/')
                                        if len(end_parts) == 3:
                                            marriage_end_year = int(end_parts[2])
                                            years_since_divorce = current_year - marriage_end_year

                                            # Child must be at least (years since divorce - 1) years old
                                            # -1 margin for late pregnancy after separation
                                            min_child_age = max(min_child_age, years_since_divorce - 1)
                        except Exception as e:
                            # If date parsing fails, use default age ranges
                            pass

                    # Additional check for current boyfriend/girlfriend relationships
                    if marriage_num == total_marriages and marital_status in ("Girlfriend", "Boyfriend"):
                        # This is current partner (boyfriend/girlfriend)
                        # Child must be younger than relationship duration
                        if partner and partner.get("start_date"):
                            try:
                                start_parts = partner["start_date"].split('/')
                                if len(start_parts) == 3:
                                    relationship_start_year = int(start_parts[2])
                                    relationship_duration = current_year - relationship_start_year
                                    # Child cannot be older than relationship duration (with 1 year margin)
                                    max_child_age = min(max_child_age, relationship_duration + 1)
                            except:
                                pass

                    # Generate child age
                    if max_child_age >= min_child_age and max_child_age > 0:
                        child_age = random.randint(min_child_age, max_child_age)
                    else:
                        child_age = 0

                    # CRITICAL VALIDATION: Verify mother was not older than 45 when giving birth
                    # This is an absolute biological limit
                    if gender == 'female':
                        # Person is the mother
                        mother_age_at_birth = age - child_age
                        if mother_age_at_birth > 45:
                            # Adjust child age so mother was exactly 45
                            child_age = age - 45
                            # Ensure child_age is non-negative
                            if child_age < 0:
                                child_age = 0
                    else:
                        # Person is the father, check partner (mother) age
                        mother_age_at_birth = mother_age - child_age
                        if mother_age_at_birth > 45:
                            # Adjust child age so mother was exactly 45
                            child_age = mother_age - 45
                            # Ensure child_age is non-negative
                            if child_age < 0:
                                child_age = 0

                    # Skip if child would be 0 years old or negative (edge case)
                    if child_age <= 0:
                        continue

                    # Inherit surnames from marriage partner
                    if surname_count == 2:
                        # Two-surname system
                        if gender == 'male':
                            child_surnames = [surnames[0], marriage_partner["surnames"][0]]
                        else:
                            child_surnames = [marriage_partner["surnames"][0], surnames[0]]
                        child_surname_str = f"{child_surnames[0]} {child_surnames[1]}"
                    else:
                        # Single-surname system with gender
                        if gender == 'male':
                            father_surname_source = surnames[0]
                            father_surname_gender = 'male'
                        else:
                            father_surname_source = marriage_partner["surnames"][0]
                            father_surname_gender = 'male'

                        # Convert to child's gender
                        if father_surname_gender == child_gender:
                            child_surname = father_surname_source
                        else:
                            male_surnames = self.loader.load_surnames(country, 'male')
                            female_surnames = self.loader.load_surnames(country, 'female')
                            try:
                                if father_surname_gender == 'male':
                                    idx = male_surnames.index(father_surname_source)
                                    child_surname = female_surnames[idx] if idx < len(female_surnames) else father_surname_source
                                else:
                                    idx = female_surnames.index(father_surname_source)
                                    child_surname = male_surnames[idx] if idx < len(male_surnames) else father_surname_source
                            except (ValueError, IndexError):
                                child_surname = father_surname_source

                        child_surnames = [child_surname]
                        child_surname_str = child_surname

                    # CRITICAL: Check if another child already has this age (twins)
                    # If so, they MUST have the same birth date
                    # LIMIT: Max 2 children per birth date (twins only, rarely triplets)
                    if child_age in used_child_ages:
                        # Check if this would create triplets (3+ children with same birth date)
                        potential_birth_date = used_child_ages[child_age]
                        existing_count = birth_date_counts.get(potential_birth_date, 0)

                        # For China specifically: triplets at age 45+ is extremely rare
                        # Allow max 2 twins, but regenerate age if would create triplets
                        if existing_count >= 2:
                            # Already have twins with this birth date
                            # Generate a different age for this child (adjust by 1 year)
                            if child_age + 1 <= max_child_age:
                                child_age = child_age + 1
                            elif child_age - 1 >= min_child_age:
                                child_age = child_age - 1
                            else:
                                # Can't adjust, skip this child
                                continue

                            # Generate new birth date for adjusted age
                            birth_date, _ = self._generate_birth_date(child_age, current_year, date_format)
                            is_twin = False
                        else:
                            # TWINS! Use the exact same birth date as the sibling
                            birth_date = potential_birth_date
                            is_twin = True
                    else:
                        # First child of this age - generate new birth date
                        birth_date, _ = self._generate_birth_date(child_age, current_year, date_format)
                        is_twin = False

                    # Track this birth date
                    used_child_ages[child_age] = birth_date
                    birth_date_counts[birth_date] = birth_date_counts.get(birth_date, 0) + 1

                    # Check if child is deceased
                    child_deceased = random.random() < (children_death_prob / 100.0)

                    if child_deceased:
                        death_info = self._generate_death_info(child_age, current_year, date_format, rules)
                        children.append({
                            "name": child_name,
                            "surname": child_surname_str,
                            "gender": child_gender,
                            "surnames": child_surnames,
                            "deceased": True,
                            "from_marriage": marriage_num,
                            "is_twin": is_twin,
                            **death_info
                        })
                    else:
                        children.append({
                            "name": child_name,
                            "surname": child_surname_str,
                            "gender": child_gender,
                            "surnames": child_surnames,
                            "deceased": False,
                            "birth_date": birth_date,
                            "current_age": child_age,  # Use child_age directly
                            "from_marriage": marriage_num,
                            "is_twin": is_twin
                        })
        # If will_have_children is False, children remains as empty list []

        # Generate siblings based on country's sibling probability
        siblings = []

        # Generate siblings (always possible now that orphan logic is removed)
        min_siblings = rules.get_min_siblings()
        max_siblings = rules.get_max_siblings()
        avg_siblings = rules.get_average_siblings()
        sibling_probability = rules.get_sibling_probability()
        siblings_death_prob = rules.get_death_probability("siblings", identity_age_bucket)

        # SPECIAL: One-child policy for China
        if country.lower() == 'china':
            # Calculate birth year from age
            from datetime import datetime
            current_year = datetime.now().year
            birth_year = current_year - age

            # Apply one-child policy rules based on birth year
            if birth_year < 1980:
                # Before one-child policy: More siblings allowed
                avg_siblings = float(rules.get('one_child_pre_1980_avg_siblings', 1.5))
                max_siblings = int(rules.get('one_child_pre_1980_max_siblings', 3))
                sibling_probability = 70  # Higher chance of siblings
            elif 1980 <= birth_year < 2000:
                # Strict one-child policy period
                avg_siblings = float(rules.get('one_child_1980_2000_avg_siblings', 0.3))
                max_siblings = int(rules.get('one_child_1980_2000_max_siblings', 1))
                sibling_probability = 25  # Very low chance of siblings
            elif 2000 <= birth_year < 2016:
                # One-child policy still in effect but slightly relaxed
                avg_siblings = float(rules.get('one_child_2000_2016_avg_siblings', 0.4))
                max_siblings = int(rules.get('one_child_2000_2016_max_siblings', 1))
                sibling_probability = 30  # Low chance of siblings
            elif 2016 <= birth_year < 2021:
                # Two-child policy
                avg_siblings = float(rules.get('one_child_2016_2021_avg_siblings', 0.8))
                max_siblings = int(rules.get('one_child_2016_2021_max_siblings', 2))
                sibling_probability = 55  # Moderate chance of siblings
            else:
                # Three-child policy (2021+)
                avg_siblings = float(rules.get('one_child_2021_plus_avg_siblings', 1.0))
                max_siblings = int(rules.get('one_child_2021_plus_max_siblings', 2))
                sibling_probability = 65  # Higher chance of siblings

        # Use sibling_probability to determine if person has siblings
        if random.random() < (sibling_probability / 100.0):
            # Determine number of siblings using Gaussian distribution around average
            num_siblings = min(max_siblings, max(1, int(random.gauss(avg_siblings, avg_siblings / 2.5))))

            # Track already used sibling ages (allow duplicates for twins) and names (NEVER duplicate)
            used_sibling_ages = {}  # age -> count (for twins/triplets detection)
            used_sibling_names = set()  # NEVER allow duplicate names
            used_sibling_pinyin = set()  # For China: also prevent same pinyin

            for _ in range(num_siblings):
                # Siblings are similar age - use same age bucket as identity
                sibling_gender = random.choice(['male', 'female'])

                # Generate unique name - NEVER duplicate (and for China, never duplicate pinyin)
                max_name_attempts = 50
                for name_attempt in range(max_name_attempts):
                    sibling_name = self.loader.load_name_by_age(country, sibling_gender, age, bucket_offset=0)

                    # Check exact name match (all countries)
                    if sibling_name in used_sibling_names:
                        continue

                    # For China: also check pinyin to avoid 子萱 (Zixuan) and 子轩 (Zixuan)
                    if country.lower() == 'china':
                        try:
                            from pypinyin import lazy_pinyin, Style
                            pinyin_list = lazy_pinyin(sibling_name, style=Style.NORMAL)
                            # Filter out spaces and join to get full pinyin
                            pinyin_name = ''.join([p for p in pinyin_list if p.strip()]).lower()

                            if pinyin_name in used_sibling_pinyin:
                                # Same pinyin, try another name
                                continue
                            else:
                                # Unique pinyin, use this name
                                used_sibling_pinyin.add(pinyin_name)
                                used_sibling_names.add(sibling_name)
                                break
                        except:
                            # If pypinyin fails, just check exact match
                            used_sibling_names.add(sibling_name)
                            break
                    else:
                        # Not China, just check exact match
                        used_sibling_names.add(sibling_name)
                        break
                else:
                    # Fallback: add number to make unique
                    sibling_name = f"{sibling_name}{len(used_sibling_names)}"
                    used_sibling_names.add(sibling_name)

                # Generate sibling age respecting mother's fertility limits
                # Mother must have been between fertility_min and fertility_max when giving birth to ALL children

                # CRITICAL: Calculate valid age range for siblings based on mother's BIRTH YEAR
                # Must extract birth year from mother's birth_date to ensure biological consistency
                mother_birth_date = mother.get('birth_date', '')
                try:
                    # Parse birth year from date format (DD/MM/YYYY, MM/DD/YYYY, or YYYY/MM/DD)
                    parts = mother_birth_date.split('/')
                    if len(parts) == 3:
                        # Try YYYY/MM/DD format first
                        if len(parts[0]) == 4:
                            mother_birth_year = int(parts[0])
                        # Then DD/MM/YYYY or MM/DD/YYYY (year is last)
                        else:
                            mother_birth_year = int(parts[2])
                    else:
                        # Fallback: calculate from age
                        mother_birth_year = current_year - (age + fertility_min + 10)
                except:
                    # Fallback: calculate from age
                    mother_birth_year = current_year - (age + fertility_min + 10)

                # Sibling age range: mother must have been between fertility_min and fertility_max when sibling was born
                # For each potential sibling age:
                #   sibling_birth_year = current_year - sibling_age
                #   mother_age_at_birth = sibling_birth_year - mother_birth_year
                #   Must satisfy: fertility_min <= mother_age_at_birth <= fertility_max

                # Max sibling age: mother was fertility_min when sibling was born
                #   sibling_birth_year = mother_birth_year + fertility_min
                #   max_sibling_age = current_year - sibling_birth_year
                max_sibling_age = current_year - (mother_birth_year + fertility_min)

                # Min sibling age: mother was fertility_max when sibling was born (or sibling is 1 year old)
                #   sibling_birth_year = mother_birth_year + fertility_max
                #   min_sibling_age = current_year - sibling_birth_year
                min_sibling_age = max(1, current_year - (mother_birth_year + fertility_max))

                # Also limit sibling age to +/- 15 years from identity for realism
                max_sibling_age = min(max_sibling_age, age + 15)
                min_sibling_age = max(min_sibling_age, max(1, age - 15))

                # CRITICAL Safety check: ensure valid range
                # If mother was too young or calculations are inconsistent, skip this sibling
                if max_sibling_age < 1 or min_sibling_age > max_sibling_age:
                    # Mother's age doesn't allow for valid siblings - skip this one
                    # This can happen if mother died very young or calculations are edge cases
                    continue  # Skip to next sibling iteration

                # ALLOW same age for twins/triplets (15% chance)
                max_attempts = 20
                allow_twins = random.random() < 0.15  # 15% chance of twins/triplets

                sibling_age = None
                for attempt in range(max_attempts):
                    # Generate age within valid fertility range
                    candidate_age = random.randint(min_sibling_age, max_sibling_age)

                    # CRITICAL: Double-check that BOTH parents had valid age when this sibling was born
                    sibling_birth_year = current_year - candidate_age
                    mother_age_at_sibling_birth = sibling_birth_year - mother_birth_year

                    # Get father's birth year for validation
                    father_birth_date = father.get('birth_date', '')
                    try:
                        parts = father_birth_date.split('/')
                        if len(parts) == 3:
                            father_birth_year = int(parts[2]) if len(parts[0]) <= 2 else int(parts[0])
                        else:
                            father_birth_year = current_year - father_age
                    except:
                        father_birth_year = current_year - father_age

                    father_age_at_sibling_birth = sibling_birth_year - father_birth_year

                    # Verify biological validity for MOTHER
                    if mother_age_at_sibling_birth < fertility_min or mother_age_at_sibling_birth > fertility_max:
                        # Mother would have been too young or too old - skip this age
                        continue

                    # Verify biological validity for FATHER (minimum age to father children: ~16, typical: 18+)
                    MIN_FATHER_AGE = 16
                    MAX_FATHER_AGE = 70  # Biologically possible but rare
                    if father_age_at_sibling_birth < MIN_FATHER_AGE or father_age_at_sibling_birth > MAX_FATHER_AGE:
                        # Father would have been too young or too old - skip this age
                        continue

                    # If twins allowed and we have an age with count < 3, can reuse
                    if allow_twins and candidate_age in used_sibling_ages and used_sibling_ages[candidate_age] < 3:
                        used_sibling_ages[candidate_age] += 1
                        sibling_age = candidate_age
                        is_twin = True
                        break
                    # Otherwise check if this age is available (not used yet)
                    elif candidate_age != age and candidate_age not in used_sibling_ages:
                        used_sibling_ages[candidate_age] = 1
                        sibling_age = candidate_age
                        is_twin = False
                        break

                # If no valid age found after all attempts, skip this sibling
                if sibling_age is None:
                    continue  # Skip to next sibling in the loop

                # Siblings inherit parents' surnames
                if surname_count == 2:
                    # Two-surname system: inherit from both parents
                    # Same as person: father's first surname + mother's first surname
                    sibling_surnames = surnames.copy()
                    sibling_surname_str = f"{surnames[0]} {surnames[1]}"
                else:
                    # Single-surname system with gendered surnames
                    # Need to get correct gender version of father's surname
                    if sibling_gender == 'male':
                        # Male sibling gets masculine version
                        if gender == 'male':
                            # Person is male, use same surname
                            sibling_surname = surnames[0]
                        else:
                            # Person is female, convert to masculine
                            female_surnames = self.loader.load_surnames(country, 'female')
                            male_surnames = self.loader.load_surnames(country, 'male')
                            try:
                                idx = female_surnames.index(surnames[0])
                                sibling_surname = male_surnames[idx] if idx < len(male_surnames) else surnames[0]
                            except (ValueError, IndexError):
                                sibling_surname = surnames[0]
                    else:
                        # Female sibling gets feminine version
                        if gender == 'female':
                            # Person is female, use same surname
                            sibling_surname = surnames[0]
                        else:
                            # Person is male, convert to feminine
                            male_surnames = self.loader.load_surnames(country, 'male')
                            female_surnames = self.loader.load_surnames(country, 'female')
                            try:
                                idx = male_surnames.index(surnames[0])
                                sibling_surname = female_surnames[idx] if idx < len(male_surnames) else surnames[0]
                            except (ValueError, IndexError):
                                sibling_surname = surnames[0]

                    sibling_surnames = [sibling_surname]
                    sibling_surname_str = sibling_surname

                # Determine if sibling is deceased
                sibling_deceased = random.random() < (siblings_death_prob / 100.0)

                if sibling_deceased:
                    death_info = self._generate_death_info(sibling_age, current_year, date_format, rules)
                    siblings.append({
                        "name": sibling_name,
                        "surname": sibling_surname_str,
                        "gender": sibling_gender,
                        "surnames": sibling_surnames,
                        "deceased": True,
                        "is_twin": is_twin,
                        **death_info
                    })
                else:
                    birth_date, current_age = self._generate_birth_date(sibling_age, current_year, date_format)
                    siblings.append({
                        "name": sibling_name,
                        "surname": sibling_surname_str,
                        "gender": sibling_gender,
                        "surnames": sibling_surnames,
                        "deceased": False,
                        "birth_date": birth_date,
                        "current_age": current_age,
                        "is_twin": is_twin
                    })

        # ADDITIONAL CASE: Mother could have died giving birth to ANY sibling
        # Check if mother died and if death date matches any sibling's birth year
        if mother.get('deceased') and siblings:
            mother_death_date = mother.get('death_date')
            if mother_death_date:
                mother_death_year = int(mother_death_date.split('/')[-1])  # Extract year from DD/MM/YYYY

                # Check each sibling's birth year
                for sibling in siblings:
                    sibling_birth_date = sibling.get('birth_date')
                    if sibling_birth_date:
                        sibling_birth_year = int(sibling_birth_date.split('/')[-1])

                        # If mother died in same year sibling was born (5% chance for childbirth complications)
                        if mother_death_year == sibling_birth_year and random.random() < 0.05:
                            # Mother died giving birth to this sibling
                            mother['cause_of_death'] = "Childbirth complications"
                            # Calculate age at death based on fertility age when giving birth
                            fertility_min = rules.get_female_fertility_min_age()
                            sibling_current_age = sibling.get('current_age') or sibling.get('age_at_death', 0)
                            # Mother's age when she died = mother's current age - years since sibling birth
                            years_since_birth = current_year - sibling_birth_year
                            mother['age_at_death'] = mother.get('age_at_death', age + fertility_min)
                            break  # Only one sibling can be the cause

        return {
            "marital_status": marital_status,
            "partner": partner,
            "ex_partner": ex_partners[0] if ex_partners else None,  # Legacy compatibility - first ex-partner
            "ex_partners": ex_partners,  # New: list of all ex-partners
            "relationship_history": relationship_history,  # Past relationships for singles
            "father": father,
            "mother": mother,
            "siblings": siblings,
            "children": children
        }

    def _generate_education(self, age: int, job: str, country: str) -> Optional[str]:
        """
        Generate education level and field coherent with age and job.

        Args:
            age: Person's age
            job: Current job
            country: Country code

        Returns:
            Education description string or None
        """
        # Load job education requirements
        job_requirements = self.loader.load_job_education_requirements()
        education_levels_list = self.loader.load_education_levels()
        # Convert to dict for easy lookups
        education_levels = {
            "none": "No formal education",
            "primary": "Primary school",
            "secondary": "Secondary education",
            "vocational": "Vocational training",
            "bachelor": "Bachelor's degree",
            "master": "Master's degree",
            "doctorate": "Doctorate/PhD"
        }

        # Special cases
        if job in ["Student", "Jobless"] or job.startswith("Student of"):
            # Students: currently studying
            # CRITICAL: "in progress" only for people under 35 (realistic)
            # CRITICAL: University students (Student of X) MUST show university-level education

            is_university_student = job.startswith("Student of ")

            if age < 22:
                # Ages 18-21: Can be university students OR high school students
                if is_university_student:
                    # University student - MUST be Bachelor's degree (in progress)
                    return "Bachelor's degree (in progress)"
                else:
                    # High school student (generic "Student")
                    return "Secondary education (in progress)"
            elif age < 26:
                # Ages 22-25: Almost certainly university or vocational
                if is_university_student:
                    # University student - Bachelor's or Master's (if older)
                    if age < 24:
                        return "Bachelor's degree (in progress)"
                    else:
                        return random.choice([
                            "Bachelor's degree (in progress)",
                            "Master's degree (in progress)"
                        ])
                else:
                    return random.choice([
                        "Bachelor's degree (in progress)",
                        "Vocational training (in progress)"
                    ])
            elif age < 35:
                # Older students - only postgraduate studies make sense
                return random.choice([
                    "Master's degree (in progress)",
                    "Bachelor's degree (in progress)"
                ])
            else:
                # Age 35+: should have COMPLETED education, not "in progress"
                # This is absurd - return completed degree instead
                return random.choice([
                    education_levels.get("bachelor", "Bachelor's degree"),
                    education_levels.get("master", "Master's degree"),
                    education_levels.get("secondary", "Secondary education")
                ])

        if job == "Retired":
            # Older generations often had less education
            # CRITICAL: In Spain, ESO mandatory since 1990, so "No formal education" only for age 55+
            if age >= 75:
                # Very likely to have little formal education
                if random.random() < 0.6:
                    return education_levels.get("none", "No formal education")
                else:
                    return education_levels.get("primary", "Primary education")
            elif age >= 65:
                if random.random() < 0.4:
                    return education_levels.get("none", "No formal education")
                elif random.random() < 0.7:
                    return education_levels.get("primary", "Primary education")
                else:
                    return education_levels.get("secondary", "Secondary education")
            elif age >= 55:
                # 55-64: can have no formal education but less common
                if random.random() < 0.15:
                    return education_levels.get("none", "No formal education")
                elif random.random() < 0.5:
                    return education_levels.get("primary", "Primary education")
                else:
                    return education_levels.get("secondary", "Secondary education")

        # Check if job has specific requirements
        if job in job_requirements:
            min_level, field, min_age_for_job = job_requirements[job]
            base_education = education_levels.get(min_level, "Secondary education")

            if field and field != "Any":
                return f"{base_education} - {field}"
            else:
                return base_education

        # For unemployed/housewife - random education that makes sense for age
        if job in ["Unemployed", "Housewife"]:
            if age >= 60:
                # Older people - less education (but "none" only if 55+)
                if age >= 55:
                    return random.choice([
                        education_levels.get("none", "No formal education"),
                        education_levels.get("primary", "Primary education"),
                        education_levels.get("secondary", "Secondary education")
                    ])
                else:
                    return random.choice([
                        education_levels.get("primary", "Primary education"),
                        education_levels.get("secondary", "Secondary education")
                    ])
            elif age >= 40:
                return random.choice([
                    education_levels.get("primary", "Primary education"),
                    education_levels.get("secondary", "Secondary education"),
                    education_levels.get("vocational", "Vocational training")
                ])
            else:
                # Younger unemployed might have degrees (can't find work)
                if random.random() < 0.3:
                    # Has degree but unemployed
                    fields = ["Business", "Arts", "Humanities", "Social Sciences", "Engineering", "IT"]
                    field = random.choice(fields)
                    return f"{education_levels.get('bachelor', 'Bachelor degree')} - {field}"
                else:
                    return random.choice([
                        education_levels.get("secondary", "Secondary education"),
                        education_levels.get("vocational", "Vocational training")
                    ])

        # Default fallback based on age
        if age < 30:
            return education_levels.get("secondary", "Secondary education")
        elif age < 50:
            return random.choice([
                education_levels.get("secondary", "Secondary education"),
                education_levels.get("vocational", "Vocational training")
            ])
        elif age >= 55:
            # Older generations - "none" only if 55+
            return random.choice([
                education_levels.get("none", "No formal education"),
                education_levels.get("primary", "Primary education"),
                education_levels.get("secondary", "Secondary education")
            ])
        else:
            # Age 50-54: ESO was already mandatory, no "none"
            return random.choice([
                education_levels.get("primary", "Primary education"),
                education_levels.get("secondary", "Secondary education")
            ])

    def _generate_languages(self, country: str, age: int, education: Optional[str], job: Optional[str], social_class: str) -> List[Dict[str, str]]:
        """
        Generate languages known by the person with levels and certifications.

        Args:
            country: Country code
            age: Person's age
            education: Education level
            job: Current job
            social_class: Social class

        Returns:
            List of language dictionaries with language, level, and certification
        """
        rules = self.loader.load_rules(country)
        certifications = self.loader.load_language_certifications()

        # Get language configuration from rules
        min_langs = rules.min_languages if hasattr(rules, 'min_languages') else 1
        max_langs = rules.max_languages if hasattr(rules, 'max_languages') else 4
        available_languages = rules.available_languages if hasattr(rules, 'available_languages') else {"English": 70}

        # Get level probabilities from rules
        prob_basic = rules.language_level_basic if hasattr(rules, 'language_level_basic') else 30
        prob_intermediate = rules.language_level_intermediate if hasattr(rules, 'language_level_intermediate') else 50
        prob_advanced = rules.language_level_advanced if hasattr(rules, 'language_level_advanced') else 20

        languages = []

        # Always add native language
        country_languages = {
            "spain": "Spanish",
            "russia": "Russian",
            "thailand": "Thai",
            "china": "Chinese",
            "japan": "Japanese",
            "greece": "Greek",
            "vietnam": "Vietnamese"
        }
        native_lang = country_languages.get(country.lower(), "Native")
        languages.append({
            "language": native_lang,
            "level": "Native",
            "certification": "Native speaker"
        })

        # Jobs that REQUIRE multiple languages
        language_intensive_jobs = [
            "Flight Attendant", "Tour Guide", "Hotel Receptionist", "Translator", "Interpreter",
            "Customer Service Representative", "Travel Agent", "Cruise Ship Staff",
            "International Sales", "Marketing Manager", "Export Manager", "Diplomat"
        ]

        # Education level significantly affects language learning
        education_lower = (education or "").lower()

        # People with very low education rarely speak other languages well
        # UNLESS they're young (under 30) - even poor kids learn English at school
        if "incomplete" in education_lower or "no formal education" in education_lower:
            if age < 30:
                # Young people - basic English is common even with low education
                num_additional = 1 if random.random() < 0.4 else 0
            else:
                # Older with no education - very rare to know languages
                if random.random() > 0.98:  # Only 2% chance
                    num_additional = 1 if random.random() < 0.3 else 0
                else:
                    return languages  # Return only native language
        elif "primary" in education_lower and "incomplete" not in education_lower:
            # Primary education
            if age < 30:
                # Young - ALWAYS knows at least basic English (taught in schools)
                num_additional = 1
            else:
                # Older - less likely
                num_additional = 1 if random.random() < 0.2 else 0
        else:
            # Jobs that require languages - MUST have multiple
            if job and job in language_intensive_jobs:
                num_additional = random.randint(2, 3)  # Minimum 2 additional languages
            else:
                # Decide how many additional languages
                # Probability decreases for each additional language
                num_additional = 0

                # Young people (<30) with secondary or higher education ALWAYS know English
                if age < 30:
                    num_additional = 1  # At least English

                for i in range(max_langs - 1 - num_additional):  # -1 for native, -num_additional for already assigned
                    # Base probability - YOUNG PEOPLE MUCH MORE LIKELY
                    if age < 25:
                        prob = 80 / (2 ** (i + num_additional))  # 80%, 40%, 20%
                    elif age < 35:
                        prob = 70 / (2 ** (i + num_additional))  # 70%, 35%, 17.5%
                    else:
                        prob = 60 / (2 ** (i + num_additional))  # 60%, 30%, 15%

                    # Older people less likely to know multiple languages
                    if age >= 60:
                        prob *= 0.4
                    elif age >= 45:
                        prob *= 0.6

                    # Higher education increases probability
                    if education and ("Bachelor" in education or "Master" in education or "Doctorate" in education):
                        prob *= 1.4

                    # Low social class reduces probability (less opportunity)
                    if social_class == "low":
                        prob *= 0.7

                    if random.random() * 100 < prob:
                        num_additional += 1
                    else:
                        break

        # Select additional languages
        selected_langs = []
        if num_additional > 0:
            # For young people or language-intensive jobs, English is almost mandatory
            if (age < 30 or (job and job in language_intensive_jobs)) and "English" in available_languages:
                selected_langs.append("English")
                num_additional -= 1

            if num_additional > 0:
                # Weight by probability from available_languages
                lang_choices = []
                lang_weights = []
                for lang, weight in available_languages.items():
                    if lang not in selected_langs:  # Don't add English again
                        lang_choices.append(lang)
                        lang_weights.append(weight)

                # Normalize weights
                if lang_weights:
                    total_weight = sum(lang_weights)
                    lang_weights = [w / total_weight for w in lang_weights]

                    # Select languages without replacement
                    for _ in range(min(num_additional, len(lang_choices))):
                        lang = random.choices(lang_choices, weights=lang_weights, k=1)[0]
                        selected_langs.append(lang)
                        # Remove selected language
                        idx = lang_choices.index(lang)
                        lang_choices.pop(idx)
                        lang_weights.pop(idx)
                        # Renormalize
                        if lang_weights:
                            total_weight = sum(lang_weights)
                            lang_weights = [w / total_weight for w in lang_weights]

        # SPECIAL CASE: Students with university degrees MUST have B1+ English (intermediate or advanced)
        university_degrees = ["Bachelor", "Master", "Doctorate", "PhD"]
        has_university_degree = education and any(degree in education for degree in university_degrees)

        # Add each selected language with level and certification
        if selected_langs:  # Only if we have selected languages
            for lang in selected_langs:
                # Determine level based on probabilities and education
                # Low education = only basic level possible
                if "incomplete" in education_lower or "no formal education" in education_lower:
                    level = "basic"
                elif "primary" in education_lower:
                    # Primary education - max basic level
                    level = "basic"
                elif "secondary" in education_lower or "high school" in education_lower:
                    # Secondary - basic or intermediate
                    level = "basic" if random.random() < 0.6 else "intermediate"
                else:
                    # Higher education - follow probabilities
                    rand_val = random.randint(1, 100)
                    if rand_val <= prob_basic:
                        level = "basic"
                    elif rand_val <= prob_basic + prob_intermediate:
                        level = "intermediate"
                    else:
                        level = "advanced"

                # OVERRIDE: University degree holders MUST have at least intermediate English
                if has_university_degree and lang == "English" and level == "basic":
                    # Force intermediate or advanced (70% intermediate, 30% advanced)
                    level = "intermediate" if random.random() < 0.7 else "advanced"

                # Get certification (or None if no certification)
                cert_key = f"{lang}:{level}"
                possible_certs = certifications.get(cert_key, ["None"])

                # 60% chance to have a certification if available
                if random.random() < 0.6 and len(possible_certs) > 1:
                    # Choose from non-None certifications
                    non_none = [c for c in possible_certs if c != "None"]
                    if non_none:
                        certification = random.choice(non_none)
                    else:
                        certification = "None"
                else:
                    certification = "None"

                languages.append({
                    "language": lang,
                    "level": level.capitalize(),
                    "certification": certification
                })

        return languages

    def _get_coherent_previous_job(self, current_job: str, all_jobs: List[str]) -> Optional[str]:
        """
        Select a coherent previous job based on job category transitions.
        Ensures career progression makes sense (e.g., lawyer wasn't a construction worker).

        Args:
            current_job: Current job title
            all_jobs: List of all available jobs

        Returns:
            A coherent previous job or None
        """
        import json
        from pathlib import Path

        # Load job transitions data
        transitions_file = self.loader.data_dir / "global" / "job_transitions.json"
        if not transitions_file.exists():
            return random.choice(all_jobs) if all_jobs else None

        try:
            with open(transitions_file, 'r', encoding='utf-8') as f:
                transitions_data = json.load(f)

            job_categories = transitions_data.get("job_categories", {})
            incompatible = transitions_data.get("incompatible_transitions", [])

            # Find current job's category
            current_category = None
            for category, jobs in job_categories.items():
                if current_job in jobs:
                    current_category = category
                    break

            if not current_category:
                # Job not categorized - return random job
                return random.choice(all_jobs) if all_jobs else None

            # Filter out incompatible jobs
            compatible_jobs = []
            for prev_job in all_jobs:
                if prev_job == current_job:
                    continue  # Skip same job

                # Check if this transition is explicitly incompatible
                is_incompatible = False
                for incompatible_pair in incompatible:
                    if (current_job in incompatible_pair and prev_job in incompatible_pair):
                        is_incompatible = True
                        break

                if not is_incompatible:
                    compatible_jobs.append(prev_job)

            if not compatible_jobs:
                compatible_jobs = [j for j in all_jobs if j != current_job]

            # Prefer jobs from same category (70% chance)
            same_category_jobs = [j for j in compatible_jobs if j in job_categories.get(current_category, [])]

            if same_category_jobs and random.random() < 0.70:
                return random.choice(same_category_jobs)
            else:
                return random.choice(compatible_jobs) if compatible_jobs else None

        except Exception as e:
            # If anything fails, fall back to random selection
            return random.choice(all_jobs) if all_jobs else None

    def _generate_work_experience(
        self,
        age: int,
        job: str,
        previous_job: Optional[str],
        country: str,
        date_format: str,
        gender: str = "male",
        social_class: str = "middle"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate work experience including dates at current job and previous positions.
        Ensures job coherence - previous jobs are related to current career.

        Args:
            age: Person's age
            job: Current job
            previous_job: Previous job (if any)
            country: Country code
            date_format: Date format string
            gender: Person's gender (for job selection)
            social_class: Person's social class (for job selection)

        Returns:
            Work experience dictionary or None
        """
        from datetime import datetime, timedelta
        import re

        job_requirements = self.loader.load_job_education_requirements()
        termination_reasons = self.loader.load_termination_reasons()

        # Helper function to format date
        def format_date(year, month):
            """Format date according to country format."""
            if date_format == "DD/MM/YYYY":
                return f"01/{month:02d}/{year}"
            elif date_format == "DD.MM.YYYY":
                return f"01.{month:02d}.{year}"
            elif date_format == "MM/DD/YYYY":
                return f"{month:02d}/01/{year}"
            else:
                return f"01/{month:02d}/{year}"  # default

        # Current year
        current_year = datetime.now().year

        # Special cases - no work experience
        if job in ["Student", "Jobless"] or job.startswith("Student of"):
            # Students may have internships
            if age >= 20 and random.random() < 0.4:
                # Has internship experience
                internship_duration = random.randint(3, 6)  # months
                internship_fields = ["Marketing", "IT", "Administration", "Sales", "Customer Service", "Design"]
                internship_field = random.choice(internship_fields)

                # Calculate internship dates (ended recently, lasted 3-6 months)
                end_year = current_year - random.randint(0, 1)
                end_month = random.randint(1, 12)
                start_year = end_year if internship_duration < 12 else end_year - 1
                start_month = end_month - internship_duration
                if start_month <= 0:
                    start_month += 12
                    start_year -= 1

                # CRITICAL: Ensure internship didn't start when person was a minor
                birth_year = current_year - age
                min_internship_age = 18  # Internships typically 18+
                earliest_possible_start = birth_year + min_internship_age

                if start_year < earliest_possible_start:
                    # Adjust start year to when person turned 18
                    start_year = earliest_possible_start
                    start_month = random.randint(1, 12)
                    # Adjust end date to maintain reasonable duration
                    end_year = start_year
                    end_month = start_month + internship_duration
                    if end_month > 12:
                        end_month -= 12
                        end_year += 1

                return {
                    "current_job": None,
                    "start_date": None,
                    "previous_positions": [{
                        "job": f"Intern - {internship_field}",
                        "start_date": format_date(start_year, start_month),
                        "end_date": format_date(end_year, end_month),
                        "termination_reason": random.choice([
                            "Internship program completed",
                            "Returned to studies",
                            "End of internship"
                        ])
                    }]
                }
            return None

        if job == "Housewife":
            # May have worked before
            if random.random() < 0.3:
                prev_jobs_list = ["Cashier", "Sales Associate", "Waitress", "Receptionist", "Cleaner"]
                prev_job_title = random.choice(prev_jobs_list)
                years_worked = random.randint(2, 8)

                # Calculate dates (stopped working years ago)
                end_year = current_year - random.randint(5, 15)
                end_month = random.randint(1, 12)
                start_year = end_year - years_worked
                start_month = random.randint(1, 12)

                # CRITICAL: Ensure job didn't start when person was a minor
                birth_year = current_year - age
                min_working_age = 16  # Basic jobs can start at 16
                earliest_possible_start = birth_year + min_working_age

                if start_year < earliest_possible_start:
                    # Adjust start year to when person turned 16
                    start_year = earliest_possible_start
                    start_month = random.randint(1, 12)
                    # Recalculate years worked
                    years_worked = end_year - start_year
                    if years_worked < 1:
                        # If duration too short, skip previous job
                        return None

                return {
                    "current_job": None,
                    "start_date": None,
                    "previous_positions": [{
                        "job": prev_job_title,
                        "start_date": format_date(start_year, start_month),
                        "end_date": format_date(end_year, end_month),
                        "termination_reason": random.choice([
                            "Family reasons",
                            "Started family",
                            "Personal choice"
                        ])
                    }]
                }
            return None

        # Calculate years at current job
        years_at_current = None

        if job == "Retired":
            # Show when retired
            retirement_age = random.randint(63, 67)
            years_since_retirement = age - retirement_age

            # What job they retired from
            retired_from = previous_job if previous_job else "Various positions"
            years_before_retirement = random.randint(15, 40)

            # Calculate retirement date
            retirement_year = current_year - years_since_retirement
            retirement_month = random.randint(1, 12)

            # Calculate start date of previous job
            prev_start_year = retirement_year - years_before_retirement
            prev_start_month = random.randint(1, 12)

            # CRITICAL: Ensure job didn't start when person was a minor
            birth_year = current_year - age
            min_working_age = 18  # Most careers start at 18+
            earliest_possible_start = birth_year + min_working_age

            if prev_start_year < earliest_possible_start:
                # Adjust start year to when person turned 18
                prev_start_year = earliest_possible_start
                prev_start_month = random.randint(1, 12)
                # Recalculate years worked
                years_before_retirement = retirement_year - prev_start_year

            return {
                "current_job": "Retired",
                "start_date": format_date(retirement_year, retirement_month),
                "retirement_age": retirement_age,
                "previous_positions": [{
                    "job": retired_from,
                    "start_date": format_date(prev_start_year, prev_start_month),
                    "end_date": format_date(retirement_year, retirement_month),
                    "termination_reason": "Retirement"
                }]
            }

        if job == "Unemployed":
            # How long unemployed
            months_unemployed = random.randint(3, 18)

            # Previous job
            prev_job_title = previous_job if previous_job else "Various positions"
            years_at_prev = random.randint(2, 12)

            # Choose appropriate termination reason
            # For unemployed, NEVER use voluntary reasons like "better opportunity"
            termination_categories = {
                "economic": ["Economic crisis layoff", "Position eliminated", "Cost-cutting measures", "Business downturn"],
                "company": ["Company restructuring", "Company closure", "Department elimination", "Contract ended"],
                "personal": ["Health reasons", "Family relocation", "Personal circumstances"]
            }

            # More likely to be economic/company reasons (NOT voluntary for unemployed)
            category = random.choices(
                ["economic", "company", "personal"],
                weights=[55, 35, 10]
            )[0]
            reason = random.choice(termination_categories[category])

            # Calculate dates
            years_ago_lost_job = months_unemployed / 12
            end_year = int(current_year - years_ago_lost_job)
            end_month = random.randint(1, 12)
            start_year = end_year - years_at_prev
            start_month = random.randint(1, 12)

            return {
                "current_job": "Unemployed",
                "start_date": None,
                "months_unemployed": months_unemployed,
                "previous_positions": [{
                    "job": prev_job_title,
                    "start_date": format_date(start_year, start_month),
                    "end_date": format_date(end_year, end_month),
                    "termination_reason": reason
                }]
            }

        # Handle Jobless, Housewife, Student - no work experience
        if job in ["Jobless", "Housewife"] or job.startswith("Student"):
            return {
                "current_job": job,
                "start_date": None,
                "previous_positions": None
            }

        # For currently employed
        # Get minimum age requirement for job
        age_requirements_file = self.loader.data_dir / "global" / "jobs" / "age_requirements.txt"
        min_job_age = 18  # default

        if age_requirements_file.exists():
            for line in self.loader.load_lines(age_requirements_file):
                if ':' in line:
                    job_title, min_age_str = line.split(':', 1)
                    if job_title.strip() == job:
                        min_job_age = int(min_age_str.strip())
                        break

        # Calculate realistic years at current job
        max_possible_years = age - min_job_age

        # CRITICAL: If person is too young for this job, they shouldn't have it
        # This is a data consistency issue - job assignment should respect min_job_age
        if max_possible_years < 0:
            # Person is too young for this job - assign 0 years (just started)
            years_at_current = 0
            # Ensure start date is very recent (within last 3 months)
            current_start_year = current_year
            current_start_month = max(1, datetime.now().month - random.randint(0, 2))
        elif max_possible_years == 0:
            # Just became old enough for this job
            years_at_current = 0
            current_start_year = current_year
            current_start_month = random.randint(1, 12)
        elif max_possible_years <= 3:
            years_at_current = random.randint(0, max_possible_years)
            current_start_year = current_year - years_at_current
            current_start_month = random.randint(1, 12)
        else:
            # Most people don't stay in one job for entire career
            # Use exponential decay for probability
            max_realistic = min(max_possible_years, 25)
            years_at_current = random.randint(0, max_realistic)

            # Weight towards shorter durations (most people change jobs)
            if years_at_current > 10:
                if random.random() < 0.7:  # 70% chance to reduce
                    years_at_current = random.randint(2, 10)

            # Calculate current job start date
            current_start_year = current_year - years_at_current
            current_start_month = random.randint(1, 12)

        # Safety check: ensure start date is not in the future
        if current_start_year > current_year:
            current_start_year = current_year
            current_start_month = random.randint(1, datetime.now().month)

        # CRITICAL: Final safety check - ensure person was old enough when current job started
        birth_year = current_year - age
        earliest_possible_start = birth_year + min_job_age
        if current_start_year < earliest_possible_start:
            # Adjust to minimum allowed start year
            current_start_year = earliest_possible_start
            current_start_month = random.randint(1, 12)
            # Recalculate years at current job
            years_at_current = current_year - current_start_year

        # Generate previous positions
        previous_positions = []

        # CRITICAL: Ensure person didn't start working TOO LATE in life
        # Calculate how old they were when starting current job
        age_when_started_current = age - years_at_current

        # If they started current job after age 25 AND have no previous_job, it's unrealistic
        # EXCEPTION: Special careers that start late (doctors at 28, professors at 30, etc.)
        late_start_acceptable = min_job_age >= 24  # Jobs requiring advanced degrees

        if age_when_started_current > 25 and not previous_job and not late_start_acceptable:
            # Generate a previous job to fill the gap
            # They should have started working around age 20-25
            realistic_career_start_age = random.randint(20, 25)
            years_at_prev = age_when_started_current - realistic_career_start_age
            years_at_prev = max(1, min(years_at_prev, 15))  # Cap at 15 years

            # Get a coherent job for previous employment (same category or related field)
            all_jobs = self.loader.load_jobs(gender, social_class)
            available_prev_jobs = [j for j in all_jobs if j != job]
            if available_prev_jobs:
                # Use coherent job selection based on current job category
                previous_job = self._get_coherent_previous_job(job, available_prev_jobs)

        # If has previous_job, generate its history
        if previous_job and years_at_current >= 0:
            years_at_prev = random.randint(2, 12)

            # If person is older (40+), they likely had longer career at previous job
            if age >= 40:
                years_at_prev = random.randint(5, 15)

            # CRITICAL: Select termination reason appropriate for job level
            # Filter out inappropriate reasons based on previous job seniority
            executive_jobs = ["CEO", "CFO", "CTO", "COO", "CMO", "Managing Director", "Executive Director",
                            "Vice President", "Company Director", "General Manager", "Senior Manager"]
            professional_jobs = ["Doctor", "Surgeon", "Lawyer", "Judge", "University Professor",
                               "Architect", "Engineer"]
            entry_level_student_jobs = ["Intern", "Trainee", "Student"]
            seasonal_jobs = ["Seasonal Worker", "Farm Worker", "Beach Lifeguard"]

            inappropriate_reasons = []
            if previous_job in executive_jobs or previous_job in professional_jobs:
                # Executives/professionals: never internship, seasonal, or student reasons
                inappropriate_reasons = ["internship", "seasonal", "graduated", "student", "trainee"]
            elif previous_job not in entry_level_student_jobs:
                # Regular jobs: never internship/student reasons
                inappropriate_reasons = ["internship", "graduated", "student", "trainee"]

            if previous_job not in seasonal_jobs:
                # Non-seasonal jobs: never "seasonal work ended"
                if "seasonal" not in inappropriate_reasons:
                    inappropriate_reasons.append("seasonal")

            # Filter termination reasons
            appropriate_reasons = [
                r for r in termination_reasons
                if "retirement" not in r.lower() and
                not any(term in r.lower() for term in inappropriate_reasons)
            ]

            # If all filtered out (shouldn't happen), use safe fallback
            if not appropriate_reasons:
                appropriate_reasons = ["Better job opportunity", "Company restructuring", "Career change"]

            reason = random.choice(appropriate_reasons)

            # Previous job ended when current started
            prev_end_year = current_start_year
            prev_end_month = current_start_month
            prev_start_year = prev_end_year - years_at_prev
            prev_start_month = random.randint(1, 12)

            # CRITICAL: Ensure prev_start_year isn't before person turned min_job_age
            # Calculate birth year and earliest possible work start
            birth_year = current_year - age
            min_working_age = 18  # Legal working age in Spain for most jobs
            earliest_possible_start = birth_year + min_working_age

            if prev_start_year < earliest_possible_start:
                prev_start_year = earliest_possible_start
                # Recalculate years_at_prev to match the corrected start year
                years_at_prev = prev_end_year - prev_start_year
                if years_at_prev < 1:
                    # If this makes duration too short, skip previous job entirely
                    previous_positions = []
                    return {
                        "current_job": job,
                        "start_date": format_date(current_start_year, current_start_month),
                        "previous_positions": None
                    }
                prev_start_month = random.randint(1, 12)

            previous_positions.append({
                "job": previous_job,
                "start_date": format_date(prev_start_year, prev_start_month),
                "end_date": format_date(prev_end_year, prev_end_month),
                "termination_reason": reason
            })

        return {
            "current_job": job,
            "start_date": format_date(current_start_year, current_start_month),
            "previous_positions": previous_positions if previous_positions else None
        }

    def generate(
        self,
        country: str = "spain",
        gender: Optional[str] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        website: str = ""
    ) -> Identity:
        """
        Generate a single synthetic identity.

        Args:
            country: Country code (default: "spain")
            gender: "male" or "female" (random if None)
            min_age: Minimum age (uses country rules if None)
            max_age: Maximum age (uses country rules if None)
            website: Website this identity is for

        Returns:
            Complete Identity object
        """
        # Load rules
        rules = self.loader.load_rules(country)

        # Use country-specific age ranges if not provided
        if min_age is None:
            min_age = rules.get_min_age()
        if max_age is None:
            max_age = rules.get_max_age()

        # Select gender
        if gender is None:
            gender = random.choice(['male', 'female'])

        # Generate DOB and age first
        date_format = rules.get_date_format()
        dob, age = self._generate_dob(date_format, min_age, max_age)
        first_name = self.loader.load_name_by_age(country, gender, age)

        # Load data (pass gender for gendered surnames)
        surnames = self.loader.load_surnames(country, gender)
        city_lines = self.loader.load_cities(country)

        # Select social class based on country probabilities
        social_classes = rules.get_social_classes()
        social_class = self._weighted_choice(social_classes)

        # Load jobs based on social class
        jobs = self.loader.load_jobs(gender, social_class)

        # Determine age bucket for hobby logic using country rules
        min_age = rules.get_min_age()
        life_expectancy = rules.get_life_expectancy()
        if age < min_age + 5:
            hobby_bucket = "very_young"
        elif min_age + 5 <= age < min_age + 16:
            hobby_bucket = "young_adults"
        elif min_age + 16 <= age < 50:
            hobby_bucket = "adults"
        elif 50 <= age < 65:
            hobby_bucket = "older_adults"
        elif 65 <= age <= life_expectancy:
            hobby_bucket = "elderly"
        else:
            hobby_bucket = "elderly"

        selected_hobbies = []

        # Load different hobby categories
        age_appropriate_hobbies, country_hobbies = self.loader._get_hobbies_for_age_and_gender(gender, age, country)
        class_hobbies = self.loader.load_class_hobbies(social_class)
        neutral_hobbies = []
        if hobby_bucket in ["very_young", "young_adults", "adults"]:
            neutral_path = self.loader.data_dir / "global" / "hobbies" / "hobbies_neutral.txt"
            if neutral_path.exists():
                neutral_hobbies = self.loader.load_lines(neutral_path)

        # 1. Add 2 national hobbies (guaranteed if available)
        if country_hobbies and len(country_hobbies) >= 2:
            selected_hobbies.extend(random.sample(country_hobbies, 2))
        elif country_hobbies:
            selected_hobbies.extend(country_hobbies)

        # 2. Add 1 class-based hobby (if available and not already selected, and only for <= adults)
        if hobby_bucket in ["very_young", "young_adults", "adults"] and class_hobbies:
            available_class = [h for h in class_hobbies if h not in selected_hobbies]
            if available_class:
                selected_hobbies.append(random.choice(available_class))

        # 3. Add 1 gender-based hobby (if available and not already selected)
        if age_appropriate_hobbies:
            available_gender = [h for h in age_appropriate_hobbies if h not in selected_hobbies and h not in country_hobbies]
            if available_gender:
                selected_hobbies.append(random.choice(available_gender))

        # 4. Add 1 neutral hobby (if available and not already selected, and only for allowed buckets)
        if neutral_hobbies:
            available_neutral = [h for h in neutral_hobbies if h not in selected_hobbies]
            if available_neutral:
                selected_hobbies.append(random.choice(available_neutral))

        # For seniors, elderly and older_adults: ensure 3-4 hobbies total
        if hobby_bucket in ["older_adults", "seniors", "elderly"]:
            # Combine all available age-appropriate and country hobbies
            all_available = age_appropriate_hobbies + country_hobbies
            remaining = [h for h in all_available if h not in selected_hobbies]

            # Target 3-4 hobbies for these age groups
            target_hobbies = random.randint(3, 4)
            num_to_add = target_hobbies - len(selected_hobbies)

            if num_to_add > 0 and remaining:
                num_to_add = min(num_to_add, len(remaining))
                selected_hobbies.extend(random.sample(remaining, num_to_add))
        # Para los demás, la lógica ya permite hasta 5 hobbies
        elif len(selected_hobbies) < 2:
            # Fill up to 2 with any available hobbies (pero nunca neutrales para mayores)
            all_hobbies = list(set(age_appropriate_hobbies + class_hobbies))
            if hobby_bucket in ["very_young", "young_adults", "adults"]:
                all_hobbies += neutral_hobbies
            available = [h for h in all_hobbies if h not in selected_hobbies]
            if available:
                num_to_add = min(2 - len(selected_hobbies), len(available))
                selected_hobbies.extend(random.sample(available, num_to_add))
        elif len(selected_hobbies) > 5:
            # Trim to 5
            selected_hobbies = selected_hobbies[:5]

        # Select surnames based on rules
        surname_count = rules.get_surname_count()
        selected_surnames = []

        for i in range(surname_count):
            surname = random.choice(surnames)
            # Ensure it's different from already selected surnames
            while surname in selected_surnames:
                surname = random.choice(surnames)
            selected_surnames.append(surname)

        # Build name components
        name_components = {'first': first_name}
        for i, surname in enumerate(selected_surnames, 1):
            name_components[f'surname{i}'] = surname

        # Build full name according to rules
        name_order = rules.get_name_order()
        full_name = self._build_full_name(name_components, name_order, country=country, gender=gender)

        # Generate physical characteristics
        height_cm, weight_kg, hair_color, eye_color, skin_tone = self._generate_physical_characteristics(
            country, gender, age, rules
        )

        # Select city with postal code
        city_line = random.choice(city_lines)
        city, nearby_town, postal_code = self._parse_city_line(city_line)

        # Generate religion (older adults/elderly are much more religious)
        religions = rules.get_religions()
        if age >= 50:
            # Older adults (50+) and elderly (65+) are much more likely to be religious
            # Find the most common religion in the country
            most_common_religion = max(religions.items(), key=lambda x: x[1])[0]

            # 90% chance of being the most common religion for elderly (65+)
            # 70% chance for older adults (50-64)
            if age >= 65:
                religious_probability = 0.90
            else:  # 50-64
                religious_probability = 0.70

            if random.random() < religious_probability:
                religion = most_common_religion
            else:
                religion = self._weighted_choice(religions)
        else:
            # Younger people follow normal distribution
            religion = self._weighted_choice(religions)

        # Generate family information first to determine marital status and children for job generation
        family = self._generate_family(country, age, gender, selected_surnames, rules, social_class)

        # Get age bucket for job generation (use country rules for min_age/life_expectancy)
        min_age = rules.get_min_age()
        life_expectancy = rules.get_life_expectancy()
        if age < min_age + 5:
            age_bucket = "very_young"
        elif min_age + 5 <= age < min_age + 16:
            age_bucket = "young_adults"
        elif min_age + 16 <= age < 50:
            age_bucket = "adults"
        elif 50 <= age < 65:
            age_bucket = "older_adults"
        elif 65 <= age <= life_expectancy:
            age_bucket = "elderly"
        else:
            age_bucket = "elderly"

        # Determine if person has children for job generation
        has_children = family.get("children") is not None and len(family.get("children", [])) > 0
        marital_status = family.get("marital_status", "Single")

        # Select job based on age, gender, family status (returns tuple: current_job, previous_job)
        job, previous_job = self._get_job_for_age(age, jobs, rules, gender, age_bucket, country, marital_status, has_children)

        # Generate phone
        phone = self._generate_phone(rules)

        # Generate email (with transliteration for non-Latin scripts)
        email = self._generate_fake_email(first_name, selected_surnames, dob, country)

        # Load cultural considerations
        considerations = self.loader.load_considerations(country)

        # Generate salary/pension and previous_salary based on employment status
        salary = None
        previous_salary = None

        if job == "Retired":
            # Retired: generate pension based on social class
            min_pension, max_pension = rules.get_pension_range(social_class)
            base_pension = random.randint(min_pension, max_pension)

            # Round pension to nearest 50 or 100
            if base_pension < 30000:
                salary = round(base_pension / 50) * 50  # salary field holds pension
            else:
                salary = round(base_pension / 100) * 100

            # Also generate what they earned before retiring
            min_prev_salary, max_prev_salary = rules.get_salary_range(social_class)
            base_prev = random.randint(min_prev_salary, max_prev_salary)
            if base_prev < 30000:
                previous_salary = round(base_prev / 50) * 50
            else:
                previous_salary = round(base_prev / 100) * 100

        elif job == "Unemployed":
            # Unemployed: generate what they used to earn
            min_prev_salary, max_prev_salary = rules.get_salary_range(social_class)
            base_prev = random.randint(min_prev_salary, max_prev_salary)
            if base_prev < 30000:
                previous_salary = round(base_prev / 50) * 50
            else:
                previous_salary = round(base_prev / 100) * 100

        elif job and job not in ["Student", "Housewife", "Jobless"] and not job.startswith("Student of"):
            # Currently employed: generate current salary
            min_salary, max_salary = rules.get_salary_range(social_class)
            base_salary = random.randint(min_salary, max_salary)

            # Apply age-based salary adjustment (younger workers earn less)
            if age < 25:
                # Very young workers: 50-70% of base range
                base_salary = int(base_salary * random.uniform(0.50, 0.70))
            elif age < 30:
                # Young workers: 65-85% of base range
                base_salary = int(base_salary * random.uniform(0.65, 0.85))
            elif age < 40:
                # Young-mid career: 80-100% of base range
                base_salary = int(base_salary * random.uniform(0.80, 1.00))
            # Ages 40+ get full range (no adjustment)

            # Round to nearest 50 or 100
            if base_salary < 30000:
                salary = round(base_salary / 50) * 50
            else:
                salary = round(base_salary / 100) * 100

        # Generate education, languages, and work experience
        # For retired/unemployed, use previous_job to determine education
        job_for_education = previous_job if job in ["Retired", "Unemployed"] and previous_job else job
        education = self._generate_education(age, job_for_education, country)
        languages = self._generate_languages(country, age, education, job_for_education, social_class)
        work_experience = self._generate_work_experience(age, job, previous_job, country, date_format, gender, social_class)

        # Generate regional characteristics
        regional_characteristics = self.loader.load_regional_characteristics(country, age, gender)

        # Create identity
        identity = Identity(
            country=country,
            gender=gender,
            first_name=first_name,
            surnames=selected_surnames,
            full_name=full_name,
            date_of_birth=dob,
            age=age,
            city=city,
            nearby_town=nearby_town,
            postal_code=postal_code,
            job=job,
            previous_job=previous_job,
            social_class=social_class,
            salary=salary,
            previous_salary=previous_salary,
            hobbies=selected_hobbies,
            phone=phone,
            height_cm=height_cm,
            weight_kg=weight_kg,
            hair_color=hair_color,
            eye_color=eye_color,
            skin_tone=skin_tone,
            email=email,
            website=website,
            religion=religion,
            family=family,
            considerations=considerations,
            education=education,
            languages=languages,
            work_experience=work_experience,
            regional_characteristics=regional_characteristics
        )

        return identity

    def generate_identity(self, country: str, gender: str, min_age: int = 18, max_age: int = 80, **kwargs) -> Identity:
        """
        Generate a single synthetic identity.

        Args:
            country: Country code
            gender: "male" or "female"
            rules: CountryRules object
            min_age: Minimum age
            max_age: Maximum age

        Returns:
            Complete Identity object
        """
        rules = self.loader.load_rules(country)
        dob, age = self._generate_dob(rules.get_date_format(), min_age, max_age)
        # Use new logic for Spain, fallback to old for others
        if country.lower() == "spain":
            first_name = self.loader.load_name_by_age(country, gender, age)
        else:
            first_name = random.choice(self.loader.load_names(country, gender))
        # ...existing code...

def get_inbox_url(email: str) -> str:
    """
    Get the inbox URL for a fake email address.

    Args:
        email: The fake email address

    Returns:
        URL to access the email inbox
    """
    local_part = email.split('@')[0]
    domain = email.split('@')[1]
    return f"https://www.fakemailgenerator.com/#/{domain}/{local_part}/"