#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data models for the Synthetic Identity Generator.
Contains Identity dataclass and CountryRules parser.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any
from wcwidth import wcswidth
from datetime import datetime

from config import (
    BOLD, RED, WHITE, YELLOW, MAGENTA, CYAN, RESET,
    BOX_WIDTH, CONTENT_WIDTH, GREEN
)

# Import transliteration libraries
try:
    from pythainlp.transliterate import romanize as thai_romanize
    PYTHAINLP_AVAILABLE = True
except ImportError:
    PYTHAINLP_AVAILABLE = False

try:
    from pypinyin import lazy_pinyin, Style
    PYPINYIN_AVAILABLE = True
except ImportError:
    PYPINYIN_AVAILABLE = False

try:
    import cutlet
    CUTLET_AVAILABLE = True
    # Initialize Japanese romanizer
    try:
        katsu = cutlet.Cutlet()
    except:
        CUTLET_AVAILABLE = False
except ImportError:
    CUTLET_AVAILABLE = False

try:
    from transliterate import translit
    TRANSLITERATE_AVAILABLE = True
except ImportError:
    TRANSLITERATE_AVAILABLE = False

try:
    from unidecode import unidecode
    UNIDECODE_AVAILABLE = True
except ImportError:
    UNIDECODE_AVAILABLE = False


# Transliteration map for Cyrillic to Latin
CYRILLIC_TO_LATIN = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E', 'Ж': 'Zh',
    'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O',
    'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts',
    'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu',
    'Я': 'Ya',
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh',
    'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
    'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
    'я': 'ya'
}

# Transliteration map for Thai to Latin (RTGS - Royal Thai General System)
THAI_TO_LATIN = {
    # Consonants
    'ก': 'k', 'ข': 'kh', 'ฃ': 'kh', 'ค': 'kh', 'ฅ': 'kh', 'ฆ': 'kh',
    'ง': 'ng',
    'จ': 'ch', 'ฉ': 'ch', 'ช': 'ch', 'ซ': 's', 'ฌ': 'ch', 'ญ': 'y',
    'ฎ': 'd', 'ฏ': 't', 'ฐ': 'th', 'ฑ': 'th', 'ฒ': 'th', 'ณ': 'n',
    'ด': 'd', 'ต': 't', 'ถ': 'th', 'ท': 'th', 'ธ': 'th', 'น': 'n',
    'บ': 'b', 'ป': 'p', 'ผ': 'ph', 'ฝ': 'f', 'พ': 'ph', 'ฟ': 'f', 'ภ': 'ph', 'ม': 'm',
    'ย': 'y', 'ร': 'r', 'ฤ': 'rue', 'ล': 'l', 'ฦ': 'lue',
    'ว': 'w', 'ศ': 's', 'ษ': 's', 'ส': 's', 'ห': 'h', 'ฬ': 'l', 'อ': 'o', 'ฮ': 'h',
    # Vowels (independent form)
    'ะ': 'a', 'ั': 'a', 'า': 'a', 'ำ': 'am',
    'ิ': 'i', 'ี': 'i', 'ึ': 'ue', 'ื': 'ue', 'ุ': 'u', 'ู': 'u',
    'เ': 'e', 'แ': 'ae', 'โ': 'o', 'ใ': 'ai', 'ไ': 'ai',
    'ฯ': '...', 'ๆ': '2', '๏': '...',
    # Numbers (convert to Arabic numerals)
    '๐': '0', '๑': '1', '๒': '2', '๓': '3', '๔': '4',
    '๕': '5', '๖': '6', '๗': '7', '๘': '8', '๙': '9',
    # Tone marks and other diacritics (remove them for simplicity)
    '่': '', '้': '', '๊': '', '๋': '',
    '์': '', 'ํ': '', 'ั': '', 'ิ': 'i', 'ี': 'i', 'ึ': 'ue', 'ื': 'ue',
    'ุ': 'u', 'ู': 'u', 'ๅ': '',
}


def transliterate(text: str) -> str:
    """
    Transliterate non-Latin characters to Latin.
    Supports Cyrillic and Thai scripts.

    Args:
        text: Text that may contain Cyrillic or Thai characters

    Returns:
        Transliterated text with only ASCII characters
    """
    result = []
    for char in text:
        if char in CYRILLIC_TO_LATIN:
            result.append(CYRILLIC_TO_LATIN[char])
        elif char in THAI_TO_LATIN:
            result.append(THAI_TO_LATIN[char])
        else:
            result.append(char)
    return ''.join(result)


def display_with_transliteration(text: str, country: str = "unknown") -> str:
    """
    Display text with transliteration if it contains non-ASCII characters.

    Args:
        text: Original text
        country: Country code to determine proper transliteration method

    Returns:
        "Original (Transliterated)" for non-Latin scripts, just original for Latin
    """
    # Check if text contains non-ASCII characters
    has_non_ascii = any(ord(char) > 127 for char in text)

    if not has_non_ascii:
        return text

    # Get transliterated version using centralized function
    transliterated = translate(text, country)

    # If transliteration failed or returned same text, show only original
    if transliterated == text:
        return text

    # Show both original and transliteration
    return f"{text} ({transliterated})"


def display_name_with_transliteration(name: str, surname: str, country: str = "unknown") -> str:
    """
    Display full name with transliteration if it contains non-ASCII characters.

    Args:
        name: First name
        surname: Surname(s)
        country: Country code for proper transliteration

    Returns:
        Full name with transliteration if needed
    """
    full_name = f"{name} {surname}"
    return display_with_transliteration(full_name, country)


def translate(text: str, country: str) -> str:
    """
    Centralized transliteration function for all countries.
    Uses appropriate library based on country's writing system.

    Args:
        text: Text to transliterate (name, surname, etc.)
        country: Country code (lowercase, e.g., 'thailand', 'china', 'russia')

    Returns:
        Transliterated text in Latin alphabet

    Note:
        - Returns original text if country uses Latin alphabet
        - Returns original text if required library is not available
        - Falls back to unidecode for unsupported scripts
    """
    country = country.lower().strip()

    # Countries that use Latin alphabet - return as-is
    latin_countries = {
        'spain', 'argentina', 'australia', 'belgium', 'brazil',
        'france', 'germany', 'italy', 'mexico', 'netherlands',
        'poland', 'portugal', 'sweden', 'turkey', 'uk', 'usa',
        'vietnam'  # Uses Latin with diacritics
    }

    if country in latin_countries:
        return text

    # Check if text is already in Latin alphabet (no transliteration needed)
    if text.isascii():
        return text

    # Country-specific transliteration using appropriate libraries
    try:
        # THAILAND - Thai script (ไทย)
        if country == 'thailand':
            if PYTHAINLP_AVAILABLE:
                # Use pythainlp for proper RTGS transliteration
                return thai_romanize(text, engine='royin')
            else:
                # Fallback: return original (better than broken transliteration)
                return text

        # CHINA - Chinese characters (汉字)
        elif country == 'china':
            if PYPINYIN_AVAILABLE:
                # Use pypinyin for Pinyin transliteration
                pinyin_list = lazy_pinyin(text, style=Style.NORMAL)
                return ' '.join(pinyin_list).title()
            else:
                # Fallback to unidecode
                if UNIDECODE_AVAILABLE:
                    return unidecode(text)
                return text

        # JAPAN - Japanese (Kanji/Hiragana/Katakana)
        elif country == 'japan':
            if CUTLET_AVAILABLE:
                # Use cutlet for Romaji transliteration
                try:
                    return katsu.romaji(text)
                except:
                    pass
            # Fallback to unidecode
            if UNIDECODE_AVAILABLE:
                return unidecode(text)
            return text

        # RUSSIA - Cyrillic (Кириллица)
        elif country == 'russia':
            if TRANSLITERATE_AVAILABLE:
                # Use transliterate library for proper Russian romanization
                try:
                    return translit(text, 'ru', reversed=True)
                except:
                    pass
            # Fallback to manual Cyrillic map
            return transliterate(text)

        # GREECE - Greek alphabet (Ελληνικά)
        elif country == 'greece':
            if TRANSLITERATE_AVAILABLE:
                # Use transliterate library for Greek
                try:
                    return translit(text, 'el', reversed=True)
                except:
                    pass
            # Fallback to unidecode
            if UNIDECODE_AVAILABLE:
                return unidecode(text)
            return text

        # INDIA - Multiple scripts (but names usually pre-romanized)
        elif country == 'india':
            # Indian names are typically already romanized in international contexts
            # If not ASCII, use unidecode as fallback
            if UNIDECODE_AVAILABLE:
                return unidecode(text)
            return text

        # UNKNOWN COUNTRY - fallback to unidecode
        else:
            if UNIDECODE_AVAILABLE:
                return unidecode(text)
            return text

    except Exception as e:
        # If any error occurs, fallback to unidecode or return original
        try:
            if UNIDECODE_AVAILABLE:
                return unidecode(text)
        except:
            pass
        return text


def calculate_time_ago(date_str: str) -> str:
    """
    Calculate time elapsed from a date string to now.

    Args:
        date_str: Date in DD/MM/YYYY, MM/DD/YYYY, or YYYY/MM/DD format

    Returns:
        String like "(2 years ago)" or "(6 months ago)"
    """
    try:
        parts = date_str.split('/')

        if len(parts) != 3:
            return ""

        # Try to detect format
        # YYYY/MM/DD: year is 4 digits and first
        if len(parts[0]) == 4:
            year, month, day = map(int, parts)
        # DD/MM/YYYY or MM/DD/YYYY: year is 4 digits and last
        elif len(parts[2]) == 4:
            # If first part > 12, it's DD/MM/YYYY
            if int(parts[0]) > 12:
                day, month, year = map(int, parts)
            # If second part > 12, it's MM/DD/YYYY
            elif int(parts[1]) > 12:
                month, day, year = map(int, parts)
            # Ambiguous - assume DD/MM/YYYY
            else:
                day, month, year = map(int, parts)
        else:
            return ""

        past_date = datetime(year, month, day)
        now = datetime.now()

        # Calculate difference
        diff = now - past_date
        years = diff.days // 365
        months = (diff.days % 365) // 30

        if years > 0:
            if years == 1:
                return "(1 year ago)"
            else:
                return f"({years} years ago)"
        elif months > 0:
            if months == 1:
                return "(1 month ago)"
            else:
                return f"({months} months ago)"
        else:
            days = diff.days
            if days == 1:
                return "(1 day ago)"
            else:
                return f"({days} days ago)"
    except Exception as e:
        return ""


@dataclass
class Identity:
    """
    Represents a synthetic identity.

    Attributes:
        country: Country code (e.g., 'spain', 'russia')
        gender: Gender ('male' or 'female')
        first_name: First name
        surnames: List of surnames
        full_name: Complete formatted name
        date_of_birth: Birth date in country-specific format
        age: Age in years
        city: City of residence
        nearby_town: Nearby town (optional)
        job: Occupation
        hobbies: List of hobbies
        phone: Phone number with country code
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
        hair_color: Hair color
        eye_color: Eye color
        skin_tone: Skin tone
        email: Email address
        website: Personal website
        postal_code: Postal/ZIP code
        religion: Religious affiliation
        email_status: Status of email ("Activated" or "Inactivated")
        previous_job: Previous job if unemployed/retired (optional)
        family: Family information dict with keys:
            - marital_status: 'Single', 'Married', 'Divorced', 'Girlfriend', 'Boyfriend'
            - partner: Dict with 'name', 'gender', 'start_date', 'marriage_date' (if applicable)
            - relationship_history: List of past relationships (for singles, divorced, etc.)
            - ex_partners: List of dicts for multiple divorces/relationships
            - father: Dict with 'name', 'surname', 'deceased' (bool), 'birth_date', 'death_date', 'age_at_death', 'cause_of_death'
            - mother: Dict with 'name', 'surname', 'deceased' (bool), 'birth_date', 'death_date', 'age_at_death', 'cause_of_death'
            - siblings: List of dicts with 'name', 'gender', 'surname', 'deceased' (bool), 'birth_date', 'death_date', 'age_at_death', 'cause_of_death'
            - children: List of dicts with 'name', 'gender', 'surname', 'deceased' (bool), 'birth_date', 'death_date', 'age_at_death', 'cause_of_death', 'from_marriage' (int, which marriage)
        notes: List of user notes
    """
    country: str
    gender: str
    first_name: str
    surnames: List[str]
    full_name: str
    date_of_birth: str
    age: int
    city: str
    nearby_town: Optional[str]
    postal_code: Optional[str]
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
    religion: str
    email_status: str = "Inactivated"  # "Activated" or "Inactivated"
    previous_job: Optional[str] = None  # Previous job if unemployed/retired
    social_class: str = "middle"  # Social class: low, middle, upper-middle, high
    salary: Optional[int] = None  # Annual salary in local currency (or pension if retired)
    previous_salary: Optional[int] = None  # Salary from previous job (for unemployed/retired)
    education: Optional[str] = None  # Education level and field
    languages: Optional[List[Dict[str, str]]] = None  # Languages with levels and certifications
    work_experience: Optional[Dict[str, Any]] = None  # Current and previous work experience details
    family: Optional[Dict[str, Any]] = None
    considerations: str = ""  # Cultural considerations for the country
    regional_characteristics: Optional[List[str]] = None  # Regional/historical characteristics
    status: str = "Created"  # Status: Created (new identity), Recovered (panic mode recovery)
    notes: List[str] = None

    def __post_init__(self):
        """Initialize default values for optional fields."""
        if self.notes is None:
            self.notes = []
        if self.family is None:
            self.family = {
                "marital_status": "Single",
                "partner": None,
                "ex_partner": None,  # Legacy - kept for compatibility
                "ex_partners": [],  # New: list of all ex-partners
                "relationship_history": [],  # For singles with past relationships
                "father": None,
                "mother": None,
                "siblings": [],
                "children": []
            }

    def to_dict(self) -> dict:
        """Convert identity to dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert identity to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def to_str_box(self) -> str:
        """
        Generate a human-readable string representation in a box format.
        Includes colors and formatting for terminal display.

        Returns:
            Formatted string with box drawing characters and ANSI colors
        """
        def pad_line(label: str, value: str, color_start: str = "", color_end: str = "") -> str:
            """
            Pad a line to exact width, handling ANSI color codes.

            Args:
                label: Label text (e.g., "Full Name:       ")
                value: Value text
                color_start: ANSI color code for value
                color_end: ANSI reset code

            Returns:
                Padded line with proper spacing
            """
            import re
            def strip_ansi(s):
                return re.sub(r'\x1b\[[0-9;]*m', '', s)
            visible = f"{label}{value}"
            visible_len = wcswidth(strip_ansi(visible))
            padding_needed = CONTENT_WIDTH - visible_len
            if padding_needed < 0:
                padding_needed = 0
            if color_start and color_end:
                return f"║ {label}{color_start}{value}{color_end}{' ' * (padding_needed + 3)}║"
            else:
                return f"║ {label}{value}{' ' * (padding_needed + 3)}║"

        # Format hobbies with line wrapping
        hobbies_str = ", ".join(self.hobbies)
        max_hobby_line = 70
        hobby_lines = []
        while hobbies_str:
            if len(hobbies_str) > max_hobby_line:
                split_idx = hobbies_str.rfind(",", 0, max_hobby_line)
                if split_idx == -1:
                    split_idx = max_hobby_line
                hobby_lines.append(hobbies_str[:split_idx].strip())
                hobbies_str = hobbies_str[split_idx+1:].strip()
            else:
                hobby_lines.append(hobbies_str)
                hobbies_str = ""

        # Build formatted lines
        # Display names with transliteration if non-ASCII (e.g., "Имя (Imya)")
        display_name = display_with_transliteration(self.full_name, self.country)
        name_line = pad_line("Full Name:       ", display_name, BOLD + YELLOW, RESET)
        gender_line = pad_line("Gender:          ", self.gender.capitalize())
        dob_text = f"{self.date_of_birth} ({self.age} years old)"
        dob_line = pad_line("Date of Birth:   ", dob_text)

        # Physical characteristics
        physical_text = f"{self.height_cm}cm, {self.weight_kg}kg"
        physical_line = pad_line("Physical:        ", physical_text)
        skin_line = pad_line("Skin:            ", self.skin_tone)
        hair_line = pad_line("Hair:            ", self.hair_color)
        eyes_line = pad_line("Eyes:            ", self.eye_color)

        # Religion
        religion_line = pad_line("Religion:        ", self.religion, BOLD + WHITE, RESET)

        # Location and contact
        display_city = display_with_transliteration(self.city, self.country)
        location_text = f"{display_city}, {RED}{self.country.upper()}{RESET}"
        location_line = pad_line("Location:        ", location_text)

        # Postal code
        postal_text = self.postal_code if self.postal_code else 'N/A'
        postal_line = pad_line("Postal Code:     ", postal_text, BOLD + WHITE, RESET)

        display_nearby = display_with_transliteration(self.nearby_town, self.country) if self.nearby_town else 'N/A'
        nearby_line = pad_line("Nearby:          ", display_nearby, BOLD + YELLOW, RESET)

        # Job display - always show both current and previous
        current_job_line = pad_line("Current Job:     ", self.job)

        # Build current job time immediately after job title
        current_job_time_line = ""
        if self.work_experience:
            exp = self.work_experience
            if exp.get("current_job") == "Retired":
                start_date = exp.get("start_date", "N/A")
                time_ago = calculate_time_ago(start_date)
                current_job_time_line = pad_line("                 ", f"Retired since {start_date} {time_ago}", BOLD + WHITE, RESET) + "\n"
            elif exp.get("current_job") == "Unemployed":
                months = exp.get("months_unemployed", 0)
                current_job_time_line = pad_line("                 ", f"For {months} months", BOLD + RED, RESET) + "\n"
            elif exp.get("current_job") and exp.get("start_date"):
                start_date = exp.get("start_date")
                time_ago = calculate_time_ago(start_date)
                current_job_time_line = pad_line("                 ", f"{start_date} - Present {time_ago}", BOLD + YELLOW, RESET) + "\n"

        # Previous Job: Show from previous_job field OR from work_experience
        previous_job_value = self.previous_job if self.previous_job else "None"

        # If work_experience has previous positions, use the most recent one
        if self.work_experience and self.work_experience.get("previous_positions"):
            prev_positions = self.work_experience["previous_positions"]
            if prev_positions and len(prev_positions) > 0:
                # Use the first (most recent) previous position
                previous_job_value = prev_positions[0].get("job", previous_job_value)

        previous_job_line = pad_line("Previous Job:    ", previous_job_value, BOLD + WHITE, RESET)

        # Social class and salary
        social_class_display = self.social_class.replace('-', '-').title()  # Format: "Upper-Middle"
        social_class_line = pad_line("Social Class:    ", social_class_display, BOLD + WHITE, RESET)

        # Salary/Pension and Previous Salary display
        salary_line = ""
        previous_salary_line = ""

        if self.salary or self.previous_salary:
            # Get currency symbol from country rules
            from pathlib import Path
            import config
            rules_path = config.DATA_DIR / "countries" / self.country / "rules.txt"
            country_rules = CountryRules(rules_path)
            currency_symbol = country_rules.get_currency_symbol()

            # For retired: show pension and what they earned before
            if self.job == "Retired" and self.salary:
                pension_formatted = f"{currency_symbol}{self.salary:,}"
                salary_line = pad_line("Pension (Annual):", pension_formatted, BOLD + YELLOW, RESET) + "\n"

                if self.previous_salary:
                    prev_formatted = f"{currency_symbol}{self.previous_salary:,}"
                    previous_salary_line = pad_line("Prev. Salary:    ", prev_formatted, BOLD + WHITE, RESET) + "\n"

            # For unemployed: show what they used to earn
            elif self.job == "Unemployed" and self.previous_salary:
                prev_formatted = f"{currency_symbol}{self.previous_salary:,}"
                previous_salary_line = pad_line("Prev. Salary:    ", prev_formatted, BOLD + WHITE, RESET) + "\n"

            # For currently employed: show current salary
            elif self.salary:
                salary_formatted = f"{currency_symbol}{self.salary:,}"
                salary_line = pad_line("Salary (Annual): ", salary_formatted, BOLD + YELLOW, RESET) + "\n"

        phone_line = pad_line("Phone:           ", self.phone, BOLD + YELLOW, RESET)
        email_line = pad_line("Email:           ", self.email, BOLD + RED, RESET)

        # Calculate inbox URL
        local_part = self.email.split('@')[0]
        domain = self.email.split('@')[1]
        inbox_url = f"https://www.fakemailgenerator.com/#/{domain}/{local_part}/"

        # Handle long inbox URLs with line wrapping
        inbox_label = "Inbox URL:       "
        if len(inbox_label + inbox_url) <= CONTENT_WIDTH:
            inbox_line = pad_line(inbox_label, inbox_url, BOLD + WHITE, RESET)
        else:
            first_part_len = CONTENT_WIDTH - len(inbox_label)
            inbox_line = pad_line(inbox_label, inbox_url[:first_part_len], BOLD + WHITE, RESET) + "\n"
            inbox_line += pad_line("                 ", inbox_url[first_part_len:], BOLD + WHITE, RESET)

        # Email status with color coding
        status_color = BOLD + YELLOW if self.email_status == "Activated" else BOLD + RED
        email_status_line = pad_line("Email Status:    ", self.email_status, status_color, RESET)

        # Build hobbies block
        hobbies_block = ""
        for i, line in enumerate(hobby_lines):
            if i == 0:
                hobbies_block += pad_line("Hobbies:         ", line) + "\n"
            else:
                hobbies_block += pad_line("                 ", line) + "\n"

        # Build education block
        education_block = ""
        if self.education:
            education_block += pad_line("Education:       ", self.education, BOLD + WHITE, RESET) + "\n"

        # Build languages block
        languages_block = ""
        if self.languages and len(self.languages) > 0:
            for i, lang_info in enumerate(self.languages):
                lang = lang_info.get("language", "Unknown")
                level = lang_info.get("level", "Unknown")
                cert = lang_info.get("certification", "None")

                # Format: Language (Level) - Certification
                if cert == "None":
                    lang_text = f"{lang} ({level})"
                else:
                    lang_text = f"{lang} ({level}) - {cert}"

                if i == 0:
                    languages_block += pad_line("Languages:       ", lang_text, BOLD + WHITE, RESET) + "\n"
                else:
                    languages_block += pad_line("                 ", lang_text, WHITE, RESET) + "\n"

        # Build previous job dates block (if applicable)
        prev_job_dates_block = ""
        if self.work_experience:
            exp = self.work_experience
            prev_positions = exp.get("previous_positions")
            if prev_positions and len(prev_positions) > 0:
                # Show dates and reason for most recent previous position
                prev = prev_positions[0]
                start_date = prev.get("start_date", "N/A")
                end_date = prev.get("end_date", "N/A")
                reason = prev.get("termination_reason", "N/A")

                # Calculate duration worked (years/months)
                try:
                    from datetime import datetime
                    # Parse dates (DD/MM/YYYY format)
                    if '/' in start_date and '/' in end_date:
                        start_parts = start_date.split('/')
                        end_parts = end_date.split('/')

                        start_dt = datetime(int(start_parts[2]), int(start_parts[1]), int(start_parts[0]))
                        end_dt = datetime(int(end_parts[2]), int(end_parts[1]), int(end_parts[0]))

                        # Calculate difference
                        diff = end_dt - start_dt
                        years = diff.days // 365
                        months = (diff.days % 365) // 30

                        if years > 0:
                            if months > 0:
                                duration_text = f"Worked {years} year{'s' if years > 1 else ''} and {months} month{'s' if months > 1 else ''}"
                            else:
                                duration_text = f"Worked {years} year{'s' if years > 1 else ''}"
                        elif months > 0:
                            duration_text = f"Worked {months} month{'s' if months > 1 else ''}"
                        else:
                            days = diff.days
                            duration_text = f"Worked {days} day{'s' if days > 1 else ''}"
                    else:
                        duration_text = ""
                except:
                    duration_text = ""

                # Show dates and duration under Previous Job
                prev_job_dates_block += pad_line("                 ", f"{start_date} - {end_date}", BOLD + WHITE, RESET) + "\n"
                if duration_text:
                    prev_job_dates_block += pad_line("                 ", duration_text, WHITE, RESET) + "\n"
                prev_job_dates_block += pad_line("Left because:    ", reason, WHITE, RESET) + "\n"

        # Build family details block - SEPARATE SECTION
        family_block = ""
        if self.family:
            # Father
            if self.family.get("father"):
                father = self.family["father"]
                if isinstance(father, dict):
                    if father.get("deceased"):
                        # Deceased: show birth-death dates and age at death
                        death_date = father.get('death_date', 'N/A')
                        time_ago = calculate_time_ago(death_date) if death_date != 'N/A' else ""
                        father_text = f"{display_name_with_transliteration(father['name'], father['surname'], self.country)} (Deceased)"
                        family_block += pad_line("Father:          ", father_text, BOLD + RED, RESET) + "\n"
                        death_info = f"{father.get('birth_date', 'N/A')} - {death_date} {time_ago} (Died at {father.get('age_at_death', 'N/A')} years old)"
                        family_block += pad_line("                 ", death_info, WHITE, RESET) + "\n"
                        if father.get('cause_of_death'):
                            family_block += pad_line("                 ", f"Cause: {father['cause_of_death']}", WHITE, RESET) + "\n"
                    else:
                        # Living: show birth date and current age
                        father_text = display_name_with_transliteration(father['name'], father['surname'], self.country)
                        current_age = father.get('current_age', 'N/A')
                        family_block += pad_line("Father:          ", father_text, BOLD + WHITE, RESET) + "\n"
                        family_block += pad_line("                 ", f"Alive - {father.get('birth_date', 'N/A')} ({current_age} years old)", WHITE, RESET) + "\n"

            # Mother
            if self.family.get("mother"):
                mother = self.family["mother"]
                if isinstance(mother, dict):
                    if mother.get("deceased"):
                        # Deceased: show birth-death dates and age at death
                        death_date = mother.get('death_date', 'N/A')
                        time_ago = calculate_time_ago(death_date) if death_date != 'N/A' else ""
                        mother_text = f"{display_name_with_transliteration(mother['name'], mother['surname'], self.country)} (Deceased)"
                        family_block += pad_line("Mother:          ", mother_text, BOLD + RED, RESET) + "\n"
                        death_info = f"{mother.get('birth_date', 'N/A')} - {death_date} {time_ago} (Died at {mother.get('age_at_death', 'N/A')} years old)"
                        family_block += pad_line("                 ", death_info, WHITE, RESET) + "\n"
                        if mother.get('cause_of_death'):
                            family_block += pad_line("                 ", f"Cause: {mother['cause_of_death']}", WHITE, RESET) + "\n"
                    else:
                        # Living: show birth date and current age
                        mother_text = display_name_with_transliteration(mother['name'], mother['surname'], self.country)
                        current_age = mother.get('current_age', 'N/A')
                        family_block += pad_line("Mother:          ", mother_text, BOLD + WHITE, RESET) + "\n"
                        family_block += pad_line("                 ", f"Alive - {mother.get('birth_date', 'N/A')} ({current_age} years old)", WHITE, RESET) + "\n"

            # Siblings
            siblings = self.family.get("siblings", [])
            if siblings:
                # Detect twins/triplets (siblings with same age)
                age_counts = {}
                for sib in siblings:
                    age = sib.get('current_age') or sib.get('age_at_death')
                    if age:
                        age_counts[age] = age_counts.get(age, 0) + 1

                for i, sibling in enumerate(siblings):
                    sibling_surnames = sibling.get("surnames")
                    if sibling_surnames and isinstance(sibling_surnames, list):
                        sibling_surname_str = " ".join(sibling_surnames)
                    else:
                        sibling_surname_str = sibling.get("surname", "")

                    # Detect twin/triplet marker
                    sibling_age = sibling.get('current_age') or sibling.get('age_at_death')
                    twin_marker = ""
                    if sibling_age and age_counts.get(sibling_age, 0) == 2:
                        twin_marker = " (Twin)"
                    elif sibling_age and age_counts.get(sibling_age, 0) >= 3:
                        twin_marker = " (Triplet)"

                    if sibling.get("deceased"):
                        # Deceased sibling
                        sibling_text = f"{display_name_with_transliteration(sibling['name'], sibling_surname_str, self.country)} ({sibling['gender']}){twin_marker} (Deceased)".strip()
                        color = BOLD + RED
                    else:
                        # Living sibling
                        sibling_text = f"{display_name_with_transliteration(sibling['name'], sibling_surname_str, self.country)} ({sibling['gender']}){twin_marker}".strip()
                        color = BOLD + YELLOW

                    if i == 0:
                        family_block += pad_line("Siblings:        ", sibling_text, color, RESET) + "\n"
                    else:
                        family_block += pad_line("                 ", sibling_text, color, RESET) + "\n"

                    # Add death/birth info on next line
                    if sibling.get("deceased"):
                        death_date = sibling.get('death_date', 'N/A')
                        time_ago = calculate_time_ago(death_date) if death_date != 'N/A' else ""
                        death_info = f"{sibling.get('birth_date', 'N/A')} - {death_date} {time_ago} (Died at {sibling.get('age_at_death', 'N/A')} years old)"
                        family_block += pad_line("                 ", death_info, YELLOW, RESET) + "\n"
                        if sibling.get('cause_of_death'):
                            family_block += pad_line("                 ", f"Cause: {sibling['cause_of_death']}", YELLOW, RESET) + "\n"
                    else:
                        current_age = sibling.get('current_age', 'N/A')
                        family_block += pad_line("                 ", f"Alive - {sibling.get('birth_date', 'N/A')} ({current_age} years old)", YELLOW, RESET) + "\n"

            # Marital Status
            marital_status = self.family.get("marital_status", "Single")
            family_block += pad_line("Marital Status:  ", marital_status, BOLD + MAGENTA, RESET) + "\n"

            # Current Partner (Married, Girlfriend, Boyfriend)
            if marital_status in ("Married", "Girlfriend", "Boyfriend") and self.family.get("partner"):
                partner = self.family["partner"]
                partner_surname_str = partner.get("surname", "")
                partner_text = f"{display_name_with_transliteration(partner['name'], partner_surname_str, self.country)} ({partner['gender']})"
                family_block += pad_line("Partner:         ", partner_text, BOLD + WHITE, RESET) + "\n"

                # Show birth date and age for partner
                current_age = partner.get('current_age', 'N/A')
                family_block += pad_line("                 ", f"Alive - {partner.get('birth_date', 'N/A')} ({current_age} years old)", WHITE, RESET) + "\n"

                # Show relationship start date
                if partner.get('start_date'):
                    time_ago = calculate_time_ago(partner['start_date'])
                    # Remove parentheses and " ago", then add back properly
                    # calculate_time_ago returns "(2 years ago)"
                    # We want "2024/01/02 (2 years ago)"
                    time_display = time_ago.strip("()").strip()
                    if marital_status == "Married":
                        family_block += pad_line("Marriage Date:   ", f"{partner['start_date']} ({time_display})", BOLD + YELLOW, RESET) + "\n"
                    else:  # Girlfriend/Boyfriend
                        family_block += pad_line("Together since:  ", f"{partner['start_date']} ({time_display})", BOLD + YELLOW, RESET) + "\n"

            # Ex-Partners (for divorced/remarried people)
            ex_partners = self.family.get("ex_partners", [])
            if ex_partners:
                # Show all past marriages
                for i, ex in enumerate(ex_partners, 1):
                    marriage_num = ex.get('marriage_number', i)
                    ex_surname_str = ex.get("surname", "")

                    # Header for each past marriage
                    if len(ex_partners) > 1:
                        family_block += pad_line(f"Marriage #{marriage_num}:", "", BOLD + MAGENTA, RESET) + "\n"

                    # Show ex-partner info
                    if ex.get("deceased"):
                        # Ex-partner is deceased
                        ex_text = f"{display_name_with_transliteration(ex['name'], ex_surname_str, self.country)} ({ex['gender']}) (Deceased)"
                        family_block += pad_line("  Ex-Partner:    ", ex_text, BOLD + RED, RESET) + "\n"
                        death_date = ex.get('death_date', 'N/A')
                        time_ago = calculate_time_ago(death_date) if death_date != 'N/A' else ""
                        death_info = f"{ex.get('birth_date', 'N/A')} - {death_date} {time_ago} (Died at {ex.get('age_at_death', 'N/A')} years old)"
                        family_block += pad_line("                 ", death_info, YELLOW, RESET) + "\n"
                    else:
                        # Ex-partner is alive
                        ex_text = f"{display_name_with_transliteration(ex['name'], ex_surname_str, self.country)} ({ex['gender']})"
                        family_block += pad_line("  Ex-Partner:    ", ex_text, YELLOW, RESET) + "\n"
                        current_age = ex.get('current_age', 'N/A')
                        family_block += pad_line("                 ", f"Alive - {ex.get('birth_date', 'N/A')} ({current_age} years old)", YELLOW, RESET) + "\n"

                    # Show marriage dates and duration
                    if ex.get('marriage_date'):
                        marriage_time_ago = calculate_time_ago(ex['marriage_date'])
                        family_block += pad_line("  Married:       ", f"{ex['marriage_date']} {marriage_time_ago}", WHITE, RESET) + "\n"

                    if ex.get('end_date'):
                        end_time_ago = calculate_time_ago(ex['end_date'])
                        duration_years = ex.get('duration', 0)
                        duration_text = f"{duration_years} years" if duration_years != 1 else "1 year"
                        family_block += pad_line("  Ended:         ", f"{ex['end_date']} {end_time_ago} (Lasted {duration_text})", WHITE, RESET) + "\n"

                    # Show divorce cause
                    if ex.get('divorce_cause'):
                        family_block += pad_line("  Reason:        ", ex['divorce_cause'], BOLD + YELLOW, RESET) + "\n"

            # Relationship History (for singles with past relationships)
            relationship_history = self.family.get("relationship_history", [])
            if relationship_history:
                family_block += pad_line("Past Relations:  ", "", BOLD + MAGENTA, RESET) + "\n"
                for i, rel in enumerate(relationship_history, 1):
                    rel_surname_str = rel.get("surname", "")
                    rel_text = f"{display_name_with_transliteration(rel['name'], rel_surname_str, self.country)} ({rel['gender']})"
                    family_block += pad_line(f"  [{i}] Partner:   ", rel_text, YELLOW, RESET) + "\n"

                    # Show birth date and current age
                    current_age = rel.get('current_age', 'N/A')
                    family_block += pad_line("                 ", f"{rel.get('birth_date', 'N/A')} ({current_age} years old)", YELLOW, RESET) + "\n"

                    # Show relationship dates and duration
                    if rel.get('start_date') and rel.get('end_date'):
                        end_time_ago = calculate_time_ago(rel['end_date'])
                        duration = rel.get('duration', 0)
                        duration_text = f"{duration} years" if duration != 1 else "1 year"
                        family_block += pad_line("      Duration:   ", f"{rel['start_date']} - {rel['end_date']} {end_time_ago} ({duration_text})", WHITE, RESET) + "\n"

                    # Show breakup reason
                    if rel.get('breakup_reason'):
                        family_block += pad_line("      Reason:     ", rel['breakup_reason'], WHITE, RESET) + "\n"

            # Children (grouped by marriage if from multiple marriages)
            children = self.family.get("children", [])
            if children:
                # Check if children are from multiple marriages
                marriages_with_children = set(child.get('from_marriage', 1) for child in children)
                show_marriage_groups = len(marriages_with_children) > 1 and len(ex_partners) > 0

                if show_marriage_groups:
                    # Group children by marriage
                    children_by_marriage = {}
                    for child in children:
                        marriage_num = child.get('from_marriage', 1)
                        if marriage_num not in children_by_marriage:
                            children_by_marriage[marriage_num] = []
                        children_by_marriage[marriage_num].append(child)

                    # Display children grouped by marriage
                    first_group = True
                    for marriage_num in sorted(children_by_marriage.keys()):
                        marriage_children = children_by_marriage[marriage_num]

                        # Show which marriage
                        if first_group:
                            family_block += pad_line("Children:        ", f"From Marriage #{marriage_num}:", BOLD + MAGENTA, RESET) + "\n"
                            first_group = False
                        else:
                            family_block += pad_line("                 ", f"From Marriage #{marriage_num}:", BOLD + MAGENTA, RESET) + "\n"

                        for child in marriage_children:
                            child_surnames = child.get("surnames")
                            if child_surnames and isinstance(child_surnames, list):
                                child_surname_str = " ".join(child_surnames)
                            else:
                                child_surname_str = child.get("surname", "")

                            if child.get("deceased"):
                                child_text = f"  {child['name']} {child_surname_str} ({child['gender']}) (Deceased)".strip()
                                color = BOLD + RED
                            else:
                                child_text = f"  {child['name']} {child_surname_str} ({child['gender']})".strip()
                                color = BOLD + WHITE

                            family_block += pad_line("                 ", child_text, color, RESET) + "\n"

                            # Add death/birth info
                            if child.get("deceased"):
                                death_date = child.get('death_date', 'N/A')
                                death_time_ago = calculate_time_ago(death_date) if death_date != 'N/A' else ""
                                death_info = f"  {child.get('birth_date', 'N/A')} - {death_date} {death_time_ago} (Died at {child.get('age_at_death', 'N/A')} years old)"
                                family_block += pad_line("                 ", death_info, WHITE, RESET) + "\n"
                                if child.get('cause_of_death'):
                                    family_block += pad_line("                 ", f"  Cause: {child['cause_of_death']}", WHITE, RESET) + "\n"
                            else:
                                current_age = child.get('current_age', 'N/A')
                                family_block += pad_line("                 ", f"  Alive - {child.get('birth_date', 'N/A')} ({current_age} years old)", WHITE, RESET) + "\n"
                else:
                    # Display all children together (single marriage or no grouping needed)
                    for i, child in enumerate(children):
                        child_surnames = child.get("surnames")
                        if child_surnames and isinstance(child_surnames, list):
                            child_surname_str = " ".join(child_surnames)
                        else:
                            child_surname_str = child.get("surname", "")

                        if child.get("deceased"):
                            child_text = f"{display_name_with_transliteration(child['name'], child_surname_str, self.country)} ({child['gender']}) (Deceased)".strip()
                            color = BOLD + RED
                        else:
                            child_text = f"{display_name_with_transliteration(child['name'], child_surname_str, self.country)} ({child['gender']})".strip()
                            color = BOLD + WHITE

                        if i == 0:
                            family_block += pad_line("Children:        ", child_text, color, RESET) + "\n"
                        else:
                            family_block += pad_line("                 ", child_text, color, RESET) + "\n"

                        # Add death/birth info on next line
                        if child.get("deceased"):
                            death_date = child.get('death_date', 'N/A')
                            death_time_ago = calculate_time_ago(death_date) if death_date != 'N/A' else ""
                            death_info = f"{child.get('birth_date', 'N/A')} - {death_date} {death_time_ago} (Died at {child.get('age_at_death', 'N/A')} years old)"
                            family_block += pad_line("                 ", death_info, WHITE, RESET) + "\n"
                            if child.get('cause_of_death'):
                                family_block += pad_line("                 ", f"Cause: {child['cause_of_death']}", WHITE, RESET) + "\n"
                        else:
                            current_age = child.get('current_age', 'N/A')
                            family_block += pad_line("                 ", f"Alive - {child.get('birth_date', 'N/A')} ({current_age} years old)", WHITE, RESET) + "\n"

        # Build regional characteristics block
        regional_block = ""
        if self.regional_characteristics and len(self.regional_characteristics) > 0:
            for i, characteristic in enumerate(self.regional_characteristics):
                if i == 0:
                    regional_block += pad_line("Regional:        ", characteristic, BOLD + YELLOW, RESET) + "\n"
                else:
                    regional_block += pad_line("                 ", characteristic, YELLOW, RESET) + "\n"

        # Build notes block
        notes_block = ""
        if self.notes and len(self.notes) > 0:
            for i, note in enumerate(self.notes):
                note_prefix = f"[{i + 1}]"
                if i == 0:
                    notes_block += pad_line(f"Notes {note_prefix}:      ", note, BOLD + WHITE, RESET) + "\n"
                else:
                    notes_block += pad_line(f"      {note_prefix}:      ", note, BOLD + WHITE, RESET) + "\n"
        else:
            notes_block += pad_line("Notes:           ", "Your notes will appear here when you mark them", WHITE, RESET) + "\n"

        # Build website section
        if self.website and self.website not in (None, "None", ""):
            website_line = pad_line("Website:         ", self.website, BOLD + MAGENTA, RESET)
        else:
            website_line = pad_line("Website:         ", "None", BOLD + MAGENTA, RESET)
        website_section = f"{website_line}\n╠{'═'*BOX_WIDTH}╣"

        # Assemble final box with separate sections
        return f"""╔{'═'*BOX_WIDTH}╗
║{BOLD}{'SYNTHETIC IDENTITY'.center(BOX_WIDTH)}{RESET}║
╠{'═'*BOX_WIDTH}╣
{website_section}
{name_line}
{gender_line}
{dob_line}
{religion_line}
{physical_line}
{skin_line}
{hair_line}
{eyes_line}
{location_line}
{postal_line}
{nearby_line}
{current_job_line}
{current_job_time_line}{previous_job_line}
{prev_job_dates_block}{social_class_line}
{salary_line}{previous_salary_line}{education_block}{languages_block}{phone_line}
{email_line}
{inbox_line}
{email_status_line}
{hobbies_block}{regional_block}╠{'═'*BOX_WIDTH}╣
║{BOLD}{'FAMILY DETAILS'.center(BOX_WIDTH)}{RESET}║
╠{'═'*BOX_WIDTH}╣
{family_block}╠{'═'*BOX_WIDTH}╣
║{BOLD}{'NOTES'.center(BOX_WIDTH)}{RESET}║
╠{'═'*BOX_WIDTH}╣
{notes_block}╚{'═'*BOX_WIDTH}╝"""

    def display_considerations_box(self) -> str:
        """Display cultural considerations in a box format with colors."""
        country_name = self.country.upper() if hasattr(self, 'country') else "UNKNOWN"
        
        if not self.considerations or self.considerations.strip() == "":
            # Calculate proper padding for title with ANSI codes
            title_text = "CULTURAL CONSIDERATIONS"
            title_with_color = f"{BOLD}{CYAN}{title_text}{RESET}"
            # Padding = (BOX_WIDTH - len(title_text)) // 2
            left_pad = (BOX_WIDTH - len(title_text)) // 2
            right_pad = BOX_WIDTH - len(title_text) - left_pad
            title_line = f"║{' '*left_pad}{title_with_color}{' '*right_pad}║"
            
            return f"""╔{'═'*BOX_WIDTH}╗
{title_line}
╠{'═'*BOX_WIDTH}╣
║{YELLOW}{'No cultural considerations available for this country.'.ljust(CONTENT_WIDTH)}{RESET}║
╚{'═'*BOX_WIDTH}╝"""

        # Process text: remove markdown, clean up
        text = self.considerations
        text = text.replace('#', '')  # Remove markdown headers
        text = text.replace('**', '')  # Remove markdown bold
        lines = text.split('\n')

        formatted_lines = []
        current_section = None
        first_line = True
        
        for line in lines:
            # Skip the first line if it's the title (already shown in header)
            if first_line:
                first_line = False
                if 'CULTURAL CONSIDERATIONS' in line.upper():
                    continue
            
            line = line.strip()
            if not line:
                formatted_lines.append(("empty", ""))  # Empty line
                continue

            # Detect section headers (lines that end with : or are all caps)
            if line.endswith(':') and len(line) < 60:
                current_section = line
                formatted_lines.append(("header", line))
                continue
            
            # Replace leading dash with spaces for list items
            is_list_item = False
            if line.startswith('-'):
                line = '  ' + line[1:].strip()  # 2 spaces for indent
                is_list_item = True

            # Wrap long lines
            while len(line) > CONTENT_WIDTH:
                # Find last space before width limit
                wrap_pos = line[:CONTENT_WIDTH].rfind(' ')
                if wrap_pos == -1:
                    wrap_pos = CONTENT_WIDTH
                formatted_lines.append(("list" if is_list_item else "text", line[:wrap_pos]))
                remaining = line[wrap_pos:].strip()
                line = ('  ' if is_list_item else '') + remaining
                is_list_item = False  # Only first line gets list marker
            
            if line:
                formatted_lines.append(("list" if is_list_item else "text", line))

        # Build box with title
        title_text = f"CULTURAL CONSIDERATIONS FOR {country_name}"
        # Calculate padding accounting for ANSI codes
        left_pad = (BOX_WIDTH - len(title_text)) // 2
        right_pad = BOX_WIDTH - len(title_text) - left_pad
        title_with_color = f"{BOLD}{CYAN}{title_text}{RESET}"
        title_line = f"║{' '*left_pad}{title_with_color}{' '*right_pad}║"
        
        result = f"╔{'═'*BOX_WIDTH}╗\n"
        result += f"{title_line}\n"
        result += f"╠{'═'*BOX_WIDTH}╣\n"

        for line_type, line_text in formatted_lines:
            # Replace any remaining tabs with spaces
            line_text = line_text.replace('\t', '  ')
            
            if line_type == "empty":
                result += f"║{' '*CONTENT_WIDTH}    ║\n"
            elif line_type == "header":
                # Section headers in bold yellow
                padding_needed = CONTENT_WIDTH - len(line_text)
                result += f"║{BOLD}{YELLOW}{line_text}{RESET}{' '*padding_needed}    ║\n"
            elif line_type == "list":
                # List items in white
                padding_needed = CONTENT_WIDTH - len(line_text)
                result += f"║{WHITE}{line_text}{RESET}{' '*padding_needed}    ║\n"
            else:
                # Regular text in white
                padding_needed = CONTENT_WIDTH - len(line_text)
                result += f"║{WHITE}{line_text}{RESET}{' '*padding_needed}    ║\n"

        result += f"╚{'═'*BOX_WIDTH}╝"
        return result

class CountryRules:
    """
    Parses and stores country-specific generation rules.

    Reads rules.txt from a country directory and provides methods
    to access formatted rule values.
    """

    def __init__(self, rules_path: Path):
        """
        Initialize CountryRules from a rules.txt file.

        Args:
            rules_path: Path to rules.txt file
        """
        self.rules = self._parse_rules(rules_path)

    def _parse_rules(self, rules_path: Path) -> Dict[str, Any]:
        """
        Parse rules.txt file into a dictionary.

        Format:
            key=value
            key=value1,value2,value3  # Lists
            # Comments are ignored

        Args:
            rules_path: Path to rules.txt

        Returns:
            Dictionary of parsed rules
        """
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
        """Get a rule value by key."""
        return self.rules.get(key, default)

    def get_name_order(self) -> List[str]:
        """Get name order as list of components (e.g., ['first', 'surname1', 'surname2'])."""
        order = self.get('name_order', 'first+surname')
        return order.split('+')

    def get_surname_count(self) -> int:
        """Get number of surnames (1 or 2)."""
        return int(self.get('surname_count', '1'))

    def get_date_format(self) -> str:
        """Get date format string (e.g., 'DD/MM/YYYY')."""
        return self.get('date_format', 'DD/MM/YYYY')

    def get_phone_format(self) -> str:
        """Get phone format pattern (e.g., '### ### ###')."""
        return self.get('phone_format', '### ### ###')

    def get_phone_country_code(self) -> str:
        """Get phone country code (e.g., '+34')."""
        return self.get('phone_country_code', '+1')

    def get_phone_length(self) -> int:
        """Get phone number length without country code."""
        return int(self.get('phone_length', '10'))

    def get_phone_prefixes(self) -> List[str]:
        """
        Get mobile phone prefixes only (landlines removed).

        Returns:
            List of mobile prefixes
        """
        all_prefixes = []

        # ONLY mobile prefixes (100% mobile, no landlines)
        mobile_prefixes = self.get('phone_mobile_prefixes')
        if mobile_prefixes:
            if isinstance(mobile_prefixes, list):
                all_prefixes.extend(mobile_prefixes)
            elif isinstance(mobile_prefixes, str):
                all_prefixes.append(mobile_prefixes)

        # Fallback to generic prefixes (assuming they're mobile)
        if not all_prefixes:
            general_prefixes = self.get('phone_prefixes')
            if general_prefixes:
                if isinstance(general_prefixes, list):
                    all_prefixes = general_prefixes
                elif isinstance(general_prefixes, str):
                    all_prefixes = [general_prefixes]

        return all_prefixes if all_prefixes else ['6']

    def get_life_expectancy(self) -> int:
        """Get life expectancy (used for max age)."""
        return int(self.get('life_expectancy', '80'))

    def get_min_age(self) -> int:
        """Get minimum age for generation."""
        return int(self.get('min_age', '18'))

    def get_max_age(self) -> int:
        """Get maximum age (defaults to life expectancy)."""
        max_age = self.get('max_age')
        if max_age:
            return int(max_age)
        return self.get_life_expectancy()

    def _parse_weighted_dict(self, key: str, default: Dict[str, float]) -> Dict[str, float]:
        """
        Parse weighted dictionary from rules (e.g., hair_colors, eye_colors).

        Format: 'Black:35,Brown:30,Blonde:20'

        Args:
            key: Rule key
            default: Default dictionary if not found

        Returns:
            Dictionary with color/tone names and probabilities
        """
        value_str = self.get(key)
        if not value_str:
            return default

        result_dict = {}
        if isinstance(value_str, list):
            # Format: ['Black:35', 'Brown:30', ...]
            for item in value_str:
                if ':' in item:
                    name, prob = item.split(':', 1)
                    result_dict[name.strip()] = float(prob.strip())
                else:
                    result_dict[item.strip()] = 10.0
        elif isinstance(value_str, str):
            # Single string format
            for item in value_str.split(','):
                if ':' in item:
                    name, prob = item.split(':', 1)
                    result_dict[name.strip()] = float(prob.strip())
                else:
                    result_dict[item.strip()] = 10.0

        return result_dict

    def get_hair_colors(self) -> Dict[str, float]:
        """Get dictionary of hair colors with probabilities."""
        default = {'Black': 35, 'Brown': 30, 'Dark Brown': 20, 'Light Brown': 10, 'Blonde': 4, 'Red': 1}
        return self._parse_weighted_dict('hair_colors', default)

    def get_eye_colors(self) -> Dict[str, float]:
        """Get dictionary of eye colors with probabilities."""
        default = {'Brown': 50, 'Dark Brown': 30, 'Light Brown': 10, 'Green': 5, 'Blue': 4, 'Hazel': 1}
        return self._parse_weighted_dict('eye_colors', default)

    def get_skin_tones(self) -> Dict[str, float]:
        """Get dictionary of skin tones with probabilities."""
        default = {'Light': 40, 'Medium': 30, 'Olive': 15, 'Tan': 10, 'Dark': 5}
        return self._parse_weighted_dict('skin_tones', default)

    def get_religions(self) -> Dict[str, float]:
        """Get dictionary of religions with probabilities."""
        default = {'Atheist': 40, 'Christian': 50, 'Agnostic': 8, 'Other': 2}
        return self._parse_weighted_dict('religions', default)

    def get_average_children(self) -> float:
        """Get average number of children."""
        avg_str = self.get('average_children', '2.0')
        return float(avg_str)

    def get_min_children(self) -> int:
        """Get minimum number of children."""
        return int(self.get('min_children', '1'))

    def get_max_children(self) -> int:
        """Get maximum number of children."""
        return int(self.get('max_children', '4'))

    def get_average_siblings(self) -> float:
        """Get average number of siblings."""
        return float(self.get('average_siblings', '1.2'))

    def get_min_siblings(self) -> int:
        """Get minimum number of siblings."""
        return int(self.get('min_siblings', '0'))

    def get_max_siblings(self) -> int:
        """Get maximum number of siblings."""
        return int(self.get('max_siblings', '3'))

    def get_sibling_probability(self) -> float:
        """Get probability of having siblings (percentage)."""
        return float(self.get('sibling_probability', '50.0'))

    def get_unemployment_rate(self) -> float:
        """Get unemployment rate percentage."""
        return float(self.get('unemployment_rate', '10.0'))

    def get_jobless_rate(self) -> float:
        """Get jobless rate percentage (not looking for work)."""
        return float(self.get('jobless_rate', '2.0'))

    def get_death_probability(self, family_member_type: str, age_bucket: str) -> float:
        """
        Get death probability for a family member based on identity's age bucket.

        Args:
            family_member_type: 'parents', 'children', or 'siblings'
            age_bucket: Age bucket of the identity (not the family member)

        Returns:
            Death probability as percentage (0-100)
        """
        key = f'death_prob_{family_member_type}_{age_bucket}'
        return float(self.get(key, '0.0'))

    def get_social_classes(self) -> Dict[str, float]:
        """Get dictionary of social classes with probabilities."""
        default = {'low': 25, 'middle': 50, 'upper-middle': 20, 'high': 5}
        return self._parse_weighted_dict('social_classes', default)

    def get_salary_range(self, social_class: str) -> tuple:
        """
        Get salary range for a social class.

        Args:
            social_class: The social class (low, middle, upper-middle, high)

        Returns:
            Tuple of (min_salary, max_salary)
        """
        key = f'salary_{social_class}'
        value = self.get(key)

        if value:
            if isinstance(value, list):
                # Format: ['12000', '22000']
                return (int(value[0]), int(value[1]))
            elif isinstance(value, str):
                # Format: '12000,22000' (already parsed as list by _parse_rules)
                # But in case it's not parsed yet
                parts = value.split(',')
                return (int(parts[0]), int(parts[1]))

        # Default ranges based on class
        defaults = {
            'low': (15000, 25000),
            'middle': (25000, 50000),
            'upper-middle': (50000, 100000),
            'high': (100000, 300000)
        }
        return defaults.get(social_class, (20000, 40000))

    def get_currency_symbol(self) -> str:
        """Get currency symbol (e.g., '€', '$')."""
        return self.get('currency_symbol', '$')

    def get_currency_code(self) -> str:
        """Get currency code (e.g., 'EUR', 'USD')."""
        return self.get('currency_code', 'USD')

    def get_pension_range(self, social_class: str) -> tuple:
        """
        Get pension range for a social class.

        Args:
            social_class: The social class (low, middle, upper-middle, high)

        Returns:
            Tuple of (min_pension, max_pension)
        """
        key = f'pension_{social_class}'
        value = self.get(key)

        if value:
            if isinstance(value, list):
                return (int(value[0]), int(value[1]))
            elif isinstance(value, str):
                parts = value.split(',')
                return (int(parts[0]), int(parts[1]))

        # Default ranges based on class (60-70% of salary range)
        defaults = {
            'low': (8000, 16000),
            'middle': (15000, 30000),
            'upper-middle': (28000, 55000),
            'high': (50000, 120000)
        }
        return defaults.get(social_class, (12000, 24000))

    def get_female_fertility_min_age(self) -> int:
        """Get minimum age for female fertility."""
        return int(self.get('female_fertility_min_age', '15'))

    def get_female_fertility_max_age(self) -> int:
        """Get maximum age for female fertility."""
        return int(self.get('female_fertility_max_age', '45'))

    @property
    def min_languages(self) -> int:
        """Get minimum number of languages (including native)."""
        return int(self.get('min_languages', '1'))

    @property
    def max_languages(self) -> int:
        """Get maximum number of languages (including native)."""
        return int(self.get('max_languages', '4'))

    @property
    def available_languages(self) -> Dict[str, float]:
        """
        Get available languages with probabilities.

        Format in rules.txt: available_languages=English:70,French:30,German:15

        Returns:
            Dictionary with language names and probabilities
        """
        default = {'English': 70}
        return self._parse_weighted_dict('available_languages', default)

    @property
    def language_level_basic(self) -> int:
        """Get probability for basic language level (percentage)."""
        return int(self.get('language_level_basic', '30'))

    @property
    def language_level_intermediate(self) -> int:
        """Get probability for intermediate language level (percentage)."""
        return int(self.get('language_level_intermediate', '50'))

    @property
    def language_level_advanced(self) -> int:
        """Get probability for advanced language level (percentage)."""
        return int(self.get('language_level_advanced', '20'))

    def get_parent_min_age_gap(self) -> int:
        """Get minimum age gap between parent and child."""
        return int(self.get('parent_min_age_gap', '18'))

    def get_parent_max_age_gap(self) -> int:
        """Get maximum age gap between parent and child."""
        return int(self.get('parent_max_age_gap', '45'))
