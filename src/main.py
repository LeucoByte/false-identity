#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synthetic Identity Generator - Main Entry Point

A tool for generating realistic synthetic identities for privacy protection,
research, and software testing purposes.

Author: Leucocito
GitHub: https://github.com/LeucoByte
"""

import signal

from config import BOLD, RED, GREEN, YELLOW, CYAN, RESET
from ui.display import signal_handler, clear_screen, print_banner, print_warnings
from ui.menus import (
    generate_new_identity,
    view_saved_identities,
    check_emails,
    clean_all_identities_menu,
    import_identities_menu,
    panic_mode_menu,
    panic_recovery_menu
)


def main():
    """
    Main entry point with interactive menu system.

    Displays banner, warnings, and main menu options.
    Handles user input and navigation between features.
    """
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Clear screen on startup
    clear_screen()

    while True:
        # Display banner and warnings
        print_banner()
        print_warnings()

        # Main menu
        print(f"{BOLD}{YELLOW}What would you like to do?{RESET}")
        options = [
            "Generate new identity",
            "View saved identities",
            "Check email inbox",
            "Import identities from JSON",
            "Clean all identities",
            f"{RED}PANIC / HACKED MODE{RESET}",
            f"{CYAN}PANIC RECOVERY (Import encrypted backup){RESET}"
        ]

        for i, opt in enumerate(options):
            print(f"    [{RED}{i}{RESET}] {opt}")

        print(f"    [{RED}Enter{RESET}] Exit")
        print()

        choice = input(f"{BOLD}Select option:{RESET} ").strip()
        print()

        # Handle menu selection
        if choice == '':
            # Exit on Enter
            clear_screen()
            print(f"\n{BOLD}{GREEN}Goodbye!{RESET}\n")
            break
        elif choice == '0':
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
            import_identities_menu()
        elif choice == '4':
            clear_screen()
            clean_all_identities_menu()
        elif choice == '5':
            clear_screen()
            panic_mode_menu()
        elif choice == '6':
            clear_screen()
            panic_recovery_menu()
        else:
            print(f"{RED}Invalid option. Please try again.{RESET}\n")


if __name__ == "__main__":
    main()
