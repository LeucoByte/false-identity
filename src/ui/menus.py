#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menu functions for the Synthetic Identity Generator.
Interactive user interface for generating, viewing, and managing identities.
"""

import random
import subprocess
import time
from pathlib import Path
from wcwidth import wcswidth

from config import (
    BOLD, RED, GREEN, YELLOW, CYAN, MAGENTA, RESET,
    COUNTRIES_DIR
)
from generator import DataLoader, IdentityGenerator, get_inbox_url
from storage import (
    save_identity, load_identity, list_saved_identities,
    delete_identity, clean_all_identities, import_identities_from_json
)
from ui.display import clear_screen, print_world_ascii
from panic import panic_mode, panic_recovery
from models import translate


def pad_unicode_string(text: str, width: int) -> str:
    """
    Pad a string to a specific width, accounting for Unicode character widths.

    Args:
        text: String to pad (may contain Unicode characters)
        width: Target display width

    Returns:
        Padded string
    """
    # Calculate visual width of the string
    visual_width = wcswidth(text)
    if visual_width < 0:
        # If wcswidth returns -1 (contains non-printable), fallback to len()
        visual_width = len(text)

    # Calculate padding needed
    padding_needed = width - visual_width
    if padding_needed > 0:
        return text + (' ' * padding_needed)
    else:
        return text


def generate_new_identity():
    """
    Generate a new identity interactively.

    Displays country selection, generates identity, saves it,
    and offers option to continue generating.
    """
    print(f"{BOLD}{YELLOW}Current world:{RESET}")
    print_world_ascii()

    # Dynamically list all country directories
    available_countries = sorted([d.name for d in COUNTRIES_DIR.iterdir() if d.is_dir()])

    # Get display names and finished status from rules.txt
    country_display_names = {}
    country_finished = {}
    for code in available_countries:
        rules_path = COUNTRIES_DIR / code / "rules.txt"
        display_name = code.capitalize()
        finished = False
        if rules_path.exists():
            try:
                with open(rules_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().startswith('country_name='):
                            display_name = line.strip().split('=', 1)[1].strip()
                        elif line.strip().startswith('finished='):
                            finished = line.strip().split('=', 1)[1].strip().lower() == 'true'
            except Exception:
                pass
        country_display_names[code] = display_name
        country_finished[code] = finished

    # Dynamic number formatting
    num_width = len(str(len(available_countries) - 1))

    # Display countries in columns
    print(f"{BOLD}{YELLOW}Available countries:{RESET}")
    num_cols = 3
    col_entries = [[] for _ in range(num_cols)]
    num_rows = (len(available_countries) + num_cols - 1) // num_cols

    for idx, code in enumerate(available_countries):
        col = idx // num_rows
        # Add green dot for finished, red dot for unfinished (entre índice y nombre)
        status_indicator = f"{GREEN}●{RESET}" if country_finished[code] else f"{RED}●{RESET}"
        display = f"    [{RED}{idx:0{num_width}d}{RESET}] {status_indicator} {country_display_names[code]}"
        col_entries[col].append(display)

    # Pad columns to same number of rows
    for col in range(num_cols):
        while len(col_entries[col]) < num_rows:
            col_entries[col].append("")

    # Calculate visual width (accounting for ANSI codes and Unicode width)
    def visual_width(text):
        """Calculate visual width of string, excluding ANSI escape codes."""
        import re
        # Remove ANSI escape codes
        ansi_pattern = r'\x1b\[[0-9;]*m'
        clean = re.sub(ansi_pattern, '', text)
        # For Unicode characters (Thai, Cyrillic), each char = 1 width
        # Python's len() works correctly for most cases
        return len(clean)

    # Find max visual width for each column
    col_widths = []
    for col in range(num_cols):
        max_width = max(visual_width(entry) for entry in col_entries[col] if entry)
        col_widths.append(max_width)

    # Print with proper padding
    for row in range(num_rows):
        parts = []
        for col in range(num_cols):
            entry = col_entries[col][row]
            if entry:
                # Calculate padding needed
                visual_len = visual_width(entry)
                padding = col_widths[col] - visual_len
                padded = entry + (' ' * padding)
                parts.append(padded)
            else:
                parts.append(' ' * col_widths[col])
        line = "  ".join(parts)
        print(line)
    print()

    # Select country
    print(f"{BOLD}{YELLOW}Press Enter without typing a number to select a random country.{RESET}")
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

    # Get website
    print(f"{BOLD}{YELLOW}Please enter the website where you intend to use this synthetic identity (e.g., https://example.com):{RESET}")
    website = input(f"{BOLD}Website:{RESET} ").strip()
    if not website:
        website = "None"
    print()

    # Get gender (optional)
    print(f"{BOLD}{YELLOW}Select gender (Press Enter for random):{RESET}")
    print(f"{CYAN}1.{RESET} Male")
    print(f"{CYAN}2.{RESET} Female")
    gender_input = input(f"{BOLD}Choice (1/2):{RESET} ").strip()

    if gender_input == "1":
        selected_gender = "male"
    elif gender_input == "2":
        selected_gender = "female"
    else:
        selected_gender = None  # Random
    print()

    # Get age (optional)
    data_loader = DataLoader()
    rules = data_loader.load_rules(selected_country)
    min_age = rules.get_min_age()
    max_age = rules.get_max_age()
    print(f"{BOLD}{YELLOW}Do you want to specify an age? (Press Enter for random age){RESET}")
    age_input = input(f"{BOLD}Age ({min_age}-{max_age}):{RESET} ").strip()

    if age_input:
        try:
            age = int(age_input)
            if age < min_age or age > max_age:
                print(f"{RED}Age must be between {min_age} and {max_age}. Using random age.{RESET}")
                min_age_gen = None
                max_age_gen = None
            else:
                # Use exact age by setting min and max to same value
                min_age_gen = age
                max_age_gen = age
        except ValueError:
            print(f"{RED}Invalid age. Using random age.{RESET}")
            min_age_gen = None
            max_age_gen = None
    else:
        min_age_gen = None
        max_age_gen = None

    print()

    # Generate identity
    generator = IdentityGenerator(data_loader)

    # Loop for regeneration (r) or keep (k)
    while True:
        clear_screen()
        print(f"{GREEN}Generating {country_display_names[selected_country]} identity...{RESET}")
        time.sleep(1)  # Add realism

        identity = generator.generate(country=selected_country, website=website, gender=selected_gender, min_age=min_age_gen, max_age=max_age_gen)

        # Display identity
        clear_screen()
        print(identity.to_str_box())
        print()

        # Options after generating
        print(f"{BOLD}{YELLOW}Options:{RESET}")
        print(f"  [{RED}r{RESET}] Regenerate (discard this identity)")
        print(f"  [{RED}k{RESET}] Keep this identity")
        print()

        choice = input(f"{BOLD}Select option:{RESET} ").strip().lower()

        if choice == "r":
            # Regenerate with same parameters
            continue
        elif choice == "k":
            # Keep identity - save it
            filepath = save_identity(identity)
            print(f"\n{GREEN}Identity saved to:{RESET} {filepath}")
            print()

            # Ask if they want to continue generating
            print(f"{BOLD}{YELLOW}Do you want to generate another identity?{RESET}")
            print(f"  [{RED}y{RESET}] Yes, generate another")
            print(f"  [{RED}Enter{RESET}] Return to main menu")
            print()

            continue_choice = input(f"{BOLD}Select option:{RESET} ").strip().lower()

            if continue_choice == "y":
                clear_screen()
                # Continue generating - recursive call
                generate_new_identity()
                return
            else:
                clear_screen()
                return
        else:
            # Invalid choice, ask again
            print(f"{RED}Invalid option. Please choose 'r' or 'k'.{RESET}")
            time.sleep(1)


def view_saved_identities():
    """
    View and interact with saved identities.

    Displays list of identities with options to view details,
    delete individual identities, or return to menu.
    """
    files = list_saved_identities()

    if not files:
        print(f"{RED}No saved identities found.{RESET}")
        return

    print(f"{BOLD}{YELLOW}Saved identities: {len(files)}{RESET}")
    print()

    # Dynamic number formatting
    num_width = len(str(len(files)))

    # Column headers
    print(f"{BOLD}{YELLOW}Name:{RESET:<46} {BOLD}{CYAN}Nationality:{RESET:<21} {BOLD}{MAGENTA}Site:{RESET}")

    for i, filepath in enumerate(files):
        identity = load_identity(str(filepath))
        # Show original name with romanization in parentheses for non-Latin scripts
        non_latin_countries = ['russia', 'thailand', 'china', 'japan', 'greece']
        if identity.country.lower() in non_latin_countries:
            original_name = identity.full_name
            romanized = translate(identity.full_name, identity.country)
            full_name = f"{original_name} ({romanized})"
        else:
            full_name = identity.full_name
        country = identity.country.upper()
        website = identity.website

        # Use Unicode-aware padding for proper alignment
        padded_name = pad_unicode_string(full_name, 44)
        padded_country = pad_unicode_string(country, 30)
        print(f"    [{RED}{i:0{num_width}d}{RESET}] {padded_name}{padded_country}{website}")

    print()
    print(f"{BOLD}{YELLOW}Options:{RESET}")
    print(f"  [{RED}Number{RESET}] View identity details and manage notes")
    print(f"  [{RED}d + Number{RESET}] Delete identity (e.g., d0)")
    print(f"  [{RED}Enter{RESET}] Return to menu")
    print()

    while True:
        choice = input(f"{BOLD}Select option:{RESET} ").strip()

        # Empty input - return to menu
        if choice == "":
            clear_screen()
            return

        # Delete command (e.g., "d0")
        if choice.lower().startswith('d'):
            delete_num = choice[1:].strip()
            if delete_num.isdigit():
                idx = int(delete_num)
                if 0 <= idx < len(files):
                    delete_identity(files[idx])
                    print(f"{GREEN}Identity successfully deleted!{RESET}\n")
                    input(f"{BOLD}Press Enter to continue...{RESET}")
                    clear_screen()
                    # Reload and show menu again
                    view_saved_identities()
                    return
                else:
                    print(f"{RED}Invalid identity number.{RESET}\n")
                    continue
            else:
                print(f"{RED}Invalid option.{RESET}\n")
                continue

        # View identity details
        if not choice.isdigit():
            print(f"{RED}Invalid option.{RESET}")
            continue

        idx = int(choice)

        if idx == len(files):
            clear_screen()
            return

        if idx < 0 or idx >= len(files):
            print(f"{RED}Invalid option.{RESET}")
            continue

        # Display identity - INNER LOOP for identity options
        identity = load_identity(str(files[idx]))

        # Inner loop for identity detail view
        while True:
            clear_screen()
            # Reload identity in case it was modified
            identity = load_identity(str(files[idx]))
            print(identity.to_str_box())
            print()

            # Notes and considerations management submenu
            print(f"{BOLD}{YELLOW}Options:{RESET}")
            print(f"  [{RED}c{RESET}] View cultural considerations")
            print(f"  [{RED}a{RESET}] Add a note")
            print(f"  [{RED}e{RESET}] Edit identity JSON (opens gedit)")
            print(f"  [{RED}r + Number{RESET}] Remove note (e.g., r1)")
            print(f"  [{RED}Enter{RESET}] Return to identity list")
            print()

            note_choice = input(f"{BOLD}Select option:{RESET} ").strip()

            # Empty input - return to identity list
            if note_choice == "":
                break

            # Handle cultural considerations view
            if note_choice.lower() == 'c':
                clear_screen()  # Clean FIRST, then show context
                print(identity.display_considerations_box())
                print()
                input(f"{BOLD}Press Enter to continue...{RESET}")
                continue

            # Handle note management
            elif note_choice.lower() == 'a':
                # Add note
                print()
                new_note = input(f"{BOLD}Enter note text:{RESET} ").strip()
                if new_note:
                    identity.notes.append(new_note)
                    save_identity(identity, filepath=str(files[idx]))
                    print(f"{GREEN}Note added successfully!{RESET}")
                    print()
                    input(f"{BOLD}Press Enter to continue...{RESET}")
                continue
            elif note_choice.lower() == 'e':
                # Edit identity JSON with gedit
                json_path = str(files[idx])
                try:
                    # Open gedit and wait for it to close
                    print(f"\n{YELLOW}Opening {json_path} in gedit...{RESET}")
                    print(f"{YELLOW}Edit the JSON file, save your changes, and close gedit to continue.{RESET}\n")
                    subprocess.run(['gedit', json_path], check=True)

                    # Reload identity from JSON
                    print(f"\n{GREEN}Reloading identity from file...{RESET}")
                    identity = load_identity(json_path)
                    print(f"{GREEN}Identity updated successfully!{RESET}")
                    print()
                    input(f"{BOLD}Press Enter to continue...{RESET}")
                    continue
                except FileNotFoundError:
                    print(f"\n{RED}Error: gedit not found. Please install gedit:{RESET}")
                    print(f"{YELLOW}  sudo apt-get install gedit  (Debian/Ubuntu){RESET}")
                    print(f"{YELLOW}  brew install gedit  (macOS){RESET}\n")
                    input(f"{BOLD}Press Enter to continue...{RESET}")
                    continue
                except subprocess.CalledProcessError as e:
                    print(f"\n{RED}Error opening gedit: {e}{RESET}\n")
                    input(f"{BOLD}Press Enter to continue...{RESET}")
                    continue
                except Exception as e:
                    print(f"\n{RED}Error loading updated identity: {e}{RESET}\n")
                    print(f"{YELLOW}The JSON file may contain invalid data.{RESET}\n")
                    input(f"{BOLD}Press Enter to continue...{RESET}")
                    continue
            elif note_choice.lower().startswith('r'):
                # Remove note
                note_num = note_choice[1:].strip()
                if note_num.isdigit():
                    note_idx = int(note_num) - 1  # Convert to 0-based index
                    if 0 <= note_idx < len(identity.notes):
                        removed_note = identity.notes.pop(note_idx)
                        save_identity(identity, filepath=str(files[idx]))
                        print()
                        print(f"{GREEN}Note removed successfully!{RESET}")
                        print()
                        input(f"{BOLD}Press Enter to continue...{RESET}")
                    else:
                        print()
                        print(f"{RED}Invalid note number.{RESET}")
                        print()
                        input(f"{BOLD}Press Enter to continue...{RESET}")
                else:
                    print()
                    print(f"{RED}Invalid option.{RESET}")
                    print()
                    input(f"{BOLD}Press Enter to continue...{RESET}")
                continue
            else:
                print()
                print(f"{RED}Invalid option.{RESET}")
                print()
                input(f"{BOLD}Press Enter to continue...{RESET}")
                continue

        clear_screen()

        # Redisplay menu - reload files list in case of deletions
        files = list_saved_identities()
        if not files:
            clear_screen()
            return

        num_width = len(str(len(files)))

        print(f"{BOLD}{YELLOW}Saved identities: {len(files)}{RESET}")
        print()

        print(f"{BOLD}{YELLOW}Name:{RESET:<46} {BOLD}{CYAN}Nationality:{RESET:<21} {BOLD}{MAGENTA}Site:{RESET}")
        for i, filepath in enumerate(files):
            identity = load_identity(str(filepath))
            # Show original name with romanization in parentheses for non-Latin scripts
            non_latin_countries = ['russia', 'thailand', 'china', 'japan', 'greece']
            if identity.country.lower() in non_latin_countries:
                original_name = identity.full_name
                romanized = translate(identity.full_name, identity.country)
                full_name = f"{original_name} ({romanized})"
            else:
                full_name = identity.full_name
            country = identity.country.upper()
            website = identity.website

            # Use Unicode-aware padding for proper alignment
            padded_name = pad_unicode_string(full_name, 44)
            padded_country = pad_unicode_string(country, 30)
            print(f"    [{RED}{i:0{num_width}d}{RESET}] {padded_name}{padded_country}{website}")

        print()
        print(f"{BOLD}{YELLOW}Options:{RESET}")
        print(f"  [{RED}Number{RESET}] View identity details and manage notes")
        print(f"  [{RED}d + Number{RESET}] Delete identity (e.g., d0)")
        print(f"  [{RED}Enter{RESET}] Return to menu")
        print()


def check_emails():
    """
    Check and activate email inboxes for saved identities.

    Displays list of emails with inbox URLs and allows selection
    to activate and view inbox.
    """
    files = list_saved_identities()

    if not files:
        print(f"{RED}No saved identities found.{RESET}")
        return

    # Dynamic number formatting
    num_width = len(str(len(files)))

    EMAIL_WIDTH = 50
    SITE_WIDTH = 40

    header_email = "Email".ljust(EMAIL_WIDTH)
    header_site = "Site:".ljust(SITE_WIDTH)
    header_links = "Link:"
    print(f"{BOLD}{YELLOW}Saved emails: {len(files)}{RESET}\n")

    print(f"{BOLD}{YELLOW}{header_email}{RESET}{BOLD}{MAGENTA}{header_site}{BOLD}{RESET}{CYAN}{header_links}{RESET}")

    emails_list = []
    for i, filepath in enumerate(files):
        identity = load_identity(str(filepath))
        inbox_url = get_inbox_url(identity.email)
        email_str = f"[{RED}{i:0{num_width}d}{RESET}] {identity.email}".ljust(EMAIL_WIDTH + len(RED) + len(RESET) + num_width - 2)
        site_str = f"{identity.website}".ljust(SITE_WIDTH)
        print(f"    {email_str} {site_str}{inbox_url}")
        emails_list.append((identity.email, identity.website, inbox_url))

    print()
    print(f"{BOLD}{YELLOW}Options:{RESET}")
    print(f"  [{RED}Number{RESET}] Consult an email inbox")
    print(f"  [{RED}Enter{RESET}] Return to menu")
    print()

    choice = input(f"{BOLD}Select option:{RESET} ").strip()

    if choice == '' or not choice.isdigit():
        clear_screen()
        return

    idx = int(choice)

    if idx == len(emails_list):
        clear_screen()
        return

    if idx < 0 or idx >= len(emails_list):
        print(f"{RED}Invalid option.{RESET}")
        return

    # Load identity to check email status
    identity = load_identity(str(files[idx]))
    inbox_url = get_inbox_url(identity.email)

    print()

    # Activate email if not already activated
    activation_success = False
    if identity.email_status != "Activated":
        try:
            result = subprocess.run(['curl', '-s', inbox_url], capture_output=True, timeout=10)
            if result.returncode == 0:
                print(f"{GREEN}[+] Email inbox activated successfully!{RESET}\n")
                # Update identity status and save
                identity.email_status = "Activated"
                save_identity(identity, filepath=str(files[idx]))
                activation_success = True
            else:
                print(f"{RED}[-] Could not activate email inbox{RESET}\n")
        except:
            print(f"{RED}[-] Could not activate email inbox{RESET}\n")
    else:
        print(f"{GREEN}[+] Email inbox is already activated{RESET}\n")
        activation_success = True

    # Show URL only if activation successful
    if activation_success:
        print()
        print(f"{BOLD}{YELLOW}Visit this URL to check your emails from your browser:{RESET} {inbox_url}")
        print()

    input(f"{BOLD}Press Enter to return to menu...{RESET}")
    clear_screen()


def delete_specific_identity():
    """
    Delete a specific identity from the list (with confirmation).

    Note: This function is no longer used in the main menu but kept for compatibility.
    """
    files = list_saved_identities()

    if not files:
        print(f"{RED}No saved identities found.{RESET}")
        return

    # Dynamic number formatting
    num_width = len(str(len(files)))

    print(f"{BOLD}{YELLOW}Saved identities:{RESET}\n")

    for i, filepath in enumerate(files):
        identity = load_identity(str(filepath))
        print(f"[{RED}{i:0{num_width}d}{RESET}] {CYAN}{identity.email}{RESET} - {MAGENTA}{identity.website}{RESET}")

    print(f"[{RED}{len(files):0{num_width}d}{RESET}] Return to menu")
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
    """
    Clean all identities with confirmation prompt.
    """
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


def import_identities_menu():
    """
    Import identities from a JSON file.

    Allows user to specify a JSON file path containing one or multiple
    identities to be imported into the identities-generated folder.
    """
    print(f"{BOLD}{YELLOW}Import Identities from JSON{RESET}\n")
    print(f"This option allows you to import identities from a JSON file.")
    print(f"The JSON file can contain:")
    print(f"  - A single identity object")
    print(f"  - An array of identity objects")
    print(f"  - An object with an 'identities' key containing an array\n")

    json_path = input(f"{BOLD}Enter path to JSON file (or Enter to cancel):{RESET} ").strip()

    if not json_path:
        print(f"{YELLOW}Cancelled.{RESET}")
        print()
        input(f"{BOLD}Press Enter to return to menu...{RESET}")
        clear_screen()
        return

    # Check if file exists
    if not Path(json_path).exists():
        print(f"{RED}Error: File not found.{RESET}")
        print()
        input(f"{BOLD}Press Enter to return to menu...{RESET}")
        clear_screen()
        return

    print()
    print(f"{YELLOW}Importing identities...{RESET}")

    # Import identities
    imported, failed = import_identities_from_json(json_path)

    print()
    if imported > 0:
        print(f"{GREEN}✓ Successfully imported {imported} identit{'y' if imported == 1 else 'ies'}.{RESET}")
    if failed > 0:
        print(f"{RED}✗ Failed to import {failed} identit{'y' if failed == 1 else 'ies'}.{RESET}")

    if imported == 0 and failed == 0:
        print(f"{YELLOW}No identities found in the file.{RESET}")

    print()
    input(f"{BOLD}Press Enter to return to menu...{RESET}")
    clear_screen()


def panic_mode_menu():
    """
    Panic/Hacked Mode - Emergency security feature.

    This will:
    1. Export all identities to encrypted JSON
    2. Create encrypted ZIP archive
    3. Upload to file.io for one-time download
    4. Display recovery information
    5. Disable Tails OS persistence (simulated)
    6. Shutdown the system (simulated)
    """
    panic_mode()
    input(f"\n{BOLD}Press Enter to return to menu...{RESET}")
    clear_screen()


def panic_recovery_menu():
    """
    Panic Recovery - Restore identities from encrypted backup.

    This will:
    1. Prompt for encrypted backup file
    2. Decrypt ZIP and JSON with user passphrases
    3. Import all identities
    4. Report success/failure
    """
    panic_recovery()
    input(f"\n{BOLD}Press Enter to return to menu...{RESET}")
    clear_screen()
