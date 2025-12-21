#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synthetic Identity Generator - Main Entry Point
Generates realistic but fake identities for privacy protection.
"""

import random
import secrets
from datetime import date, timedelta, datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import json
import os
import subprocess


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


@dataclass
class Identity:
    """Represents a synthetic identity."""
    country: str
    gender: str
    first_name: str
    surnames: List[str]
    full_name: str
    date_of_birth: str  # Format from rules
    age: int
    city: str
    nearby_town: Optional[str]
    job: str
    hobbies: List[str]
    phone: str
    height_cm: int
    weight_kg: int
    hair_color: str
    eye_color: str
    skin_tone: str
    email: str
    website: str
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self, indent=2):
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    def to_str_box(self):
        """Human-readable string representation in a box with colors and formatting."""
        # ANSI color codes
        BOLD = '\033[1m'
        CYAN = '\033[96m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        RESET = '\033[0m'

        hobbies_str = ", ".join(self.hobbies)
        max_hobby_line = 44
        hobby_lines = []
        while hobbies_str:
            if len(hobbies_str) > max_hobby_line:
                split_idx = hobbies_str.rfind(",", 0, max_hobby_line)
                if split_idx == -1:
                    split_idx = max_hobby_line
                hobby_lines.append(hobbies_str[:split_idx].strip())
                hobbies_str = hobbies_str[split_idx+1:].strip()  # FIX: was 'trip', should be 'strip'
            else:
                hobby_lines.append(hobbies_str)
                hobbies_str = ""

        # Format lines with colors
        name_line = f"║ Full Name:       {BOLD}{CYAN}{self.full_name}{RESET}".ljust(62 + len(BOLD + CYAN + RESET)) + "║"
        gender_line = f"║ Gender:          {self.gender.capitalize()}".ljust(62) + "║"
        dob_text = f"{BOLD}{self.date_of_birth}{RESET} ({YELLOW}{self.age} years old{RESET})"
        dob_line = f"║ Date of Birth:   {dob_text}".ljust(62 + len(BOLD + RESET + YELLOW + RESET)) + "║"

        # Physical characteristics
        physical_text = f"{GREEN}{self.height_cm}cm{RESET}, {GREEN}{self.weight_kg}kg{RESET}"
        physical_line = f"║ Physical:        {physical_text}".ljust(62 + len(GREEN + RESET) * 2) + "║"
        skin_line = f"║ Skin:            {MAGENTA}{self.skin_tone}{RESET}".ljust(62 + len(MAGENTA + RESET)) + "║"
        hair_line = f"║ Hair:            {MAGENTA}{self.hair_color}{RESET}".ljust(62 + len(MAGENTA + RESET)) + "║"
        eyes_line = f"║ Eyes:            {MAGENTA}{self.eye_color}{RESET}".ljust(62 + len(MAGENTA + RESET)) + "║"

        location_text = f"{BOLD}{self.city}{RESET}, {self.country.upper()}"
        location_line = f"║ Location:        {location_text}".ljust(62 + len(BOLD + RESET)) + "║"
        nearby_text = self.nearby_town or 'N/A'
        nearby_line = f"║ Nearby:          {nearby_text}".ljust(62) + "║"
        job_line = f"║ Job:             {BLUE}{BOLD}{self.job}{RESET}{RESET}".ljust(62 + len(BLUE + BOLD + RESET + RESET)) + "║"
        phone_line = f"║ Phone:           {GREEN}{self.phone}{RESET}".ljust(62 + len(GREEN + RESET)) + "║"
        email_line = f"║ Email:           {CYAN}{self.email}{RESET}".ljust(62 + len(CYAN + RESET)) + "║"

        hobbies_block = ""
        for i, line in enumerate(hobby_lines):
            if i == 0:
                hobbies_block += f"║ Hobbies:         {line}".ljust(62) + "║\n"
            else:
                hobbies_block += f"║                  {line}".ljust(62) + "║\n"

        return f"""╔{'═'*62}╗
║{BOLD}{'SYNTHETIC IDENTITY'.center(62)}{RESET}║
╠{'═'*62}╣
{name_line}
{gender_line}
{dob_line}
{physical_line}
{skin_line}
{hair_line}
{eyes_line}
{location_line}
{nearby_line}
{job_line}
{phone_line}
{email_line}
{hobbies_block}╚{'═'*62}╝"""


class CountryRules:
    """Parses and stores country-specific rules."""
    
    def __init__(self, rules_path: Path):
        self.rules = self._parse_rules(rules_path)
    
    def _parse_rules(self, rules_path: Path) -> Dict[str, Any]:
        """Parse rules.txt file."""
        rules = {}
        
        with open(rules_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Parse list values (comma-separated)
                    if ',' in value:
                        value = [v.strip() for v in value.split(',')]
                    
                    rules[key] = value
        
        return rules
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a rule value."""
        return self.rules.get(key, default)
    
    def get_name_order(self) -> List[str]:
        """Get name order as list of components."""
        order = self.get('name_order', 'first+surname')
        return order.split('+')
    
    def get_surname_count(self) -> int:
        """Get number of surnames."""
        return int(self.get('surname_count', '1'))
    
    def get_date_format(self) -> str:
        """Get date format."""
        return self.get('date_format', 'DD/MM/YYYY')
    
    def get_phone_format(self) -> str:
        """Get phone format."""
        return self.get('phone_format', '### ### ###')
    
    def get_phone_country_code(self) -> str:
        """Get phone country code."""
        return self.get('phone_country_code', '+1')
    
    def get_phone_length(self) -> int:
        """Get phone number length (without country code)."""
        return int(self.get('phone_length', '10'))
    
    def get_phone_prefixes(self) -> List[str]:
        """Get phone prefixes (combines mobile and landline with preference for mobile)."""
        all_prefixes = []

        # Get mobile prefixes (70% weight)
        mobile_prefixes = self.get('phone_mobile_prefixes')
        if mobile_prefixes:
            if isinstance(mobile_prefixes, list):
                all_prefixes.extend(mobile_prefixes * 3)  # Triple weight for mobile
            elif isinstance(mobile_prefixes, str):
                all_prefixes.extend([mobile_prefixes] * 3)

        # Get landline prefixes (30% weight)
        landline_prefixes = self.get('phone_landline_prefixes')
        if landline_prefixes:
            if isinstance(landline_prefixes, list):
                all_prefixes.extend(landline_prefixes)
            elif isinstance(landline_prefixes, str):
                all_prefixes.append(landline_prefixes)

        # Fallback to generic prefixes
        if not all_prefixes:
            general_prefixes = self.get('phone_prefixes')
            if general_prefixes:
                if isinstance(general_prefixes, list):
                    all_prefixes = general_prefixes
                elif isinstance(general_prefixes, str):
                    all_prefixes = [general_prefixes]

        return all_prefixes if all_prefixes else ['6']  # Default

    def get_life_expectancy(self) -> int:
        """Get life expectancy for max age."""
        return int(self.get('life_expectancy', '80'))

    def get_min_age(self) -> int:
        """Get minimum age."""
        return int(self.get('min_age', '18'))

    def get_max_age(self) -> int:
        """Get maximum age (defaults to life expectancy)."""
        max_age = self.get('max_age')
        if max_age:
            return int(max_age)
        return self.get_life_expectancy()

    def get_hair_colors(self) -> Dict[str, float]:
        """Get dict of hair colors with probabilities.
        Format: {'Color Name': probability}"""
        colors_str = self.get('hair_colors')
        if not colors_str:
            return {'Black': 35, 'Brown': 30, 'Dark Brown': 20, 'Light Brown': 10, 'Blonde': 4, 'Red': 1}

        colors_dict = {}
        if isinstance(colors_str, list):
            # Format: ['Black:35', 'Brown:30', ...]
            for item in colors_str:
                if ':' in item:
                    color, prob = item.split(':', 1)
                    colors_dict[color.strip()] = float(prob.strip())
                else:
                    colors_dict[item.strip()] = 10  # Default probability
        elif isinstance(colors_str, str):
            # Single string format
            for item in colors_str.split(','):
                if ':' in item:
                    color, prob = item.split(':', 1)
                    colors_dict[color.strip()] = float(prob.strip())
                else:
                    colors_dict[item.strip()] = 10
        return colors_dict

    def get_eye_colors(self) -> Dict[str, float]:
        """Get dict of eye colors with probabilities.
        Format: {'Color Name': probability}"""
        colors_str = self.get('eye_colors')
        if not colors_str:
            return {'Brown': 50, 'Dark Brown': 30, 'Light Brown': 10, 'Green': 5, 'Blue': 4, 'Hazel': 1}

        colors_dict = {}
        if isinstance(colors_str, list):
            for item in colors_str:
                if ':' in item:
                    color, prob = item.split(':', 1)
                    colors_dict[color.strip()] = float(prob.strip())
                else:
                    colors_dict[item.strip()] = 10
        elif isinstance(colors_str, str):
            for item in colors_str.split(','):
                if ':' in item:
                    color, prob = item.split(':', 1)
                    colors_dict[color.strip()] = float(prob.strip())
                else:
                    colors_dict[item.strip()] = 10
        return colors_dict

    def get_skin_tones(self) -> Dict[str, float]:
        """Get dict of skin tones with probabilities.
        Format: {'Tone Name': probability}"""
        tones_str = self.get('skin_tones')
        if not tones_str:
            return {'Light': 50, 'Medium': 30, 'Olive': 15, 'Tan': 4, 'Dark': 1}

        tones_dict = {}
        if isinstance(tones_str, list):
            for item in tones_str:
                if ':' in item:
                    tone, prob = item.split(':', 1)
                    tones_dict[tone.strip()] = float(prob.strip())
                else:
                    tones_dict[item.strip()] = 10
        elif isinstance(tones_str, str):
            for item in tones_str.split(','):
                if ':' in item:
                    tone, prob = item.split(':', 1)
                    tones_dict[tone.strip()] = float(prob.strip())
                else:
                    tones_dict[item.strip()] = 10
        return tones_dict


class DataLoader:
    """Loads data files from disk."""
    
    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self._cache = {}
    
    def load_lines(self, filepath: Path) -> List[str]:
        """Load lines from a text file, skipping empty lines and comments."""
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
        """Load country rules."""
        filepath = self.data_dir / "countries" / country / "rules.txt"
        return CountryRules(filepath)
    
    def load_names(self, country: str, gender: str) -> List[str]:
        """Load names for a specific country and gender."""
        filepath = self.data_dir / "countries" / country / "names" / f"{gender}s.txt"
        return self.load_lines(filepath)
    
    def load_surnames(self, country: str) -> List[str]:
        """Load surnames for a specific country."""
        filepath = self.data_dir / "countries" / country / "surnames.txt"
        return self.load_lines(filepath)
    
    def load_cities(self, country: str) -> List[str]:
        """Load cities for a specific country."""
        filepath = self.data_dir / "countries" / country / "cities.txt"
        return self.load_lines(filepath)
    
    def load_jobs(self, gender: Optional[str] = None) -> List[str]:
        """Load jobs list based on gender (male/female/neutral combined)."""
        jobs = []

        # Always include neutral jobs
        neutral_path = self.data_dir / "global" / "jobs" / "jobs_neutral.txt"
        jobs.extend(self.load_lines(neutral_path))

        # Add gender-specific jobs
        if gender:
            gender_path = self.data_dir / "global" / "jobs" / f"jobs_{gender}.txt"
            jobs.extend(self.load_lines(gender_path))

        return jobs

    def load_hobbies(self, gender: Optional[str] = None) -> List[str]:
        """Load hobbies list based on gender (male/female/neutral combined)."""
        hobbies = []

        # Always include neutral hobbies
        neutral_path = self.data_dir / "global" / "hobbies" / "hobbies_neutral.txt"
        hobbies.extend(self.load_lines(neutral_path))

        # Add gender-specific hobbies
        if gender:
            gender_path = self.data_dir / "global" / "hobbies" / f"hobbies_{gender}.txt"
            hobbies.extend(self.load_lines(gender_path))

        return hobbies

    def load_heights(self, country: str, gender: str) -> Dict[str, tuple]:
        """Load height ranges for a country and gender.
        Returns dict with categories (Short, Average, Tall) and their (min, max) ranges."""
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

    def load_weights(self, country: str, gender: str) -> Dict[str, tuple]:
        """Load weight ranges for a country and gender.
        Returns dict with categories (e.g., Short_Normal) and their (min, max) ranges."""
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


class IdentityGenerator:
    """Generates synthetic identities."""

    def __init__(self, data_loader: DataLoader):
        self.loader = data_loader
        # Seed random with cryptographically secure randomness
        random.seed(secrets.randbits(256))

    def _generate_fake_email(self, first_name: str, surnames: List[str], dob: str) -> str:
        """Generate a fake email based on identity information.

        Args:
            first_name: Person's first name
            surnames: List of surnames
            dob: Date of birth string

        Returns:
            Fake email address
        """
        # Available domains from fakemailgenerator.com
        domains = [
            'armyspy.com', 'cuvox.de', 'dayrep.com', 'einrot.com',
            'fleckens.hu', 'gustr.com', 'jourrapide.com', 'rhyta.com',
            'superrito.com', 'teleworm.us'
        ]

        # Clean name parts (remove accents and convert to ASCII)
        def clean_text(text):
            # Remove accents
            import unicodedata
            text = unicodedata.normalize('NFD', text)
            text = text.encode('ascii', 'ignore').decode('utf-8')
            return text.lower().strip()

        clean_first = clean_text(first_name)
        clean_surnames = [clean_text(s) for s in surnames]

        # Extract year from date of birth (various formats)
        year = ''
        if '/' in dob:
            parts = dob.split('/')
            # Could be DD/MM/YYYY or MM/DD/YYYY
            for part in parts:
                if len(part) == 4:
                    year = part[-2:]  # Last 2 digits
                    break

        # Get initials and short forms for more realistic emails
        first_initial = clean_first[0] if clean_first else 'x'
        # Take first 2-3 letters of first name
        first_short = clean_first[:3] if len(clean_first) >= 3 else clean_first
        # Take first 2-4 letters of each surname
        surname1_short = clean_surnames[0][:4] if len(clean_surnames[0]) >= 4 else clean_surnames[0]
        surname2_short = clean_surnames[1][:3] if len(clean_surnames) > 1 and len(clean_surnames[1]) >= 3 else ""

        # Generate realistic email patterns (NO dots, more like real users)
        patterns = [
            f"{clean_first}{clean_surnames[0]}",  # alfonsoperez
            f"{first_initial}{clean_surnames[0]}",  # aperez
            f"{first_short}{clean_surnames[0]}",  # alfperez
            f"{first_initial}{surname1_short}",  # aper
            f"{first_short}{surname1_short}",  # alfper
            f"{clean_first}{year}",  # alfonso90
            f"{first_short}{surname1_short}{year}",  # alfper90
            f"{first_initial}{surname1_short}{year}",  # aper90
            f"{clean_surnames[0]}{clean_first}",  # perezalfonso
            f"{surname1_short}{first_short}",  # peralfonhort
        ]

        # Add variations with both surnames if available
        if len(clean_surnames) > 1 and surname2_short:
            patterns.extend([
                f"{first_initial}{surname1_short}{surname2_short}",  # aperlop
                f"{first_short}{surname1_short}{surname2_short}",  # alfperlop
                f"{first_initial}{surname1_short}{surname2_short}{year}",  # aperlop90
            ])

        # Select random pattern and domain
        local_part = random.choice(patterns)
        domain = random.choice(domains)

        return f"{local_part}@{domain}"

    def _weighted_choice(self, options: Dict[str, float]) -> str:
        """Select an option based on weighted probabilities.

        Args:
            options: Dict of {option: probability_weight}

        Returns:
            Selected option string
        """
        # Filter out zero probabilities
        valid_options = {k: v for k, v in options.items() if v > 0}
        if not valid_options:
            return list(options.keys())[0] if options else "Unknown"

        # Create list of options and weights
        items = list(valid_options.keys())
        weights = list(valid_options.values())

        # Use random.choices with weights
        return random.choices(items, weights=weights, k=1)[0]
    
    def _generate_dob(self, date_format: str, min_age: int = 18, max_age: int = 80) -> tuple[str, int]:
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
        # Map format tokens to strftime codes
        format_str = format_str.replace('DD', '%d')
        format_str = format_str.replace('MM', '%m')
        format_str = format_str.replace('YYYY', '%Y')
        format_str = format_str.replace('YY', '%y')
        
        return date_obj.strftime(format_str)
    
    def _parse_city_line(self, line: str) -> tuple[str, Optional[str]]:
        """
        Parse a city line. 
        Format can be:
        - "Madrid" (just city)
        - "Alcalá de Henares, Madrid" (nearby town, main city)
        
        Returns:
            Tuple of (city, nearby_town_or_none)
        """
        if ',' in line:
            # "Alcalá de Henares, Madrid" -> nearby_town = "Alcalá de Henares", city = "Madrid"
            parts = [p.strip() for p in line.split(',')]
            return parts[1], parts[0]  # (main_city, nearby_town)
        else:
            # Just "Madrid"
            return line, None
    
    def _generate_phone(self, rules: CountryRules) -> str:
        """
        Generate a phone number according to country rules.
        
        Args:
            rules: CountryRules object
        
        Returns:
            Formatted phone number
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
    
    def _build_full_name(self, components: Dict[str, Any], name_order: List[str]) -> str:
        """
        Build full name according to name_order rules.

        Args:
            components: Dict with 'first', 'surname1', 'surname2', etc.
            name_order: List like ['first', 'surname1', 'surname2'] or ['first', 'surname']

        Returns:
            Full name string
        """
        parts = []
        for component in name_order:
            if component in components:
                parts.append(components[component])
            elif component == 'surname' and 'surname1' in components:
                # Handle 'surname' -> 'surname1' mapping for countries with single surname
                parts.append(components['surname1'])
        return ' '.join(parts)

    def _get_job_for_age(self, age: int, jobs: List[str]) -> str:
        """Get appropriate job based on age."""
        # Retired people (65+)
        if age >= 65:
            return "Retired"
        # Everyone else gets a job from the list
        return random.choice(jobs)

    def _filter_hobbies_by_age(self, hobbies: List[str], age: int) -> List[str]:
        """Filter hobbies to ensure they are age-appropriate.

        Args:
            hobbies: List of all available hobbies
            age: Person's age

        Returns:
            Filtered list of age-appropriate hobbies
        """
        # Define physically intensive or youth-oriented hobbies to exclude for elderly (60+)
        elderly_exclude = {
            'Belly dancing', 'Zumba', 'Salsa dancing', 'Contemporary dance', 'Ballet',
            'Skateboarding', 'Surfing', 'Snowboarding', 'Rock climbing', 'Parkour',
            'BMX biking', 'Rollerblading', 'Ice skating', 'Skiing', 'Extreme sports',
            'TikTok', 'Instagram', 'Social media', 'Vlogging', 'Blogging',
            'Gaming', 'Video games', 'Streaming', 'Twitch', 'YouTube',
            'Clubbing', 'Partying', 'Bar hopping', 'Nightlife',
            'CrossFit', 'Martial arts', 'Boxing', 'MMA', 'Wrestling',
            'Marathon running', 'Triathlons', 'Heavy weightlifting'
        }

        # Define physically very intensive hobbies to exclude for very elderly (70+)
        very_elderly_exclude = {
            'Hiking', 'Mountain biking', 'Running', 'Jogging', 'Cycling',
            'Swimming laps', 'Tennis', 'Basketball', 'Soccer', 'Football',
            'Volleyball', 'Baseball', 'Softball', 'Hockey',
            'Dance classes', 'Ballroom dancing', 'Aerobics', 'Kickboxing'
        }

        filtered = []
        for hobby in hobbies:
            # For people 70+, exclude both sets
            if age >= 70:
                if hobby not in elderly_exclude and hobby not in very_elderly_exclude:
                    filtered.append(hobby)
            # For people 60-69, exclude just the elderly set
            elif age >= 60:
                if hobby not in elderly_exclude:
                    filtered.append(hobby)
            # For people under 60, include all hobbies
            else:
                filtered.append(hobby)

        return filtered if filtered else hobbies  # Return all if filter removes everything

    def _adjust_hair_color_for_age(self, age: int, hair_colors: Dict[str, float]) -> str:
        """Adjust hair color based on age - older people more likely to have gray/white hair.

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
                # Boost gray/white probabilities
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

    def _generate_physical_characteristics(self, country: str, gender: str, age: int, rules: CountryRules) -> tuple:
        """Generate height, weight, hair color, eye color, and skin tone."""
        # Load height ranges
        heights = self.loader.load_heights(country, gender)

        # Select height category with realistic distribution
        # Adjust probabilities for elderly (60+) - they tend to be shorter
        if age >= 60:
            # Elderly: More likely to be short/average, rarely tall
            # Women lose more height with age
            if gender == 'female':
                # Elderly women: 50% Short, 45% Average, 5% Tall
                rand = random.random()
                if rand < 0.50:
                    height_category = "Short"
                elif rand < 0.95:
                    height_category = "Average"
                else:
                    height_category = "Tall"
            else:
                # Elderly men: 40% Short, 55% Average, 5% Tall
                rand = random.random()
                if rand < 0.40:
                    height_category = "Short"
                elif rand < 0.95:
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

        # Generate random height within category
        min_h, max_h = heights[height_category]
        height_cm = random.randint(min_h, max_h)

        # Apply age-based height reduction (people lose height as they age)
        # After 60, reduce height by 1-2cm per decade on average
        if age >= 60:
            # Calculate decades over 60
            decades_over_60 = (age - 60) / 10.0
            # Women lose slightly more height
            reduction_per_decade = 2 if gender == 'female' else 1.5
            height_reduction = int(decades_over_60 * reduction_per_decade)
            height_cm = max(height_cm - height_reduction, min_h - 5)  # Don't go too low

        # Load weight ranges
        weights = self.loader.load_weights(country, gender)

        # Select weight category with realistic distribution
        # 10% Underweight, 50% Normal, 30% Overweight, 10% Obese
        rand = random.random()
        if rand < 0.10:
            weight_category = f"{height_category}_Underweight"
        elif rand < 0.60:
            weight_category = f"{height_category}_Normal"
        elif rand < 0.90:
            weight_category = f"{height_category}_Overweight"
        else:
            weight_category = f"{height_category}_Obese"

        # Generate random weight within category
        min_w, max_w = weights[weight_category]
        weight_kg = random.randint(min_w, max_w)

        # Physical characteristics with weighted probabilities
        hair_colors = rules.get_hair_colors()
        eye_colors = rules.get_eye_colors()
        skin_tones = rules.get_skin_tones()

        # Use weighted selection for all characteristics
        hair_color = self._adjust_hair_color_for_age(age, hair_colors)
        eye_color = self._weighted_choice(eye_colors)
        skin_tone = self._weighted_choice(skin_tones)

        return height_cm, weight_kg, hair_color, eye_color, skin_tone
    
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
            Identity object
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

        # Load data
        first_names = self.loader.load_names(country, gender)
        surnames = self.loader.load_surnames(country)
        city_lines = self.loader.load_cities(country)
        jobs = self.loader.load_jobs(gender)
        hobbies = self.loader.load_hobbies(gender)

        # Select first name
        first_name = random.choice(first_names)

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
        full_name = self._build_full_name(name_components, name_order)

        # Generate DOB and age
        date_format = rules.get_date_format()
        dob, age = self._generate_dob(date_format, min_age, max_age)

        # Generate physical characteristics
        height_cm, weight_kg, hair_color, eye_color, skin_tone = self._generate_physical_characteristics(
            country, gender, age, rules
        )

        # Select city
        city_line = random.choice(city_lines)
        city, nearby_town = self._parse_city_line(city_line)

        # Select job based on age
        job = self._get_job_for_age(age, jobs)

        # Filter hobbies by age to ensure they're appropriate
        age_appropriate_hobbies = self._filter_hobbies_by_age(hobbies, age)

        # Select 2-5 hobbies from the filtered list
        num_hobbies = random.randint(2, 5)
        selected_hobbies = random.sample(age_appropriate_hobbies, min(num_hobbies, len(age_appropriate_hobbies)))

        # Generate phone
        phone = self._generate_phone(rules)

        # Generate email
        email = self._generate_fake_email(first_name, selected_surnames, dob)

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
            job=job,
            hobbies=selected_hobbies,
            phone=phone,
            height_cm=height_cm,
            weight_kg=weight_kg,
            hair_color=hair_color,
            eye_color=eye_color,
            skin_tone=skin_tone,
            email=email,
            website=website
        )

        return identity


def get_inbox_url(email: str) -> str:
    """Get the inbox URL for a fake email address.

    Args:
        email: The fake email address

    Returns:
        URL to access the inbox
    """
    local_part = email.split('@')[0]
    domain = email.split('@')[1]
    return f"https://www.fakemailgenerator.com/#/{domain}/{local_part}/"


def save_identity(identity: Identity, directory: str = "identities-generated") -> str:
    """Save identity to JSON file.

    Args:
        identity: Identity object to save
        directory: Directory to save identities

    Returns:
        Path to saved file
    """
    # Create directory if it doesn't exist
    Path(directory).mkdir(exist_ok=True)

    # Generate filename: email_timestamp.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    email_clean = identity.email.replace('@', '_at_').replace('.', '_')
    filename = f"{email_clean}_{timestamp}.json"
    filepath = Path(directory) / filename

    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(identity.to_json())

    return str(filepath)


def load_identity(filepath: str) -> Identity:
    """Load identity from JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Identity object
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return Identity(**data)


def list_saved_identities(directory: str = "identities-generated") -> List[Path]:
    """List all saved identity files.

    Args:
        directory: Directory containing identities

    Returns:
        List of Path objects to identity files
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []

    # Get all JSON files, sorted by modification time (newest first)
    files = sorted(dir_path.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    return files


def delete_identity(filepath: Path) -> bool:
    """Delete a specific identity file.

    Args:
        filepath: Path to identity file to delete

    Returns:
        True if deleted successfully
    """
    try:
        filepath.unlink()
        return True
    except Exception:
        return False


def clean_all_identities(directory: str = "identities-generated") -> int:
    """Delete all saved identities.

    Args:
        directory: Directory containing identities

    Returns:
        Number of files deleted
    """
    files = list_saved_identities(directory)
    deleted = 0
    for filepath in files:
        if delete_identity(filepath):
            deleted += 1
    return deleted


def generate_new_identity():
    """Generate a new identity interactively."""
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RESET = '\033[0m'

    print(f"{BOLD}{YELLOW}Current world:{RESET}")


    # ASCII art of the world (flat earth)
    print('''
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣄⣠⣀⡀⣀⣠⣤⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⢠⣠⣼⣿⣿⣿⣟⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⢠⣤⣦⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣟⣾⣿⣽⣿⣿⣅⠈⠉⠻⣿⣿⣿⣿⣿⡿⠇⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⢀⡶⠒⢉⡀⢠⣤⣶⣶⣿⣷⣆⣀⡀⠀⢲⣖⠒⠀⠀⠀⠀⠀⠀⠀
⢀⣤⣾⣶⣦⣤⣤⣶⣿⣿⣿⣿⣿⣿⣽⡿⠻⣷⣀⠀⢻⣿⣿⣿⡿⠟⠀⠀⠀⠀⠀⠀⣤⣶⣶⣤⣀⣀⣬⣷⣦⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣤⣦⣼⣀⠀
⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠓⣿⣿⠟⠁⠘⣿⡟⠁⠀⠘⠛⠁⠀⠀⢠⣾⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠏⠙⠁
⠀⠸⠟⠋⠀⠈⠙⣿⣿⣿⣿⣿⣿⣷⣦⡄⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⣼⣆⢘⣿⣯⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡉⠉⢱⡿⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⡿⠦⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⡗⠀⠈⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣉⣿⡿⢿⢷⣾⣾⣿⣞⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⣠⠟⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⠿⠿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣾⣿⣿⣷⣦⣶⣦⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠈⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⣿⣤⡖⠛⠶⠤⡀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⠙⣿⣿⠿⢻⣿⣿⡿⠋⢩⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠧⣤⣦⣤⣄⡀⠀⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠘⣧⠀⠈⣹⡻⠇⢀⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣤⣀⡀⠀⠀⠀⠀⠀⠀⠈⢽⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⣴⣿⣷⢲⣦⣤⡀⢀⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣷⢀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠂⠛⣆⣤⡜⣟⠋⠙⠂⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⠉⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣾⣿⣿⣿⣿⣆⠀⠰⠄⠀⠉⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⠿⠿⣿⣿⣿⠇⠀⠀⢀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡿⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⡇⠀⠀⢀⣼⠗⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠃⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
''')

    # Dynamically list all country directories in data/countries
    countries_path = Path(__file__).parent.parent / 'data' / 'countries'
    available_countries = sorted([d.name for d in countries_path.iterdir() if d.is_dir()])

    # Try to get a display name from a rules.txt or fallback to capitalized code
    country_display_names = {}
    for code in available_countries:
        rules_path = countries_path / code / 'rules.txt'
        display_name = code.capitalize()
        if rules_path.exists():
            try:
                with open(rules_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().startswith('country_name='):
                            display_name = line.strip().split('=', 1)[1].strip()
                            break
            except Exception:
                pass
        country_display_names[code] = display_name

    print(f"{BOLD}{YELLOW}Available countries:{RESET}")
    # Print countries in 3 columns, numbers in red, perfectly aligned
    RED = '\033[91m'
    num_cols = 3
    col_entries = [[] for _ in range(num_cols)]
    num_rows = (len(available_countries) + num_cols - 1) // num_cols
    for idx, code in enumerate(available_countries):
        col = idx // num_rows
        display = f"    [{RED}{idx:02d}{RESET}] {country_display_names[code]} ({code})"
        col_entries[col].append(display)
    # Pad columns to same number of rows
    for col in range(num_cols):
        while len(col_entries[col]) < num_rows:
            col_entries[col].append("")
    col_widths = [max(len(entry) for entry in col_entries[col]) for col in range(num_cols)]
    for row in range(num_rows):
        line = "  ".join(col_entries[col][row].ljust(col_widths[col]) for col in range(num_cols))
        print(line)
    print()

    print(f"{YELLOW}Press Enter without typing a number to select a random country.{RESET}")
    choice = input(f"{BOLD}Select country:{RESET} ").strip()
    print()

    if choice.isdigit():
        choice_num = int(choice)
        if 0 <= choice_num < len(available_countries):
            selected_country = available_countries[choice_num]
        else:
            selected_country = random.choice(available_countries)
    else:
        selected_country = random.choice(available_countries)

    print(f"{YELLOW}Please enter the website where you intend to use this synthetic identity (e.g., https://example.com):{RESET}")
    website = input(f"{BOLD}Website:{RESET} ").strip()
    print()

    data_loader = DataLoader()
    generator = IdentityGenerator(data_loader)

    print(f"{GREEN}Generating {country_display_names[selected_country]} identity...{RESET}")
    print()

    identity = generator.generate(country=selected_country, website=website)

    print(f"{BOLD}{CYAN}Identity for website:{RESET} {YELLOW}{website}{RESET}")
    print()
    print(identity.to_str_box())

    inbox_url = get_inbox_url(identity.email)
    print(f"\n{BOLD}Email inbox URL:{RESET} {CYAN}{inbox_url}{RESET}")

    filepath = save_identity(identity)
    print(f"\n{GREEN}Identity saved to:{RESET} {filepath}")
    print()

    input(f"{BOLD}Press Enter to continue...{RESET}")
    clear_screen()


def view_saved_identities():
    """View and select from saved identities."""
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

    files = list_saved_identities()

    if not files:
        print(f"{RED}No saved identities found.{RESET}")
        return

    print(f"{BOLD}Saved identities:{RESET}\n")

    for i, filepath in enumerate(files):
        identity = load_identity(str(filepath))
        print(f"[{i:02d}] {CYAN}{identity.email}{RESET} - {identity.website}")

    print(f"[{len(files):02d}] Return to menu")
    print()
    choice = input(f"{BOLD}Select identity to view:{RESET} ").strip()

    if not choice.isdigit():
        print(f"{RED}Invalid option.{RESET}")
        return

    idx = int(choice)

    if idx == len(files):
        clear_screen()
        return

    if idx < 0 or idx >= len(files):
        print(f"{RED}Invalid option.{RESET}")
        return

    identity = load_identity(str(files[idx]))

    print()
    print(f"{BOLD}{CYAN}Identity for website:{RESET} {YELLOW}{identity.website}{RESET}")
    print()
    print(identity.to_str_box())

    inbox_url = get_inbox_url(identity.email)
    print(f"\n{BOLD}Email inbox URL:{RESET} {CYAN}{inbox_url}{RESET}")
    print()

    input(f"{BOLD}Press Enter to continue...{RESET}")
    clear_screen()


def check_emails():
    """Check emails for saved identities with refresh option."""
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'

    files = list_saved_identities()

    if not files:
        print(f"{RED}No saved identities found.{RESET}")
        return

    print(f"{BOLD}Email inboxes:{RESET}\n")

    emails_list = []
    for i, filepath in enumerate(files):
        identity = load_identity(str(filepath))
        emails_list.append((identity.email, identity.website))
        print(f"[{i:02d}] {CYAN}{identity.email}{RESET} ({identity.website})")

    print(f"[{len(emails_list):02d}] Return to menu")
    print()
    choice = input(f"{BOLD}Select email inbox to check:{RESET} ").strip()

    if not choice.isdigit():
        print(f"{RED}Invalid option.{RESET}")
        return

    idx = int(choice)

    if idx == len(emails_list):
        clear_screen()
        return

    if idx < 0 or idx >= len(emails_list):
        print(f"{RED}Invalid option.{RESET}")
        return

    email, website = emails_list[idx]
    inbox_url = get_inbox_url(email)

    print()
    print(f"{BOLD}{CYAN}Checking inbox for:{RESET} {YELLOW}{email}{RESET}")
    print(f"{BOLD}Website:{RESET} {website}")
    print(f"{BOLD}Inbox URL:{RESET} {inbox_url}")
    print()

    while True:
        print(f"{GREEN}Fetching emails...{RESET}")
        try:
            result = subprocess.run(
                ['curl', '-s', inbox_url],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print(result.stdout[:2000])
            else:
                print(f"{RED}Error fetching inbox.{RESET}")

        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")

        print()
        refresh = input(f"{BOLD}Press 'r' to refresh, or any other key to return to menu:{RESET} ").strip().lower()

        if refresh != 'r':
            clear_screen()
            break
        print()


def delete_specific_identity():
    """Delete a specific identity from the list."""
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'

    files = list_saved_identities()

    if not files:
        print(f"{RED}No saved identities found.{RESET}")
        return

    print(f"{BOLD}Saved identities:{RESET}\n")

    for i, filepath in enumerate(files):
        identity = load_identity(str(filepath))
        print(f"[{i:02d}] {CYAN}{identity.email}{RESET} - {identity.website}")

    print(f"[{len(files):02d}] Return to menu")
    print()
    choice = input(f"{BOLD}Select identity to delete:{RESET} ").strip()

    if not choice.isdigit():
        print(f"{RED}Invalid option.{RESET}")
        return

    idx = int(choice)

    if idx == len(files):
        clear_screen()
        return

    if idx < 0 or idx >= len(files):
        print(f"{RED}Invalid option.{RESET}")
        return

    identity = load_identity(str(files[idx]))
    confirm = input(f"{BOLD}{RED}Delete {identity.email}? (y/n):{RESET} ").strip().lower()

    # Accept 'y', 'yes', or empty (Enter) as confirmation
    if confirm in ('y', 'yes', ''):
        if delete_identity(files[idx]):
            print(f"{GREEN}Identity deleted successfully.{RESET}")
        else:
            print(f"{RED}Error deleting identity.{RESET}")
    else:
        print(f"{YELLOW}Cancelled.{RESET}")

    print()
    input(f"{BOLD}Press Enter to continue...{RESET}")
    clear_screen()


def clean_all_identities_menu():
    """Clean all identities with confirmation."""
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

    files = list_saved_identities()

    if not files:
        print(f"{YELLOW}No identities to clean.{RESET}")
        return

    count = len(files)
    confirm = input(f"{BOLD}{RED}Delete ALL {count} identities? This cannot be undone! (yes/no):{RESET} ").strip().lower()

    # Accept 'yes', 'y', or empty (Enter) as confirmation
    if confirm in ('yes', 'y', ''):
        deleted = clean_all_identities()
        print(f"{GREEN}Deleted {deleted} identities.{RESET}")
    else:
        print(f"{YELLOW}Cancelled.{RESET}")


def main():
    """Main entry point with menu system."""
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

    # Clear screen on startup
    clear_screen()
    print(
        '''
███████████████████░ ░░░███░░ ░░███████████████████
██████████████████               ▓█████████████████
█████████████████░                █████████████████
█████████████████                 ▓████████████████
████████████████░░░░▓█████████▓▒░░░████████████████
██████████████████▓░░   ░░ ░░░░░▓██████████████████
███████████████░                   ░███████████████
███████████▒░░                        ░████████████
█████████████▒░░                   ░░▓█████████████
███████████████░                    ███████████████
████████████████░░                ░████████████████
█████████████████▒░              ▓█████████████████
██████████████████░            ░░██████████████████
███████████████████░           ░███████████████████
███████████████████░█         █░███████████████████
█████████████████  ▒███▓░░░████▓  █████████████████
██████████████░░   ▓████████████░  ░░▒█████████████
████████▒░░       ██░░██   ▓█░░█▓        ░░████████
████▒░░           █████     █████░█          ░▒████
███░              ██████   ██████░██▒          ░███
██▓              ░▓█████   █████▓▓█░            ▓██
██                 ████▒   ▒████░███            ░██
██                 ████░   ░████░█░              ██
█▒                 ░███    ░███░█░               ▒█
█                   ▒██     ██▒░                 ░█
█                   ░██     █▓                    █
░                     ░     ▒                     ░
░                                                  
                                       
        '''
    )
    print("=" * 64)
    print(f"{BOLD}{CYAN}{'SYNTHETIC IDENTITY GENERATOR'.center(64)}{RESET}")
    print(f"{'A professional tool for privacy and research purposes.'.center(64)}")
    print(f"{'Developed by Leucocito  |  GitHub: https://github.com/LeucoByte'.center(64)}")
    print("=" * 64)
    print()
    print(f"{BOLD}{YELLOW}WARNING:{RESET} This tool is intended strictly for privacy protection, research, and software testing purposes.\n")
    print("Any misuse, including fraud, impersonation, or illegal activities, is strictly prohibited and may have legal consequences.\nPlease use this tool responsibly and ethically.")
    print()

    while True:
        print(f"{BOLD}{YELLOW}What would you like to do?{RESET}")
        RED = '\033[91m'
        options = [
            "Generate new identity",
            "View saved identities",
            "Check email inbox",
            "Delete specific identity",
            "Clean all identities",
            "Exit"
        ]
        for i, opt in enumerate(options):
            print(f"    [{RED}{i}{RESET}] {opt}")
        print()
        choice = input(f"{BOLD}Select option:{RESET} ").strip()
        print()
        if choice == '0':
            clear_screen()
            generate_new_identity()
        elif choice == '1':
            clear_screen()
            view_saved_identities()
        elif choice == '2':
            clear_screen()
            check_emails()
        elif choice == '3':
            clear_screen()
            delete_specific_identity()
        elif choice == '4':
            clear_screen()
            clean_all_identities_menu()
        elif choice == '5':
            print(f"{BOLD}Goodbye!{RESET}")
            break
        else:
            print(f"{RED}Invalid option. Please try again.{RESET}\n")

if __name__ == "__main__":
    main()