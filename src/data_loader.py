#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data loading module for the Synthetic Identity Generator.
Handles loading and caching of all data files.
"""

import random
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from models import CountryRules
from config import DATA_DIR


class DataLoader:
    """
    Loads data files from disk with caching.

    Handles loading of names, surnames, cities, jobs, hobbies,
    and physical characteristics from the data directory.
    """

    # Age buckets in order from youngest to oldest
    _AGE_BUCKETS = [
        "very_young",
        "young_adults",
        "adults",
        "middle_aged",
        "older_adults",
        "seniors",
        "elderly"
    ]

    def __init__(self, data_dir: Path = None):
        """
        Initialize DataLoader.

        Args:
            data_dir: Path to data directory (defaults to DATA_DIR from config)
        """
        self.data_dir = data_dir if data_dir else DATA_DIR
        self._cache = {}

    def load_considerations(self, country: str) -> str:
        """
        Load cultural considerations for a country.

        Args:
            country: Country code

        Returns:
            Full text content of considerations file, or empty string if not found
        """
        filepath = self.data_dir / "countries" / country / "considerations.txt"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def load_lines(self, filepath: Path) -> List[str]:
        """
        Load lines from a text file, skipping empty lines and comments.

        Args:
            filepath: Path to file

        Returns:
            List of non-empty, non-comment lines
        """
        cache_key = str(filepath)
        if cache_key not in self._cache:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith('#')
                ]
                self._cache[cache_key] = lines
        return self._cache[cache_key]

    def load_rules(self, country: str) -> CountryRules:
        """Load country-specific rules."""
        filepath = self.data_dir / "countries" / country / "rules.txt"
        return CountryRules(filepath)

    def load_names(self, country: str, gender: str, age: int = None) -> List[str]:
        """Load first names for a specific country, gender, and (optionally) age bucket."""
        if age is None:
            # fallback: load all names from all buckets
            names = []
            buckets = ["very_young", "young_adults", "adults", "older_adults", "seniors", "elderly"]
            for bucket in buckets:
                path = self.data_dir / "countries" / country / "names" / gender / f"{bucket}.txt"
                if path.exists():
                    names.extend(self.load_lines(path))
            return names
        # Select bucket based on age
        if age >= 18 and age <= 22:
            bucket = "very_young"
        elif age > 22 and age <= 34:
            bucket = "young_adults"
        elif age > 34 and age < 50:
            bucket = "adults"
        elif age >= 50 and age < 65:
            bucket = "older_adults"
        elif age >= 65 and age < 80:
            bucket = "seniors"
        else:
            bucket = "elderly"
        path = self.data_dir / "countries" / country / "names" / gender / f"{bucket}.txt"
        return self.load_lines(path)

    def load_surnames(self, country: str, gender: str = None) -> List[str]:
        """
        Load surnames for a specific country.

        For countries with gendered surnames (gendered_surnames=true in rules.txt),
        loads from surnames/males.txt or surnames/females.txt based on gender.
        Otherwise loads from surnames.txt.

        Args:
            country: Country code
            gender: 'male' or 'female' (required for gendered surnames)

        Returns:
            List of surnames appropriate for the gender
        """
        # Check if country uses gendered surnames
        rules_file = self.data_dir / "countries" / country / "rules.txt"
        gendered_surnames = False
        if rules_file.exists():
            with open(rules_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('gendered_surnames='):
                        value = line.split('=')[1].strip().lower()
                        gendered_surnames = (value == 'true')
                        break

        if gendered_surnames and gender:
            # Load gender-specific surnames
            filepath = self.data_dir / "countries" / country / "surnames" / f"{gender}s.txt"
            if filepath.exists():
                return self.load_lines(filepath)
            # Fallback to surnames.txt if gender-specific file doesn't exist
            filepath = self.data_dir / "countries" / country / "surnames.txt"
            return self.load_lines(filepath)
        else:
            # Load standard surnames.txt
            filepath = self.data_dir / "countries" / country / "surnames.txt"
            return self.load_lines(filepath)

    def load_cities(self, country: str) -> List[str]:
        """Load cities for a specific country."""
        filepath = self.data_dir / "countries" / country / "cities.txt"
        return self.load_lines(filepath)

    def load_jobs(self, gender: Optional[str] = None, social_class: Optional[str] = None) -> List[str]:
        """
        Load jobs list based on gender and social class.

        Combines neutral jobs with gender-specific jobs for the given social class.

        Args:
            gender: 'male' or 'female' (includes only neutral if None)
            social_class: 'low', 'middle', 'upper-middle', 'high' (if None, loads from old structure)

        Returns:
            List of job titles
        """
        jobs = []

        if social_class:
            # New class-based structure
            # Load neutral jobs for this class
            neutral_path = self.data_dir / "global" / "jobs" / "neutral" / f"{social_class}.txt"
            if neutral_path.exists():
                jobs.extend(self.load_lines(neutral_path))

            # Add gender-specific jobs for this class
            if gender:
                gender_path = self.data_dir / "global" / "jobs" / gender / f"{social_class}.txt"
                if gender_path.exists():
                    jobs.extend(self.load_lines(gender_path))
        else:
            # Old structure (fallback for countries not using social classes)
            # Always include neutral jobs
            neutral_path = self.data_dir / "global" / "jobs" / "jobs_neutral.txt"
            if neutral_path.exists():
                jobs.extend(self.load_lines(neutral_path))

            # Add gender-specific jobs
            if gender:
                gender_path = self.data_dir / "global" / "jobs" / f"jobs_{gender}.txt"
                if gender_path.exists():
                    jobs.extend(self.load_lines(gender_path))

        return jobs

    def load_student_fields(self, country: str) -> List[str]:
        """
        Load student study fields for a country.

        Args:
            country: Country code (e.g., 'spain', 'russia')

        Returns:
            List of study fields
        """
        student_path = self.data_dir / "countries" / country / "jobs" / "students.txt"
        if student_path.exists():
            return self.load_lines(student_path)
        return []

    def load_class_hobbies(self, social_class: str) -> List[str]:
        """
        Load hobbies for a specific social class.

        Args:
            social_class: 'low', 'middle', 'upper-middle', 'high'

        Returns:
            List of hobbies appropriate for the social class
        """
        class_path = self.data_dir / "global" / "hobbies" / f"{social_class}.txt"
        if class_path.exists():
            return self.load_lines(class_path)
        return []

    def load_heights(self, country: str, gender: str) -> Dict[str, Tuple[int, int]]:
        """
        Load height ranges for a country and gender.

        Returns:
            Dict with categories (Short, Average, Tall) and their (min, max) ranges
        """
        filepath = self.data_dir / "countries" / country / "physical" / "heights" / f"{gender}s.txt"
        lines = self.load_lines(filepath)
        heights = {}
        for line in lines:
            parts = line.split(',')
            if len(parts) == 3:
                category = parts[0]
                min_height = int(parts[1])
                max_height = int(parts[2])
                heights[category] = (min_height, max_height)
        return heights

    def load_weights(self, country: str, gender: str) -> Dict[str, Tuple[int, int]]:
        """
        Load weight ranges for a country and gender.

        Returns:
            Dict with categories (e.g., Short_Normal) and their (min, max) ranges
        """
        filepath = self.data_dir / "countries" / country / "physical" / "weights" / f"{gender}s.txt"
        lines = self.load_lines(filepath)
        weights = {}
        for line in lines:
            parts = line.split(',')
            if len(parts) == 3:
                category = parts[0]
                min_weight = int(parts[1])
                max_weight = int(parts[2])
                weights[category] = (min_weight, max_weight)
        return weights

    def _get_name_age_bucket(self, age: int, rules: CountryRules = None) -> str:
        """
        Map age to the correct name bucket, using country rules for min_age and life_expectancy.
        """
        # Default values if rules not provided
        min_age = 18
        life_expectancy = 80
        if rules:
            min_age = rules.get_min_age()
            life_expectancy = rules.get_life_expectancy()
        if age < min_age + 5:
            return "very_young"
        elif min_age + 5 <= age < min_age + 16:
            return "young_adults"
        elif min_age + 16 <= age < 50:
            return "adults"
        elif 50 <= age < 65:
            return "older_adults"
        elif 65 <= age <= life_expectancy:
            return "elderly"
        else:
            return "elderly"

    def _get_bucket_index_with_offset(self, age: int, offset: int) -> str:
        """
        Get the bucket name for a given age, offset by a number of categories (clamped).
        """
        # Find the current bucket index
        bucket = self._get_name_age_bucket(age)
        try:
            idx = self._AGE_BUCKETS.index(bucket)
        except ValueError:
            idx = 0
        # Apply offset and clamp
        new_idx = max(0, min(len(self._AGE_BUCKETS) - 1, idx + offset))
        return self._AGE_BUCKETS[new_idx]

    def load_name_by_age(self, country: str, gender: str, age: int, bucket_offset: int = 0) -> str:
        """
        Load a random name from the appropriate age/gender bucket file for the given country, with optional bucket offset.
        If the bucket file does not exist or is empty, fallback to the closest available bucket with names.
        """
        rules = self.load_rules(country)
        bucket = self._get_bucket_index_with_offset(age, bucket_offset)
        base_path = self.data_dir / "countries" / country / "names" / (gender + "s")
        filepath = base_path / f"{bucket}.txt"
        # Try intended bucket first
        if filepath.exists():
            names = self.load_lines(filepath)
            if names:
                return random.choice(names)
        idx = self._AGE_BUCKETS.index(bucket)
        # Fallback: search closest buckets with names
        for offset in range(1, len(self._AGE_BUCKETS)):
            # Lower
            if idx - offset >= 0:
                alt_path = base_path / f"{self._AGE_BUCKETS[idx - offset]}.txt"
                if alt_path.exists():
                    names = self.load_lines(alt_path)
                    if names:
                        return random.choice(names)
            # Higher
            if idx + offset < len(self._AGE_BUCKETS):
                alt_path = base_path / f"{self._AGE_BUCKETS[idx + offset]}.txt"
                if alt_path.exists():
                    names = self.load_lines(alt_path)
                    if names:
                        return random.choice(names)
        # Last resort: try all buckets
        for b in self._AGE_BUCKETS:
            alt_path = base_path / f"{b}.txt"
            if alt_path.exists():
                names = self.load_lines(alt_path)
                if names:
                    return random.choice(names)
        raise ValueError(f"No names found for {country} {gender} in any age bucket.")

    def _get_hobbies_for_age_and_gender(self, gender: str, age: int, country: str) -> Tuple[List[str], List[str]]:
        """
        Load hobbies appropriate for a specific age/gender combination.

        Returns:
            Tuple of (age_appropriate_hobbies, country_specific_hobbies)
        """
        rules = self.load_rules(country)
        bucket = self._get_name_age_bucket(age, rules)

        # Age/gender appropriate hobbies
        age_hobbies = []
        hobby_path = self.data_dir / "global" / "hobbies" / f"{gender}s" / f"{bucket}.txt"
        if hobby_path.exists():
            age_hobbies = self.load_lines(hobby_path)

        # Country-specific hobbies
        country_hobbies = []
        country_hobby_path = self.data_dir / "countries" / country / "hobbies" / f"{bucket}.txt"
        if country_hobby_path.exists():
            country_hobbies = self.load_lines(country_hobby_path)

        return age_hobbies, country_hobbies

    def load_death_causes(self, age_at_death: int) -> List[str]:
        """
        Load appropriate death causes based on age at death.

        Args:
            age_at_death: Age when the person died

        Returns:
            List of possible death causes
        """
        death_causes_dir = self.data_dir / "global" / "death_causes"

        # Determine which death cause file to use based on age
        if age_at_death < 18:
            cause_file = death_causes_dir / "children.txt"
        elif age_at_death < 30:
            cause_file = death_causes_dir / "young_adults.txt"
        elif age_at_death < 60:
            cause_file = death_causes_dir / "adults.txt"
        else:
            cause_file = death_causes_dir / "elderly.txt"

        # Load causes from file
        causes = []
        if cause_file.exists():
            causes = self.load_lines(cause_file)

        # Also load generic causes that can apply to anyone
        generic_file = death_causes_dir / "generic.txt"
        if generic_file.exists():
            generic_causes = self.load_lines(generic_file)
            causes.extend(generic_causes)

        return causes if causes else ["Natural causes"]

    def load_divorce_causes(self, age: int) -> List[str]:
        """
        Load appropriate divorce causes based on age.

        Args:
            age: Age of the person at time of divorce

        Returns:
            List of possible divorce causes
        """
        divorce_causes_dir = self.data_dir / "global" / "divorce_causes"

        # Determine which divorce cause file to use based on age
        if age < 30:
            cause_file = divorce_causes_dir / "young_adults.txt"
        elif age < 50:
            cause_file = divorce_causes_dir / "adults.txt"
        elif age < 65:
            cause_file = divorce_causes_dir / "middle_aged.txt"
        else:
            cause_file = divorce_causes_dir / "elderly.txt"

        # Load causes from file
        causes = []
        if cause_file.exists():
            causes = self.load_lines(cause_file)

        return causes if causes else ["Irreconcilable differences"]

    def load_breakup_reasons(self) -> List[str]:
        """
        Load breakup reasons for boyfriend/girlfriend relationships.

        Returns:
            List of possible breakup reasons
        """
        breakup_reasons_file = self.data_dir / "global" / "breakup_reasons" / "general.txt"

        # Load reasons from file
        reasons = []
        if breakup_reasons_file.exists():
            reasons = self.load_lines(breakup_reasons_file)

        return reasons if reasons else ["Grew apart", "Different life goals"]

    def load_regional_characteristics(self, country: str, age: int, gender: str) -> List[str]:
        """
        Load regional/historical characteristics applicable to this person.

        Args:
            country: Country code
            age: Person's age
            gender: Person's gender ('male', 'female')

        Returns:
            List of applicable characteristics
        """
        filepath = self.data_dir / "countries" / country / "regional_characteristics.txt"

        if not filepath.exists():
            return []

        characteristics = []
        for line in self.load_lines(filepath):
            # Format: characteristic_text|min_age|max_age|gender|probability
            parts = line.split('|')
            if len(parts) != 5:
                continue

            text, min_age_str, max_age_str, char_gender, prob_str = parts
            min_age = int(min_age_str)
            max_age = int(max_age_str)
            probability = float(prob_str)

            # Check if this characteristic applies
            if age < min_age or age > max_age:
                continue

            # Check gender
            if char_gender.lower() not in ['both', gender.lower()]:
                continue

            # Apply probability
            if random.random() < probability:
                characteristics.append(text.strip())

        return characteristics

    def load_job_age_requirements(self) -> Dict[str, int]:
        """
        Load job age requirements from the global configuration file.

        Returns:
            Dictionary mapping job titles to minimum ages
        """
        requirements_file = self.data_dir / "global" / "jobs" / "age_requirements.txt"
        age_requirements = {}

        if requirements_file.exists():
            for line in self.load_lines(requirements_file):
                if ':' in line:
                    job, min_age_str = line.split(':', 1)
                    try:
                        age_requirements[job.strip()] = int(min_age_str.strip())
                    except ValueError:
                        pass  # Skip invalid entries

        return age_requirements

    def load_job_education_requirements(self) -> Dict[str, Tuple[str, str, int]]:
        """
        Load education and age requirements for jobs.

        Returns:
            Dict mapping job title to (min_education_level, field_of_study, min_age)
        """
        import json

        # Try new JSON format first (complete with age requirements)
        requirements_file_json = self.data_dir / "global" / "education" / "job_requirements_complete.json"

        if requirements_file_json.exists():
            try:
                with open(requirements_file_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    jobs = data.get('jobs', {})
                    education_reqs = {}

                    for job, requirements in jobs.items():
                        # Skip comment entries
                        if job.startswith('_comment'):
                            continue

                        if isinstance(requirements, list) and len(requirements) >= 3:
                            min_level = requirements[0]  # e.g., "bachelor"
                            field = requirements[1]       # e.g., "Medicine" or null
                            min_age = requirements[2]     # e.g., 30
                            education_reqs[job] = (min_level, field if field else "Any", min_age)

                    return education_reqs
            except Exception as e:
                # Fall back to old format if JSON fails
                pass

        # Fallback to old .txt format (without age requirements)
        requirements_file = self.data_dir / "global" / "education" / "job_education_map.txt"
        education_reqs = {}

        if requirements_file.exists():
            for line in self.load_lines(requirements_file):
                if ':' in line:
                    parts = line.split(':', 1)
                    job = parts[0].strip()
                    requirements = parts[1].strip().split(':')

                    if len(requirements) >= 1:
                        min_level = requirements[0].strip()
                        field = requirements[1].strip() if len(requirements) >= 2 else "Any"
                        # Default min age to 18 for old format
                        education_reqs[job] = (min_level, field, 18)

        return education_reqs

    def load_education_levels(self) -> List[str]:
        """
        Load ordered list of education levels.

        Returns:
            List of education levels from lowest to highest
        """
        levels_file = self.data_dir / "global" / "education" / "levels.txt"

        if levels_file.exists():
            return self.load_lines(levels_file)

        # Fallback default levels
        return [
            "No formal education",
            "Primary school incomplete",
            "Primary school",
            "Secondary education",
            "High school diploma",
            "Vocational training",
            "Associate degree",
            "Bachelor's degree",
            "Master's degree",
            "Doctorate/PhD"
        ]

    def load_language_certifications(self) -> Dict[str, List[str]]:
        """
        Load language certifications from file.

        Returns:
            Dict mapping "language:level" to list of certification options
        """
        cert_file = self.data_dir / "global" / "languages" / "certifications.txt"
        certifications = {}

        if cert_file.exists():
            for line in self.load_lines(cert_file):
                if ':' in line:
                    parts = line.split(':', 1)
                    lang_level = parts[0].strip()
                    certs = [c.strip() for c in parts[1].split(',')]
                    certifications[lang_level] = certs

        return certifications

    def load_termination_reasons(self) -> List[str]:
        """
        Load job termination reasons.

        Returns:
            List of termination reason strings
        """
        reasons_file = self.data_dir / "global" / "work" / "termination_reasons.txt"

        if reasons_file.exists():
            return self.load_lines(reasons_file)

        # Fallback default reasons
        return [
            "Better job opportunity",
            "Career change",
            "Relocation",
            "Company restructuring",
            "Contract ended",
            "Personal reasons",
            "Health reasons",
            "Retirement",
            "Layoff"
        ]
