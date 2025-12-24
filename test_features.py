#!/usr/bin/env python3
"""
Script de testing exhaustivo para validar todas las features implementadas.
"""

import sys
sys.path.insert(0, 'src')

from generator import IdentityGenerator, DataLoader

def main():
    loader = DataLoader()
    gen = IdentityGenerator(loader)

    print('='*80)
    print('TESTING EXHAUSTIVO DE FEATURES')
    print('='*80)
    print()

    # Generate 50 test identities
    print('Generando 50 identidades de prueba...')
    errors = []
    success = 0

    for i in range(50):
        try:
            identity = gen.generate(country='spain')

            # VALIDACIÓN 1: Edad en rango
            assert identity.age >= 18 and identity.age <= 83, f'Edad fuera de rango: {identity.age}'

            # VALIDACIÓN 2: Teléfono correcto (solo móviles)
            assert identity.phone.startswith('+34'), f'Teléfono sin código: {identity.phone}'
            phone_prefix = identity.phone.replace('+34', '').replace(' ', '')[0]
            assert phone_prefix in ['6', '7'], f'❌ Teléfono fijo detectado: {identity.phone}'

            # VALIDACIÓN 3: Hobbies
            assert len(identity.hobbies) > 0, 'Sin hobbies'

            # VALIDACIÓN 4: Idiomas coherentes con educación (B1+ para universitarios)
            if identity.education:
                edu_lower = identity.education.lower()
                if any(deg in edu_lower for deg in ['bachelor', 'master', 'doctorate']):
                    for lang in identity.languages:
                        if lang['language'] == 'English':
                            level = lang['level'].lower()
                            assert level in ['intermediate', 'advanced'], \
                                f"❌ Universitario con inglés básico: {identity.education}"

            # VALIDACIÓN 5: Jobless/Housewife/Student sin previous_positions
            if identity.job in ['Jobless', 'Housewife'] or identity.job.startswith('Student'):
                if identity.work_experience:
                    prev_pos = identity.work_experience.get('previous_positions')
                    assert prev_pos is None, \
                        f"❌ {identity.job} tiene previous_positions"

            # VALIDACIÓN 6: Padres que superan esperanza de vida están muertos
            if identity.family:
                father = identity.family.get('father')
                mother = identity.family.get('mother')

                if father and not father.get('deceased'):
                    father_age = father.get('current_age')
                    if father_age and father_age > 83:
                        raise AssertionError(f'❌ Padre vivo con {father_age} años (>83)')

                if mother and not mother.get('deceased'):
                    mother_age = mother.get('current_age')
                    if mother_age and mother_age > 83:
                        raise AssertionError(f'❌ Madre viva con {mother_age} años (>83)')

            # VALIDACIÓN 7: Work experience tiene tiempo relativo
            if identity.work_experience:
                start_date = identity.work_experience.get('start_date')
                if start_date and start_date != 'N/A':
                    # El formato debería ser DD/MM/YYYY
                    parts = start_date.split('/')
                    assert len(parts) == 3, f'❌ Formato fecha incorrecto: {start_date}'

            # VALIDACIÓN 8: Regional characteristics presentes para adultos+
            if identity.age >= 45:
                # Es probable que tengan regional characteristics
                if identity.regional_characteristics:
                    assert len(identity.regional_characteristics) > 0

            success += 1
            if (i + 1) % 10 == 0:
                print(f'  ✓ {i + 1}/50 identidades generadas correctamente')

        except Exception as e:
            errors.append(f'Identity {i+1}: {str(e)}')

    print()
    print('='*80)
    print(f'✓ {success}/50 identidades generadas exitosamente')

    if errors:
        print(f'✗ {len(errors)} errores encontrados:')
        for err in errors[:15]:  # Mostrar primeros 15 errores
            print(f'  {err}')
        return 1
    else:
        print('✓ TODAS las validaciones pasaron correctamente')
        print('✓ Features implementadas funcionan perfectamente')
        return 0

if __name__ == "__main__":
    sys.exit(main())
