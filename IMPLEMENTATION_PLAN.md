# Implementation Plan - Final Features

## Tasks Remaining:

### 1. Students → English B1+ mandatory if finished degree ✓ (partially done)
- Modify `_generate_languages()` to ensure students with completed degrees have B1+

### 2. Regional characteristics ✓ (file created)
- File created: `data/countries/spain/regional_characteristics.txt`
- Need to: Load and apply in generator

### 3. Work time display after Current Job ✓ (need to implement)
- Move work_exp_block position in models.py display

### 4. Remove landline phones ✓ (need to implement)
- Remove from rules.txt
- Update phone generation logic

### 5. Identity status field ✓ (added to model)
- Added to Identity model
- Default: "created"

### 6. Fix unemployed with "better opportunity" reason ✓ (need to fix)
- Filter termination reasons for unemployed

### 7. Adults+ → Parents more likely dead ✓ (need to implement)
- Increase death probability for elderly parents

### 8. Fix Current Job None with previous_positions ✓ (need to fix)
- Clean up work experience logic

### 9. Previous position → Previous Job display ✓ (need to implement)
- Reorganize display logic in models.py

### 10. Parents respect life expectancy ✓ (need to implement)
- Check parent ages against life_expectancy

### 11. Show "(X years/months ago)" in dates ✓ (need to implement)
- Calculate and display relative times

### 12. Testing ✓ (after all changes)

### 13. Modularize generator.py ✓ (final step)
- Split into multiple modules
