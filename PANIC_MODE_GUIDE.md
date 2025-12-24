# 🚨 PANIC MODE - Guía de Uso

## ⚠️ IMPORTANTE - LEE ESTO PRIMERO

El **PANIC MODE** es una funcionalidad de emergencia diseñada para situaciones críticas donde necesitas:
- Proteger tus identidades sintéticas de forma inmediata
- Eliminar rastros del sistema local
- Preservar acceso futuro mediante backup encriptado
- Desactivar la persistencia de Tails OS

## 📋 Qué hace el PANIC MODE

### Proceso Completo (7 pasos)

1. **Recolección de Identidades**
   - Exporta todas las identidades guardadas a un archivo JSON único

2. **Primera Encriptación (JSON)**
   - Solicita una passphrase para encriptar el JSON
   - Usa AES-256 con PBKDF2 (100,000 iteraciones)
   - Genera un salt aleatorio único

3. **Creación de ZIP**
   - Comprime el JSON encriptado en un archivo ZIP

4. **Segunda Encriptación (ZIP)**
   - Solicita una segunda passphrase (o usa la misma si presionas Enter)
   - Encripta el ZIP completo con otra capa de seguridad

5. **Upload a file.io**
   - Sube el ZIP encriptado a file.io
   - **IMPORTANTE**: El link de descarga funciona UNA SOLA VEZ
   - Después de descargar, el archivo se autodestruye del servidor

6. **Información de Recuperación**
   - Muestra el link de descarga
   - Muestra ambas passphrases
   - **CRÍTICO**: Haz una foto o escribe esta información en papel

7. **Shutdown**
   - Simula desactivación de persistencia de Tails OS
   - Cuenta regresiva de 3 segundos
   - Apagado del sistema (comando comentado por seguridad)

## 🔐 Cómo Usar PANIC MODE

### Activación

1. Ejecuta el programa principal:
   ```bash
   python3 src/main.py
   ```

2. Selecciona opción `[5] PANIC / HACKED MODE`

3. Confirma con `yes` cuando se te pregunte

4. **Introduce passphrase para JSON** (mínimo: usa algo fuerte)
   - Ejemplo: `MyStr0ng!Passphrase#2024`

5. **Introduce passphrase para ZIP** (o Enter para usar la misma)
   - Si es diferente, también debe ser fuerte
   - Si presionas Enter, usará la misma que el JSON

6. **GUARDA LA INFORMACIÓN**
   - El programa mostrará:
     - Link de descarga (file.io)
     - Passphrase 1 (JSON)
     - Passphrase 2 (ZIP)
   - **HAZ UNA FOTO O ESCRÍBELO EN PAPEL**
   - El link solo funciona UNA VEZ

7. Presiona Enter cuando hayas guardado todo

8. El sistema hará countdown y se apagará

## 🔓 PANIC RECOVERY - Recuperación

### Cuándo usar

- Has vuelto a iniciar Tails OS (sin persistencia)
- Tienes el link de descarga o el archivo guardado localmente
- Tienes las dos passphrases guardadas
- Quieres recuperar tus identidades

### Proceso

1. **Ejecuta el programa**
   ```bash
   python3 src/main.py
   ```

2. **Selecciona opción `[6] PANIC RECOVERY`**

3. **Introduce URL o ruta del archivo**

   **Opción A - Con URL (más fácil, recomendado):**
   ```
   https://d.uguu.se/xxxxx.enc
   ```
   El sistema detectará que es una URL y lo descargará automáticamente

   **Opción B - Con ruta local:**
   ```
   ~/.panic_backup/identities_backup.zip.enc
   ```
   Puedes usar Tab para autocompletar el path

4. **Introduce passphrase del ZIP**
   - Primera passphrase que te pedirá
   - Si falla, te pedirá de nuevo (Ctrl+C para cancelar)

5. **Introduce passphrase del JSON**
   - Segunda passphrase
   - Si presionas Enter, asume que es la misma que la del ZIP

6. **Verifica importación**
   - El sistema te dirá cuántas identidades importó
   - Ahora puedes verlas en el menú principal

## 🛡️ Seguridad

### Encriptación
- **Algoritmo**: AES-256 (Fernet)
- **KDF**: PBKDF2-HMAC-SHA256
- **Iteraciones**: 100,000
- **Salt**: 16 bytes aleatorios únicos por archivo
- **Doble capa**: JSON encriptado + ZIP encriptado

### Recomendaciones de Passphrases

**NO USAR**:
- ❌ `password123`
- ❌ `admin`
- ❌ Fecha de nacimiento
- ❌ Nombres propios simples

**SÍ USAR**:
- ✅ Mínimo 16 caracteres
- ✅ Mezcla de mayúsculas, minúsculas, números y símbolos
- ✅ Palabras sin sentido combinadas: `Gato#Verde$Luna!2024`
- ✅ Frases largas: `ElPerroComio7ManzanasRojas!`

### ⚠️ Advertencias Críticas

1. **Link de file.io es de UN SOLO USO**
   - Si alguien más lo descarga antes que tú, pierdes el backup
   - Descárgalo INMEDIATAMENTE después de tener Tails funcionando

2. **Sin passphrases = SIN RECUPERACIÓN**
   - Si olvidas las passphrases, NO hay forma de recuperar los datos
   - La encriptación es irreversible sin la clave correcta

3. **Persistencia de Tails**
   - En producción, el comando `sudo poweroff` está comentado
   - Descomenta en `/src/panic.py` línea ~420 para producción real

## 🧪 Testing

Para probar la encriptación sin usar el modo completo:

```bash
python3 test_panic.py
```

Esto verificará que:
- La encriptación funciona correctamente
- La desencriptación recupera el contenido original
- Las passphrases incorrectas son rechazadas

## 📁 Archivos Involucrados

- `/src/panic.py` - Módulo principal de panic mode
- `/src/ui/menus.py` - Integraciones con el menú
- `/src/main.py` - Punto de entrada con opciones
- `test_panic.py` - Tests de encriptación
- `requirements.txt` - Dependencias (cryptography, requests)

## 🔧 Dependencias

Instalar (si es necesario):
```bash
pip3 install cryptography requests
```

O en Tails:
```bash
sudo apt install python3-cryptography python3-requests
```

## 💡 Escenario de Uso Típico

1. **Situación normal**: Generas identidades, todo OK
2. **EMERGENCIA**: Detectas amenaza/compromiso
3. **Activas PANIC MODE**: Opción [5]
4. **Sistema se apaga**: Tails sin persistencia
5. **Reinicias Tails**: Sistema limpio, como nuevo
6. **Descargas backup**: Desde file.io con el link guardado
7. **PANIC RECOVERY**: Opción [6], introduces passphrases
8. **Todo recuperado**: Tus identidades están de vuelta

## ❓ Preguntas Frecuentes

**P: ¿Puedo usar la misma passphrase para JSON y ZIP?**
R: Sí, si presionas Enter cuando pide la segunda passphrase, usará la misma.

**P: ¿Qué pasa si descargo el archivo de file.io pero no lo desencripto inmediatamente?**
R: No hay problema, puedes guardarlo localmente. Solo el link expira después de una descarga.

**P: ¿Puedo hacer múltiples backups?**
R: Sí, cada vez que actives PANIC MODE se creará un nuevo backup con nuevo link.

**P: ¿Se borran las identidades locales después del panic mode?**
R: En la versión actual NO (es una simulación). En producción real, deberías añadir código para borrar.

**P: ¿El shutdown es real?**
R: NO, el comando `sudo poweroff` está comentado por seguridad. Descomenta para producción.

---

**Desarrollado por:** Leucocito
**GitHub:** https://github.com/LeucoByte
**Versión:** 1.0
