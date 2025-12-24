# Spain Implementation - Complete Documentation

## Overview

The Spain dataset is the **first fully implemented country** in the False Identity Generator system, featuring comprehensive demographic data, cultural characteristics, and realistic generation rules.

## Completion Status

✅ **COMPLETED** - All components implemented and tested
📊 **Test Success Rate**: 96-100% (48-50/50 identities pass validation)

## Dataset Components

### 1. Country Rules (`data/countries/spain/rules.txt`)

#### Demographics
```ini
finished=true
min_age=18
max_age=83
life_expectancy=83
```

#### Naming System
```ini
name_order=first+surname1+surname2
surname_count=2
surname_usage=always
```

Spanish naming follows patronymic tradition:
- First surname: Father's first surname
- Second surname: Mother's first surname
- Example: "María García López" (García from father, López from mother)

####  Fertility & Family
```ini
female_fertility_min_age=15
female_fertility_max_age=45
parent_min_age_gap=18
parent_max_age_gap=45
average_children=1.2
min_children=1
max_children=3
sibling_probability=75
average_siblings=1.8
```

**Implementation Details**:
- Mother age at birth: Strictly validated between 15-45 years
- Sibling ages: Calculated to ensure mother could give birth to all
- Twins/Triplets: 15% chance, max 3 siblings with same age
- Unique names: All siblings have different names (50-attempt uniqueness check)

#### Death Probabilities (Age-Based)

Parents (based on identity's age):
```ini
death_prob_parents_very_young=2
death_prob_parents_young_adults=5
death_prob_parents_adults=30
death_prob_parents_middle_aged=50
death_prob_parents_older_adults=70
death_prob_parents_seniors=85
death_prob_parents_elderly=95
```

**Realistic Implementation**:
- Identity 70+: 95% chance parents deceased, died 10-30 years ago
- Identity 60-70: 85% chance parents deceased, died 5-20 years ago
- Parent ages capped at life_expectancy + 0-5 years (83-88)
- No unrealistic scenarios (parents living to 100, dying "last year" when child is 75)

#### Physical Characteristics

Hair Colors (realistic Spanish distribution):
```ini
hair_colors=Black:35,Dark Brown:30,Brown:20,Light Brown:8,
            Dark Blonde:3,Blonde:2,Light Blonde:1,Red:1,
            Gray:0,White:0
```

Eye Colors:
```ini
eye_colors=Dark Brown:45,Brown:30,Light Brown:15,Hazel:5,
           Green:3,Blue:1.5,Gray:0.5
```

Skin Tones:
```ini
skin_tones=Light:60,Medium:35,Olive:4,Tan:0.8,Dark:0.2
```

#### Religion
```ini
religions=Catholic:55,Atheist:25,Agnostic:12,
          Non-practicing Catholic:5,Muslim:2,
          Protestant:0.7,Other:0.3
```

#### Economic Data

Social Class Distribution:
```ini
social_classes=low:25,middle:50,upper-middle:20,high:5
```

Salary Ranges (Annual, EUR):
```ini
salary_low=12000,22000
salary_middle=22000,40000
salary_upper-middle=40000,75000
salary_high=75000,200000
```

Pension Ranges (Annual, EUR):
```ini
pension_low=8000,16000
pension_middle=15000,30000
pension_upper-middle=28000,55000
pension_high=50000,120000
```

Employment:
```ini
unemployment_rate=13.5
jobless_rate=2.5
```

#### Phone System
```ini
phone_country_code=+34
phone_length=9
phone_mobile_prefixes=6,7
phone_format=### ## ## ##
```

**Implementation**: ONLY mobile phones generated (no landlines)
**Format**: +34 6XX XX XX XX or +34 7XX XX XX XX

#### Languages
```ini
min_languages=1
max_languages=4
available_languages=English:70,French:30,German:15,Italian:10,
                    Portuguese:12,Catalan:20,Basque:8,
                    Galician:6,Chinese:0.5,Arabic:1
language_level_basic=30
language_level_intermediate=50
language_level_advanced=20
```

**Special Rules**:
- University graduates: MUST have B1+ English (intermediate or advanced)
- Young people (<30): 100% have at least basic English
- Primary education only: Max basic level languages

### 2. Names Database

#### Structure
```
data/countries/spain/names/{gender}/{age_bucket}.txt
```

**Age Buckets**:
- very_young (18-23)
- young_adults (23-34)
- adults (34-50)
- middle_aged (50-65)
- older_adults (65-83)
- seniors (beyond life expectancy)
- elderly (oldest segment)

**Example Names**:

Male - very_young:
```
Alejandro
Hugo
Pablo
Álvaro
Adrián
```

Female - elderly:
```
María
Carmen
Josefa
Francisca
Dolores
```

#### Implementation
Age-appropriate name selection ensures realistic generational naming patterns.

### 3. Surnames

Located in: `data/countries/spain/surnames/`

**Files**:
- `male.txt`: ~200 Spanish surnames
- `female.txt`: Same surnames (Spain doesn't gender surnames)

**Most Common**:
```
García
Fernández
González
Rodríguez
López
Martínez
Sánchez
Pérez
...
```

### 4. Cities

File: `data/countries/spain/cities.txt`

Format: `City|PostalCode|Province`

```
Madrid|28001|Madrid
Barcelona|08001|Barcelona
Valencia|46001|Valencia
Sevilla|41001|Sevilla
Zaragoza|50001|Zaragoza
...
```

**Total**: 100+ Spanish cities with postal codes and provinces

### 5. Regional & Historical Characteristics

File: `data/countries/spain/regional_characteristics.txt`

Format: `text|min_age|max_age|gender|probability`

**Key Characteristics**:

```
Completed mandatory military service (Mili)|45|75|male|0.95
Grew up during Franco's dictatorship|55|999|both|1.0
Experienced the Spanish transition to democracy|50|70|both|1.0
Lived through the 1992 Barcelona Olympics era|40|999|both|0.7
Witnessed Spain joining the European Union (1986)|45|999|both|0.8
Experienced the 2008 economic crisis|25|999|both|0.85
Grew up with the Peseta currency (pre-Euro)|32|999|both|0.9
Remembers the 2004 Madrid train bombings|27|999|both|0.7
Affected by youth unemployment crisis|22|35|both|0.4
```

**Age Calculation Logic**:
- Person must have been **5-7+ years old** when event occurred to "remember" it
- Example: 2004 bombings (min_age 27) → Person born 1998 or earlier → Was 6+ in 2004

### 6. Jobs Database

#### Structure
```
data/global/jobs/{gender}/{social_class}.txt
```

**Social Classes**: low, middle, upper-middle, high

**Example Jobs**:

Female/Middle:
```
Nurse
Teacher
Accountant
Office Manager
Social Worker
Pharmacy Technician
Human Resources Specialist
Marketing Coordinator
...
```

Male/High:
```
CEO
Director
Senior Engineer
Financial Manager
Surgeon
Architect
Investment Banker
...
```

#### Age Requirements

File: `data/global/jobs/age_requirements.txt`

```
Teacher:22
Nurse:22
Pharmacy Technician:21
Lawyer:24
Doctor:26
Surgeon:28
University Professor:28
CEO:30
...
```

**Implementation**:
- Persons under minimum age CANNOT have that job
- Persons under 18 are automatically "Student"
- Work history validated: person doesn't start career unrealistically late

### 7. Hobbies

#### Global Hobbies by Age/Gender

Structure:
```
data/global/hobbies/{age_bucket}/{gender}.txt
```

Example - adults/male:
```
Playing football
Watching football matches
Playing basketball
Cycling
Hiking
Video games
Reading
Playing guitar
...
```

#### Spain-Specific Hobbies

File: `data/countries/spain/hobbies.txt`

```
Following Real Madrid
Following FC Barcelona
Following Atlético de Madrid
Playing padel
Going to terrazas in summer
Eating tapas
Watching bullfighting
Flamenco dancing
...
```

**Selection Logic**:
1. 2 national hobbies (guaranteed)
2. 1 class-based hobby
3. 1 gender-based hobby
4. 1 neutral hobby
5. Total: 3-5 hobbies per person

### 8. Death Causes

File: `data/global/death/causes_by_age.txt`

Format: `age_bucket:cause1,cause2,cause3...`

```
very_young:Car accident,Motorcycle accident,Drowning,...
young_adults:Car accident,Drug overdose,Suicide,...
adults:Heart attack,Cancer,Stroke,Diabetes complications,...
elderly:Alzheimer's disease,Pneumonia,Heart failure,...
```

**Special Cases**:
- Childbirth complications: 5% chance if mother died same year as child birth (identity or sibling)

### 9. Education System

File: `data/global/education/levels.txt`

```
No formal education
Incomplete primary education
Primary education
Secondary education
Vocational training
Bachelor's degree
Master's degree
Doctorate/PhD
```

#### Job-Education Mapping

File: `data/global/education/job_education_map.txt`

```
Nurse:bachelor|Nursing
Teacher:bachelor|Education
Lawyer:bachelor|Law
Doctor:doctorate|Medicine
Software Engineer:bachelor|Computer Science
...
```

### 10. Cultural Considerations

File: `data/countries/spain/considerations.txt`

**Content**: Detailed cultural guide covering:
- Social behavior (kisses on cheeks, personal space, eye contact)
- Daily life schedule (late meals, siesta culture)
- Communication style (directness, interrupting as engagement)
- Work culture (work-life balance, August vacations)
- Social etiquette (greeting shopkeepers, tipping)
- Food & drink culture (coffee, tapas, wine)
- Regional differences (Catalonia, Basque Country, Galicia)
- Things to avoid (Civil War discussions, bullfighting assumptions)

## Generation Statistics

### Family Structure

**Parent Distribution** (for identity age 60-80):
- 95-98% have deceased parents
- Death occurred 6-20 years ago (realistic timing)
- Parent death ages: 60-88 years (not 95-100)

**Sibling Probability**: 75%
- Average: 1.8 siblings
- Twins/Triplets: 15% chance
- All siblings have unique names

**Children** (for married/divorced 40+):
- Probability: 65-85% depending on age
- Average: 1.2 children
- Respect mother's fertility limits

### Employment

**Age <18**: 100% Student
**Age 18-23**: 70% Student, 20% Employed, 10% Unemployed
**Age 65+**: 100% Retired

**Work History Validation**:
- No one starts career after age 25 without previous jobs (unless advanced degree)
- People 40+ have previous job history (80% probability)
- Work start dates never in the future

### Language Proficiency

**Spanish**: 100% native
**English**:
- Age <30: 100% have at least basic
- University graduates: 100% have B1+ (intermediate/advanced)
- Primary education only: Max basic level

## Implementation Features

### Validation Systems

1. **Age Constraints**:
   - All family member ages validated against fertility limits
   - No impossible scenarios (mother age 8 giving birth)

2. **Death Timing**:
   - Realistic death ages (based on life expectancy)
   - Realistic timing (old identity → parents died long ago)
   - No future death dates

3. **Employment Coherence**:
   - Age requirements respected
   - Career start ages realistic
   - Work history complete for older persons

4. **Regional Characteristics**:
   - Age-filtered (person was old enough to remember event)
   - Probability-based selection

### Special Cases Handled

- ✅ Mother death in childbirth (identity or sibling birth)
- ✅ Twins/triplets (same age, unique names, marked in display)
- ✅ Unique sibling names (50-attempt uniqueness, fallback numbering)
- ✅ Realistic parent ages and death timing
- ✅ Work history gaps filled for older workers
- ✅ University graduates have appropriate English level

## Output Format

### CLI Display

Box-formatted output with:
- Personal information (name, DOB, physical characteristics)
- Location (city, postal code, province)
- Employment (current/previous with dates and termination reasons)
- Economic data (salary/pension, social class)
- Education and languages
- Contact (phone, email with inbox URL)
- Hobbies
- Family details (parents, siblings, partner, children)
  - Twin/triplet markers: "(Twin)" or "(Triplet)"
  - Deceased members: death dates and causes
- Regional characteristics
- Cultural considerations

### JSON Export

All data serialized to JSON for:
- Storage
- Import/export
- API integration

## Known Limitations

1. **Test Validation**: Test suite has incorrect validation for "Housewife/Jobless with previous_positions" (this IS valid in reality)

2. **Single Country**: Only Spain fully implemented (others planned)

3. **Binary Gender**: System currently supports only male/female (could be extended)

## Future Enhancements

- More nuanced employment sectors
- Expanded regional characteristics
- Education field specializations
- Hobby combinations based on personality clusters
- Financial history (credit scores, debts)
- Health conditions (age-appropriate)
- Additional Spanish regions with unique characteristics

---

**Version**: 1.0
**Last Updated**: December 2025
**Maintainer**: Leucocito
**Status**: Production-ready for Spain dataset
