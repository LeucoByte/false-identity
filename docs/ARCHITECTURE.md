# Technical Architecture

## System Overview

False Identity Generator is built on a modular architecture designed for extensibility, maintainability, and data-driven configuration.

## Core Components

### 1. Generator Module (`src/generator.py`)

**Purpose**: Core identity generation engine

**Key Classes**:
- `IdentityGenerator`: Main orchestrator for identity creation

**Key Methods**:
- `generate()`: Main entry point for identity generation
- `_generate_family()`: Family structure generation with fertility constraints
- `_generate_work_experience()`: Employment history with coherent timelines
- `_generate_physical_characteristics()`: Age-appropriate physical traits
- `_get_job_for_age()`: Age-appropriate job assignment
- `_generate_death_info_for_parent()`: Realistic parent death scenarios

**Lines of Code**: ~2,400 (after modularization)

### 2. Data Loader Module (`src/data_loader.py`)

**Purpose**: File I/O and data caching layer

**Key Classes**:
- `DataLoader`: Handles all data loading with caching

**Key Features**:
- Caching system for performance
- Age-based data selection (buckets: very_young, young_adults, adults, middle_aged, older_adults, seniors, elderly)
- Gender-aware data loading
- Country-specific and global data support

**Methods** (20+ public methods):
- `load_names()`, `load_surnames()`: Name data by age/gender
- `load_jobs()`: Jobs filtered by gender and social class
- `load_regional_characteristics()`: Age-filtered historical/cultural traits
- `load_rules()`: Country configuration
- `load_death_causes()`: Age-appropriate death causes

**Lines of Code**: ~600

### 3. Models Module (`src/models.py`)

**Purpose**: Data structures and display logic

**Key Classes**:
- `Identity`: Main data structure (dataclass)
- `CountryRules`: Configuration wrapper

**Key Features**:
- Display formatting with colored output
- Twin/triplet detection in families
- Time calculation utilities
- Box drawing for CLI interface

**Lines of Code**: ~800

### 4. UI Modules (`src/ui/`)

**Components**:
- `display.py`: Terminal UI formatting
- `menus.py`: Interactive menu systems

### 5. Storage Module (`src/storage.py`)

**Purpose**: Identity persistence and retrieval

**Features**:
- JSON serialization
- File-based storage
- Identity search and management

## Data Flow

```
User Input
    ↓
main.py → IdentityGenerator
    ↓
generate() method
    ↓
    ├→ DataLoader.load_rules() → Country configuration
    ├→ DataLoader.load_names() → Age/gender-appropriate names
    ├→ _generate_family() → Family structure
    │   ├→ Parent generation (age constraints)
    │   ├→ Sibling generation (fertility validation)
    │   └→ Children generation (fertility validation)
    ├→ _get_job_for_age() → Age-appropriate employment
    ├→ _generate_work_experience() → Employment history
    ├→ _generate_physical_characteristics() → Physical traits
    └→ load_regional_characteristics() → Cultural context
    ↓
Identity object
    ↓
Storage.save() → JSON file
```

## Key Algorithms

### Age-Based Data Selection

```python
AGE_BUCKETS = [
    "very_young",      # min_age to min_age+5
    "young_adults",    # min_age+5 to min_age+16
    "adults",          # min_age+16 to 50
    "middle_aged",     # 50 to 65
    "older_adults",    # 65 to life_expectancy
    "seniors",         # Beyond life_expectancy
    "elderly"          # Oldest segment
]
```

Data files are organized by bucket for realistic name, hobby, and characteristic selection.

### Parent Age Validation

**Constraints**:
1. `parent_age = identity_age + random(parent_min_gap, parent_max_gap)`
2. `parent_age <= life_expectancy + random(0,5)` (realistic cap)
3. Death timing based on identity age:
   - Identity 70+: parent died 10-30 years ago
   - Identity 50-70: parent died 5-20 years ago
   - Identity 35-50: parent died 0-15 years ago

### Sibling Age Calculation with Fertility Constraints

```python
# Mother's current age (or age at death)
mother_age = mother['current_age'] or mother['age_at_death']

# Valid sibling age range
max_sibling_age = mother_age - fertility_min  # Mother was AT LEAST fertility_min
min_sibling_age = max(1, mother_age - fertility_max)  # Mother was AT MOST fertility_max

# Also respect ±15 years from identity age for realism
max_sibling_age = min(max_sibling_age, identity_age + 15)
min_sibling_age = max(min_sibling_age, max(1, identity_age - 15))
```

**Result**: No impossible scenarios (e.g., mother giving birth at age 8)

### Twin/Triplet Detection

```python
# Allow same age with 15% probability
if random.random() < 0.15 and sibling_count_at_age < 3:
    # Assign same age as existing sibling
    used_ages[age] += 1
```

Display logic detects multiples by counting siblings with identical ages.

### Job Age Filtering

```python
def _filter_jobs_by_age(jobs, age, age_requirements):
    """Filter jobs to only those person is old enough for."""
    filtered = []
    for job in jobs:
        min_age = age_requirements.get(job, 18)  # Default: 18
        if age >= min_age:
            filtered.append(job)
    return filtered
```

**Safeguard**: Persons under 18 are automatically assigned "Student" status.

## Configuration System

### Country Rules (`data/countries/{country}/rules.txt`)

Key-value pairs controlling generation logic:

```ini
# Demographics
min_age=18
max_age=83
life_expectancy=83

# Fertility
female_fertility_min_age=15
female_fertility_max_age=45
parent_min_age_gap=18
parent_max_age_gap=45

# Probabilities
death_prob_parents_elderly=95
unemployment_rate=13.5

# Formats
date_format=DD/MM/YYYY
phone_format=### ## ## ##
```

### Data File Formats

**Names** (`data/countries/{country}/names/{gender}/{age_bucket}.txt`):
```
María
José
Carmen
```

**Regional Characteristics** (`data/countries/{country}/regional_characteristics.txt`):
```
characteristic_text|min_age|max_age|gender|probability
Remembers the 2004 Madrid train bombings|27|999|both|0.7
```
- `min_age`: Person must be THIS age NOW to have this characteristic
- Calculated so person was 5-7+ years old when event occurred (realistic memory)

**Jobs** (`data/global/jobs/{gender}/{social_class}.txt`):
```
Software Engineer
Nurse
Teacher
```

**Age Requirements** (`data/global/jobs/age_requirements.txt`):
```
Nurse:22
Lawyer:24
Pharmacy Technician:21
```

## Performance Optimizations

1. **Caching**: `DataLoader` caches all loaded files in `_cache` dict
2. **Lazy Loading**: Data only loaded when needed
3. **Random Sampling**: Efficient selection from weighted distributions
4. **Minimal File I/O**: Read files once, use repeatedly

## Error Handling

**Data Validation**:
- Age range checks before all operations
- Fallback to defaults if data files missing
- Safe random selection with bounds checking

**Edge Case Handling**:
- Empty job lists → fallback to "Student"
- Invalid date ranges → swap min/max or adjust
- Missing data files → use hardcoded defaults

## Extensibility

### Adding a New Country

1. Create directory: `data/countries/{country}/`
2. Add configuration: `rules.txt`
3. Add name files: `names/{gender}/{age_bucket}.txt`
4. Add surnames: `surnames/{gender}.txt` (if gendered) or `surnames.txt`
5. Add cities: `cities.txt`
6. Add regional characteristics: `regional_characteristics.txt`
7. Mark as complete: Set `finished=true` in `rules.txt`

### Adding New Data Fields

1. Extend `Identity` dataclass in `models.py`
2. Add generation method in `generator.py`
3. Add data files in appropriate locations
4. Update `DataLoader` with loading method
5. Update display logic in `models.py`

## Testing

### Test Suite (`test_features.py`)

**Validates**:
- Age ranges (18-83 for Spain)
- Phone formats (mobile only: +34 6XX or 7XX)
- Hobbies presence
- Language coherence (university graduates have B1+ English)
- Parent death validation (if >life_expectancy, must be deceased)
- Fertility constraints (mother age at birth: 15-45)
- Regional characteristics age-appropriateness

**Success Rate**: 98-100% (50 identity test)

## Security Considerations

**Data Privacy**:
- All generated data is synthetic
- No real person data included
- Random seeds ensure unpredictability

**Abuse Prevention**:
- Legal disclaimers
- No built-in document generation
- Educational purpose markers
