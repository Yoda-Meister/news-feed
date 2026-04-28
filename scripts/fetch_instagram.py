"""
fetch_instagram.py

Fetches the latest Instagram posts for each account listed in config.json
using an instaloader session loaded from the INSTAGRAM_SESSION_B64 env var.
Writes results to public/data/instagram.json.
"""

import base64
import itertools
import json
import os
import random
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import instaloader

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "public" / "config.json"
OUTPUT_PATH = REPO_ROOT / "public" / "data" / "instagram.json"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
POSTS_PER_ACCOUNT = 15
SLEEP_BETWEEN_ACCOUNTS = (4, 9)   # seconds, randomised
MAX_RETRIES = 3
RETRY_BASE_SLEEP = 60              # seconds for first retry back-off


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------
def build_loader(session_path: str, username: str) -> instaloader.Instaloader:
    L = instaloader.Instaloader(
        sleep=True,
        quiet=False,
        request_timeout=30,
        dirname_pattern="",     # we never download files
        filename_pattern="",
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
    )
    L.load_session_from_file(username, session_path)
    return L


def write_session_from_env() -> str:
    """Decode INSTAGRAM_SESSION_B64 into a temp file, return the path."""
    b64 = os.environ.get("INSTAGRAM_SESSION_B64", "").strip()
    if not b64:
        raise RuntimeError(
            "INSTAGRAM_SESSION_B64 env var is not set. "
            "Run scripts/create_session.py locally to generate it."
        )
    session_bytes = base64.b64decode(b64)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".session")
    tmp.write(session_bytes)
    tmp.close()
    return tmp.name


# ---------------------------------------------------------------------------
# Post serialisation
# ---------------------------------------------------------------------------
def post_to_dict(post: instaloader.Post) -> dict:
    return {
        "shortcode": post.shortcode,
        "post_url": f"https://www.instagram.com/p/{post.shortcode}/",
        "owner_username": post.owner_username,
        "timestamp_utc": post.date_utc.replace(tzinfo=timezone.utc).isoformat(),
        "caption": post.caption,
        "likes": post.likes,
        "comments": post.comments,
        "is_video": post.is_video,
        "mediacount": post.mediacount,
    }


# ---------------------------------------------------------------------------
# Fetching with retry
# ---------------------------------------------------------------------------
def fetch_posts_for_account(
    L: instaloader.Instaloader, username: str
) -> list[dict]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            posts = []
            for post in itertools.islice(profile.get_posts(), POSTS_PER_ACCOUNT):
                posts.append(post_to_dict(post))
            return posts
        except instaloader.exceptions.TooManyRequestsException as exc:
            sleep_secs = RETRY_BASE_SLEEP * (2 ** (attempt - 1))
            print(
                f"  [rate-limited] {username} attempt {attempt}/{MAX_RETRIES} "
                f"— sleeping {sleep_secs}s ({exc})",
                file=sys.stderr,
            )
            if attempt == MAX_RETRIES:
                print(f"  [skip] {username} — giving up after {MAX_RETRIES} retries", file=sys.stderr)
                return []
            time.sleep(sleep_secs)
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"  [skip] {username} — profile does not exist", file=sys.stderr)
            return []
        except Exception as exc:  # noqa: BLE001
            print(f"  [error] {username}: {exc}", file=sys.stderr)
            return []
    return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    config = load_config()
    accounts: list[str] = config.get("instagram_accounts", [])
    if not accounts:
        print("No accounts in config.json — nothing to do.", file=sys.stderr)
        sys.exit(0)

    username = os.environ.get("INSTAGRAM_USERNAME", "").strip()
    if not username:
        raise RuntimeError("INSTAGRAM_USERNAME env var is not set.")

    session_path = write_session_from_env()
    try:
        L = build_loader(session_path, username)

        results: dict[str, list[dict]] = {}
        for i, account in enumerate(accounts):
            print(f"Fetching {account} ({i + 1}/{len(accounts)})…")
            results[account] = fetch_posts_for_account(L, account)
            print(f"  → {len(results[account])} posts")

            # Sleep between accounts to avoid rate limiting, except after last
            if i < len(accounts) - 1:
                sleep_secs = random.uniform(*SLEEP_BETWEEN_ACCOUNTS)
                time.sleep(sleep_secs)

        output = {
            "accounts": results,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\nWrote {OUTPUT_PATH}")
    finally:
        os.unlink(session_path)


if __name__ == "__main__":
    main()
