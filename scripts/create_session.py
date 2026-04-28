"""
create_session.py  —  run this ONCE locally to create an instaloader session
file that can be base64-encoded and stored as a GitHub Actions secret.

Usage:
    python scripts/create_session.py

What it does:
  1. Prompts for your dedicated Instagram scraper account credentials.
  2. Calls instaloader's login flow (handles 2FA prompts if needed).
  3. Saves a session file to ./ig_session (in the repo root).
  4. Prints the base64-encoded value ready to paste as the
     INSTAGRAM_SESSION_B64 GitHub Actions secret.
  5. Deletes the local session file so it is never committed.

IMPORTANT: Use a DEDICATED, THROWAWAY Instagram account, not your personal one.
           Disable 2FA on that account before running this script.
           Never commit the session file or its base64 value to the repo.
"""

import base64
import getpass
import os
import sys
from pathlib import Path

import instaloader

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSION_FILE = REPO_ROOT / "ig_session"


def main() -> None:
    print("─── Instagram Session Creator ─────────────────────────────────")
    print("Use a dedicated scraper account, NOT your personal Instagram.")
    print()

    username = input("Instagram username: ").strip()
    if not username:
        sys.exit("Username cannot be empty.")

    password = getpass.getpass("Password: ")
    if not password:
        sys.exit("Password cannot be empty.")

    L = instaloader.Instaloader()

    try:
        L.login(username, password)
    except instaloader.exceptions.BadCredentialsException:
        sys.exit("Login failed: bad credentials.")
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        code = input("2FA code: ").strip()
        try:
            L.two_factor_login(code)
        except instaloader.exceptions.BadCredentialsException:
            sys.exit("2FA login failed: invalid code.")

    L.save_session_to_file(str(SESSION_FILE))
    print(f"\nSession saved to: {SESSION_FILE}")

    with open(SESSION_FILE, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    print("\n── Copy everything between the lines and paste as the ──────────")
    print("── INSTAGRAM_SESSION_B64 GitHub Actions secret: ────────────────")
    print("─" * 65)
    print(b64)
    print("─" * 65)
    print(f"\nINSTAGRAM_USERNAME secret value: {username}")
    print("\nAlso add that username as the INSTAGRAM_USERNAME secret.")

    # Remove local session file so it cannot accidentally be committed
    SESSION_FILE.unlink()
    print(f"\nLocal session file deleted. It will NOT be committed to git.")
    print("Done.")


if __name__ == "__main__":
    main()
