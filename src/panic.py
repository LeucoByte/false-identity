#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panic Mode & Recovery System for Synthetic Identity Generator.
Emergency security feature to encrypt, backup, and recover identities.
"""

import json
import os
import zipfile
import subprocess
import time
import getpass
import readline
import glob
from pathlib import Path
from typing import Tuple, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import requests

from config import BOLD, RED, GREEN, YELLOW, CYAN, MAGENTA, RESET, IDENTITIES_DIR
from storage import list_saved_identities, load_identity, save_identity


def setup_path_completion(start_dir='/'):
    """
    Configure readline for path autocompletion with Tab key.
    Enables completion for file paths in input prompts.

    Args:
        start_dir: Initial directory to start path completion from (default: /)
    """
    def path_completer(text, state):
        """Autocomplete file paths."""
        # Expand user directory
        text = os.path.expanduser(text)

        # If the text is empty, start from start_dir
        if not text:
            text = start_dir

        # Handle directory completion
        if text.endswith('/'):
            pattern = text + '*'
        else:
            pattern = text + '*'

        # Get all matches
        matches = glob.glob(pattern)

        # Add trailing slash to directories
        matches = [
            match + '/' if os.path.isdir(match) else match
            for match in matches
        ]

        # Return the state-th match
        try:
            return matches[state]
        except IndexError:
            return None

    # Enable tab completion
    readline.set_completer(path_completer)
    readline.parse_and_bind('tab: complete')

    # For better UX on some systems
    readline.parse_and_bind('set show-all-if-ambiguous on')
    readline.parse_and_bind('set completion-ignore-case on')


def derive_key_from_passphrase(passphrase: str, salt: bytes) -> bytes:
    """
    Derive a Fernet-compatible encryption key from a passphrase using PBKDF2.

    Args:
        passphrase: User-provided passphrase
        salt: Random salt bytes for key derivation

    Returns:
        Base64-encoded 32-byte key suitable for Fernet
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    return key


def encrypt_file(file_path: Path, passphrase: str) -> Path:
    """
    Encrypt a file using Fernet symmetric encryption.

    Args:
        file_path: Path to file to encrypt
        passphrase: Passphrase for encryption

    Returns:
        Path to encrypted file (.enc extension)
    """
    # Generate random salt
    salt = os.urandom(16)

    # Derive key from passphrase
    key = derive_key_from_passphrase(passphrase, salt)
    fernet = Fernet(key)

    # Read original file
    with open(file_path, 'rb') as f:
        data = f.read()

    # Encrypt data
    encrypted_data = fernet.encrypt(data)

    # Write encrypted file with salt prepended
    encrypted_path = file_path.with_suffix(file_path.suffix + '.enc')
    with open(encrypted_path, 'wb') as f:
        f.write(salt)  # First 16 bytes are the salt
        f.write(encrypted_data)

    return encrypted_path


def decrypt_file(encrypted_path: Path, passphrase: str, output_path: Optional[Path] = None) -> Path:
    """
    Decrypt a file encrypted with encrypt_file().

    Args:
        encrypted_path: Path to encrypted file
        passphrase: Passphrase used for encryption
        output_path: Optional output path (defaults to removing .enc extension)

    Returns:
        Path to decrypted file

    Raises:
        Exception: If passphrase is incorrect or file is corrupted
    """
    # Read encrypted file
    with open(encrypted_path, 'rb') as f:
        salt = f.read(16)  # First 16 bytes are the salt
        encrypted_data = f.read()

    # Derive key from passphrase
    key = derive_key_from_passphrase(passphrase, salt)
    fernet = Fernet(key)

    # Decrypt data
    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception as e:
        raise Exception(f"Decryption failed. Incorrect passphrase or corrupted file.") from e

    # Determine output path
    if output_path is None:
        if encrypted_path.suffix == '.enc':
            output_path = encrypted_path.with_suffix('')
        else:
            output_path = encrypted_path.with_suffix('.decrypted')

    # Write decrypted file
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)

    return output_path


def collect_all_identities() -> Tuple[list, int]:
    """
    Collect all saved identities into a list of dictionaries.

    Returns:
        Tuple of (list of identity dicts, count)
    """
    files = list_saved_identities()
    identities = []

    for filepath in files:
        try:
            identity = load_identity(str(filepath))
            # Convert to dict using the actual Identity fields
            identity_dict = {
                'first_name': identity.first_name,
                'surnames': identity.surnames,
                'full_name': identity.full_name,
                'gender': identity.gender,
                'date_of_birth': identity.date_of_birth,
                'age': identity.age,
                'country': identity.country,
                'city': identity.city,
                'nearby_town': identity.nearby_town,
                'postal_code': identity.postal_code,
                'job': identity.job,
                'phone': identity.phone,
                'email': identity.email,
                'website': identity.website,
                'email_status': identity.email_status,
                'skin_tone': identity.skin_tone,
                'hair_color': identity.hair_color,
                'eye_color': identity.eye_color,
                'height_cm': identity.height_cm,
                'weight_kg': identity.weight_kg,
                'religion': identity.religion,
                'hobbies': identity.hobbies,
                'notes': identity.notes,
                'family': identity.family
            }
            identities.append(identity_dict)
        except Exception as e:
            print(f"{RED}Warning: Could not load {filepath}: {e}{RESET}")
            continue

    return identities, len(identities)


def export_identities_to_json(output_path: Path) -> int:
    """
    Export all identities to a single JSON file.

    Args:
        output_path: Path where JSON file will be saved

    Returns:
        Number of identities exported
    """
    identities, count = collect_all_identities()

    # Create JSON structure
    export_data = {
        'version': '1.0',
        'export_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'identities': identities
    }

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    return count


def upload_to_uguu(file_path: Path) -> Optional[str]:
    """Upload to uguu.se - 128MB max, 48 hours retention."""
    try:
        with open(file_path, 'rb') as f:
            files = {'files[]': (file_path.name, f)}
            response = requests.post('https://uguu.se/upload', files=files, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('files'):
                return data['files'][0]['url']
        return None
    except Exception:
        return None


def upload_to_fileio(file_path: Path) -> Optional[str]:
    """Upload to file.io - One-time download."""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            response = requests.post('https://file.io', files=files, timeout=30)

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                return response_data.get('link')
        return None
    except Exception:
        return None


def upload_to_catbox(file_path: Path) -> Optional[str]:
    """Upload to catbox.moe - 200MB max, permanent storage."""
    try:
        with open(file_path, 'rb') as f:
            files = {'fileToUpload': (file_path.name, f)}
            data = {'reqtype': 'fileupload'}
            response = requests.post('https://catbox.moe/user/api.php', files=files, data=data, timeout=30)

        if response.status_code == 200:
            url = response.text.strip()
            if url.startswith('http'):
                return url
        return None
    except Exception:
        return None


def upload_backup(file_path: Path) -> Optional[str]:
    """
    Upload backup file to available service.
    Tries multiple services: uguu.se, catbox.moe, file.io

    Args:
        file_path: Path to file to upload

    Returns:
        Download URL if successful, None otherwise
    """
    services = [
        ('uguu.se (128MB, 48h retention)', upload_to_uguu),
        ('catbox.moe (200MB, permanent)', upload_to_catbox),
        ('file.io (one-time download)', upload_to_fileio)
    ]

    for service_name, upload_func in services:
        print(f"{YELLOW}      Trying {service_name}...{RESET}")
        url = upload_func(file_path)
        if url:
            print(f"{GREEN}      ✓ Uploaded successfully!{RESET}")
            return url

    return None


def panic_mode():
    """
    PANIC MODE - Emergency encryption and backup of all identities.

    This function:
    1. Collects all identities into a single JSON file
    2. Encrypts the JSON with user passphrase
    3. Creates a ZIP archive
    4. Encrypts the ZIP with a second passphrase
    5. Uploads to file.io for one-time download
    6. Displays download link and passphrases
    7. Simulates Tails OS persistence disable
    8. Initiates shutdown countdown
    """
    print(f"{BOLD}{RED}╔{'═'*60}╗{RESET}")
    print(f"{BOLD}{RED}║{'PANIC MODE ACTIVATED'.center(60)}║{RESET}")
    print(f"{BOLD}{RED}╚{'═'*60}╝{RESET}\n")

    print(f"{YELLOW}This will:{RESET}")
    print(f"  1. Export all identities to encrypted backup")
    print(f"  2. Upload to file.io (one-time download)")
    print(f"  3. Disable Tails OS persistence")
    print(f"  4. Initiate system shutdown\n")

    # Confirmation
    confirm = input(f"{BOLD}{RED}Continue? (yes/no):{RESET} ").strip().lower()
    if confirm not in ('yes', 'y'):
        print(f"{YELLOW}Panic mode cancelled.{RESET}")
        return

    print()

    # Step 1: Collect identities
    print(f"{CYAN}[1/7] Collecting identities...{RESET}")
    # Use home directory for easier access
    home_dir = Path.home()
    temp_dir = home_dir / '.panic_backup'
    temp_dir.mkdir(exist_ok=True)

    json_path = temp_dir / 'identities_backup.json'
    count = export_identities_to_json(json_path)
    print(f"{GREEN}      ✓ Collected {count} identities{RESET}\n")

    # Step 2: First encryption (JSON)
    print(f"{CYAN}[2/7] Encrypting identities JSON...{RESET}")
    passphrase1 = getpass.getpass(f"{BOLD}      Enter passphrase for JSON encryption:{RESET} ")

    if not passphrase1:
        print(f"{RED}Error: Passphrase cannot be empty{RESET}")
        return

    encrypted_json_path = encrypt_file(json_path, passphrase1)
    print(f"{GREEN}      ✓ JSON encrypted{RESET}\n")

    # Step 3: Create ZIP
    print(f"{CYAN}[3/7] Creating ZIP archive...{RESET}")
    zip_path = temp_dir / 'identities_backup.zip'

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(encrypted_json_path, encrypted_json_path.name)

    print(f"{GREEN}      ✓ ZIP created{RESET}\n")

    # Step 4: Second encryption (ZIP)
    print(f"{CYAN}[4/7] Encrypting ZIP archive...{RESET}")
    passphrase2 = getpass.getpass(f"{BOLD}      Enter passphrase for ZIP encryption (Enter for same):{RESET} ")

    if not passphrase2:
        passphrase2 = passphrase1
        print(f"{YELLOW}      Using same passphrase for ZIP{RESET}")

    encrypted_zip_path = encrypt_file(zip_path, passphrase2)
    print(f"{GREEN}      ✓ ZIP encrypted{RESET}\n")

    # Step 5: Upload to available service
    print(f"{CYAN}[5/7] Uploading encrypted backup...{RESET}")
    download_url = upload_backup(encrypted_zip_path)

    if not download_url:
        print(f"{RED}      ✗ Upload failed!{RESET}")
        print(f"{YELLOW}      Encrypted backup saved locally at:{RESET}")
        print(f"{YELLOW}      {encrypted_zip_path}{RESET}\n")
        return

    print(f"{GREEN}      ✓ Upload successful!{RESET}\n")

    # Step 6: Display recovery information
    print(f"{BOLD}{GREEN}╔{'═'*60}╗{RESET}")
    print(f"{BOLD}{GREEN}║{'BACKUP CREATED SUCCESSFULLY'.center(60)}║{RESET}")
    print(f"{BOLD}{GREEN}╚{'═'*60}╝{RESET}\n")

    print(f"{BOLD}{YELLOW}SAVE THIS INFORMATION (photo or write it down):{RESET}\n")
    print(f"{BOLD}Download URL (one-time only):{RESET}")
    print(f"{CYAN}{download_url}{RESET}\n")
    print(f"{BOLD}Passphrase 1 (JSON decryption):{RESET}")
    print(f"{CYAN}{passphrase1}{RESET}\n")
    print(f"{BOLD}Passphrase 2 (ZIP decryption):{RESET}")
    print(f"{CYAN}{passphrase2}{RESET}\n")

    if passphrase1 == passphrase2:
        print(f"{YELLOW}Note: Both passphrases are the same{RESET}\n")

    print(f"{RED}WARNING: Download link works only ONCE!{RESET}")
    print(f"{RED}Make sure to save this information before continuing.{RESET}\n")

    # Wait for user confirmation
    input(f"{BOLD}Press Enter when you have saved this information...{RESET}")
    print()

    # Step 7: Disable Tails persistence
    print(f"{CYAN}[6/7] Disabling Tails OS persistence...{RESET}")

    # COMMENTED FOR SAFETY - Uncomment in production on Tails OS:
    # try:
    #     # Method 1: Delete persistent volume configuration
    #     subprocess.run(['sudo', 'rm', '-rf', '/live/persistence/TailsData_unlocked'], check=False)
    #
    #     # Method 2: Disable persistence feature
    #     subprocess.run(['sudo', 'tails-persistence-setup', 'delete'], check=False)
    #
    #     # Method 3: Remove persistence.conf
    #     subprocess.run(['sudo', 'rm', '-f', '/live/persistence/TailsData_unlocked/persistence.conf'], check=False)
    #
    #     print(f"{GREEN}      ✓ Tails persistence disabled{RESET}")
    # except Exception as e:
    #     print(f"{YELLOW}      ⚠ Could not disable persistence: {e}{RESET}")

    print(f"{YELLOW}      [SIMULATION] Tails persistence disable is commented for safety{RESET}")
    print(f"{YELLOW}      [SIMULATION] Uncomment code in panic.py to enable in production{RESET}")
    print(f"{GREEN}      ✓ Persistence would be disabled{RESET}\n")

    # Step 8: Shutdown countdown
    print(f"{CYAN}[7/7] Initiating system shutdown...{RESET}\n")
    print(f"{BOLD}{RED}System will shutdown in:{RESET}\n")

    for i in range(3, 0, -1):
        print(f"{BOLD}{RED}      {i}...{RESET}")
        time.sleep(1)

    print(f"\n{BOLD}{CYAN}Goodbye, my friend.{RESET}\n")

    # Clean up temp files
    try:
        json_path.unlink(missing_ok=True)
        encrypted_json_path.unlink(missing_ok=True)
        zip_path.unlink(missing_ok=True)
        encrypted_zip_path.unlink(missing_ok=True)
    except:
        pass

    # ACTUAL SHUTDOWN COMMAND (commented for safety)
    # Uncomment in production on Tails OS:
    # subprocess.run(['sudo', 'poweroff'])

    print(f"{YELLOW}[SIMULATION] System shutdown command would execute here{RESET}")
    print(f"{YELLOW}[SIMULATION] Uncomment the poweroff command in production{RESET}\n")


def panic_recovery():
    """
    PANIC RECOVERY - Restore identities from encrypted backup.

    This function:
    1. Prompts for encrypted backup file path
    2. Decrypts ZIP with user passphrase
    3. Extracts encrypted JSON
    4. Decrypts JSON with user passphrase
    5. Imports all identities
    6. Reports success/failure
    """
    print(f"{BOLD}{CYAN}╔{'═'*60}╗{RESET}")
    print(f"{BOLD}{CYAN}║{'PANIC RECOVERY MODE'.center(60)}║{RESET}")
    print(f"{BOLD}{CYAN}╚{'═'*60}╝{RESET}\n")

    print(f"{YELLOW}This will restore identities from an encrypted backup.{RESET}\n")

    # Step 1: Get backup file (path or URL) with autocomplete
    print(f"{CYAN}[1/5] Locating backup file...{RESET}")
    print(f"{YELLOW}      Tip: Enter a URL or file path{RESET}")
    print(f"{YELLOW}      • URL example: https://d.uguu.se/xxxxx.enc{RESET}")
    print(f"{YELLOW}      • Path example: ~/.panic_backup/identities_backup.zip.enc{RESET}")
    print(f"{YELLOW}      (Tab key autocompletes paths){RESET}")

    # Enable path completion starting from home directory
    home_dir = Path.home()
    setup_path_completion(str(home_dir))

    backup_input = input(f"{BOLD}      Enter URL or path:{RESET} ").strip()

    if not backup_input:
        print(f"{YELLOW}Recovery cancelled.{RESET}")
        return

    # Create temp directory for extraction in home
    temp_dir = home_dir / '.panic_recovery'
    temp_dir.mkdir(exist_ok=True)

    # Determine if input is URL or file path
    if backup_input.startswith('http://') or backup_input.startswith('https://'):
        # It's a URL - download it
        print(f"{YELLOW}      Detected URL, downloading...{RESET}")
        try:
            response = requests.get(backup_input, timeout=60)
            if response.status_code == 200:
                # Save to temp directory
                backup_path = temp_dir / 'downloaded_backup.zip.enc'
                backup_path.write_bytes(response.content)
                print(f"{GREEN}      ✓ Downloaded {len(response.content)} bytes{RESET}\n")
            else:
                print(f"{RED}      ✗ Download failed: HTTP {response.status_code}{RESET}")
                return
        except requests.exceptions.Timeout:
            print(f"{RED}      ✗ Download timeout{RESET}")
            return
        except Exception as e:
            print(f"{RED}      ✗ Download error: {e}{RESET}")
            return
    else:
        # It's a file path
        # Expand ~ if present
        backup_input = os.path.expanduser(backup_input)
        backup_path = Path(backup_input)

        if not backup_path.exists():
            print(f"{RED}      ✗ File not found: {backup_path}{RESET}")
            return

        print(f"{GREEN}      ✓ Backup file found{RESET}\n")

    # Step 2: Decrypt ZIP
    print(f"{CYAN}[2/5] Decrypting ZIP archive...{RESET}")

    while True:
        try:
            passphrase_zip = getpass.getpass(f"{BOLD}      Enter ZIP passphrase:{RESET} ")
            zip_path = decrypt_file(backup_path, passphrase_zip, temp_dir / 'backup.zip')
            print(f"{GREEN}      ✓ ZIP decrypted{RESET}\n")
            break
        except Exception as e:
            print(f"{RED}      ✗ Decryption failed: {str(e)}{RESET}")
            print(f"{YELLOW}      Try again (Ctrl+C to cancel){RESET}\n")

    # Step 3: Extract ZIP
    print(f"{CYAN}[3/5] Extracting ZIP contents...{RESET}")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(temp_dir)
        print(f"{GREEN}      ✓ ZIP extracted{RESET}\n")
    except Exception as e:
        print(f"{RED}      ✗ Extraction failed: {e}{RESET}")
        return

    # Find the encrypted JSON
    encrypted_json = None
    for file in temp_dir.iterdir():
        if file.suffix == '.enc' and 'identities_backup.json' in file.name:
            encrypted_json = file
            break

    if not encrypted_json:
        print(f"{RED}      ✗ Encrypted JSON not found in backup{RESET}")
        return

    # Step 4: Decrypt JSON
    print(f"{CYAN}[4/5] Decrypting identities JSON...{RESET}")

    while True:
        try:
            passphrase_json = getpass.getpass(f"{BOLD}      Enter JSON passphrase (Enter for same as ZIP):{RESET} ")

            if not passphrase_json:
                passphrase_json = passphrase_zip
                print(f"{YELLOW}      Using same passphrase as ZIP{RESET}")

            json_path = decrypt_file(encrypted_json, passphrase_json, temp_dir / 'identities_backup.json')
            print(f"{GREEN}      ✓ JSON decrypted{RESET}\n")
            break
        except Exception as e:
            print(f"{RED}      ✗ Decryption failed: {str(e)}{RESET}")
            print(f"{YELLOW}      Try again (Ctrl+C to cancel){RESET}\n")

    # Step 5: Import identities
    print(f"{CYAN}[5/5] Importing identities...{RESET}")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        identities = data.get('identities', [])
        imported_count = 0
        failed_count = 0

        for identity_dict in identities:
            try:
                # Create filename
                email = identity_dict.get('email', 'unknown')
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f"{email.replace('@', '_at_')}_{timestamp}.json"
                filepath = IDENTITIES_DIR / filename

                # Save identity
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(identity_dict, f, ensure_ascii=False, indent=2)

                imported_count += 1
            except Exception as e:
                failed_count += 1
                print(f"{RED}      Warning: Failed to import one identity: {e}{RESET}")

        print(f"{GREEN}      ✓ Import complete{RESET}\n")

        # Report results
        print(f"{BOLD}{GREEN}╔{'═'*60}╗{RESET}")
        print(f"{BOLD}{GREEN}║{'RECOVERY SUCCESSFUL'.center(60)}║{RESET}")
        print(f"{BOLD}{GREEN}╚{'═'*60}╝{RESET}\n")

        print(f"{BOLD}Imported:{RESET} {GREEN}{imported_count} identities{RESET}")
        if failed_count > 0:
            print(f"{BOLD}Failed:{RESET} {RED}{failed_count} identities{RESET}")

        print(f"\n{YELLOW}You can now view your recovered identities in the main menu.{RESET}\n")

    except Exception as e:
        print(f"{RED}      ✗ Import failed: {e}{RESET}")
        return
    finally:
        # Clean up temp files
        try:
            zip_path.unlink(missing_ok=True)
            encrypted_json.unlink(missing_ok=True)
            json_path.unlink(missing_ok=True)
        except:
            pass
