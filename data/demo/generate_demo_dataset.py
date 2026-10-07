#!/usr/bin/env python3
"""Generates the SignalLens demo dataset.

IMPORTANT — disclosure (ARCHITECTURE.md §41/§24): the review TEXT in this dataset is
synthetically generated from varied templates, not scraped from Kaggle or any real app
store. This environment has no Kaggle API credentials configured, so rather than silently
fabricate a "real dataset" or depend on credentials we don't have, we generate a clearly
template-based corpus with enough lexical variation to be analytically meaningful, and we
say so here and in the README. app_version/platform/device/country metadata is synthetic
by design (ARCHITECTURE.md §24), deliberately engineered to reproduce the documented demo
story: a Payment Failure spike concentrated on Android v4.8.1 shortly after its release.

Usage:
    python generate_demo_dataset.py [--count 10000] [--out ../demo/signallens_demo.csv]
"""

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

TODAY = date(2026, 10, 1)

# (version, release_date) timeline. v4.8.1 is the regression release the demo story pivots on.
VERSION_TIMELINE = [
    ("4.7.8", TODAY - timedelta(days=58)),
    ("4.7.9", TODAY - timedelta(days=44)),
    ("4.8.0", TODAY - timedelta(days=30)),
    ("4.8.1", TODAY - timedelta(days=14)),  # regression release
    ("4.8.2", TODAY - timedelta(days=3)),
]

PLATFORMS = ["Android", "iOS"]
ANDROID_DEVICES = ["Samsung Galaxy S23", "Samsung Galaxy A54", "Google Pixel 8", "OnePlus 11", "Xiaomi 13"]
IOS_DEVICES = ["iPhone 14", "iPhone 13", "iPhone SE", "iPhone 15 Pro"]
COUNTRIES = ["India", "United States", "United Kingdom", "Brazil", "Indonesia", "Germany", "Nigeria"]

# --- Complaint categories: (category, severity-ish keyword set, templates, base rating range) ---
PAYMENT_TEMPLATES = [
    "Payment failed after the {v} update, money was deducted but the order never went through.",
    "UPI transaction rejected every single time since I updated to {v}. Lost confidence in this app.",
    "Card payment stuck on 'processing' for 20 minutes then failed. Happened right after {v}.",
    "Tried to pay three times, all failed, but my bank shows the money was deducted.",
    "Checkout is broken — payment keeps failing and support hasn't replied in two days.",
    "Since {v} the payment gateway times out constantly. This is costing me real money.",
    "Duplicate charge on my card for the same order after a failed payment attempt.",
    "Transaction failed but the amount was debited from my account, no refund yet.",
]

CRASH_TEMPLATES = [
    "The app crashes every time I open it since the last update.",
    "App freezes on the home screen and I have to force close it constantly.",
    "Keeps crashing when I try to check out, completely unusable right now.",
    "Opened the app and it immediately closed itself, happens every time now.",
    "App won't even launch anymore after updating, just crashes on splash screen.",
]

OTP_TEMPLATES = [
    "OTP never arrived, tried five times, couldn't log in for 20 minutes.",
    "Login code delayed by several minutes, very frustrating when I need to log in quickly.",
    "Can't log in — the verification code just doesn't show up anymore.",
    "OTP delivery is unreliable lately, missed two deliveries because I couldn't log in in time.",
]

PERFORMANCE_TEMPLATES = [
    "App has gotten really slow and laggy since the recent update.",
    "Takes forever to load the home screen now, used to be instant.",
    "Scrolling is choppy and the app lags whenever I open a product page.",
    "Everything feels sluggish, the app used to be so much faster.",
]

UI_TEMPLATES = [
    "The new layout is confusing, I can't find the settings menu anymore.",
    "Buttons are way too small on my screen, hard to tap the right one.",
    "The redesign makes it harder to find what I'm looking for.",
    "Dark mode has some ugly color contrast issues in the new UI.",
]

SEARCH_TEMPLATES = [
    "Search results are completely irrelevant to what I typed.",
    "Can't find products I know exist, search just doesn't work well.",
    "Search returns random unrelated items, really needs improvement.",
]

SUPPORT_TEMPLATES = [
    "Contacted support three days ago and still no response.",
    "Customer service chat just disconnects without resolving anything.",
    "Support team is unhelpful and takes forever to reply.",
]

POSITIVE_TEMPLATES = [
    "The new UI is beautiful and so much easier to navigate.",
    "Really impressed with how fast and smooth the app feels now.",
    "Customer support helped me resolve my issue within minutes, great experience.",
    "Love the new features in the latest update, well done team.",
    "This app just keeps getting better, checkout was effortless this time.",
    "Great experience overall, delivery was fast and the app worked perfectly.",
]

NEUTRAL_TEMPLATES = [
    "App works as expected, nothing special to report either way.",
    "It does what it says, no major complaints but nothing amazing either.",
    "Average experience, some features are good, others need work.",
]


def _pick_version(bias_recent: bool = False) -> tuple[str, date]:
    if bias_recent and random.random() < 0.7:
        return VERSION_TIMELINE[3]  # 4.8.1
    return random.choice(VERSION_TIMELINE)


def _review_date_after(release_date: date, max_days_after: int = 13) -> date:
    offset = random.randint(0, max_days_after)
    d = release_date + timedelta(days=offset)
    return min(d, TODAY)


def _device_for_platform(platform: str) -> str:
    return random.choice(ANDROID_DEVICES if platform == "Android" else IOS_DEVICES)


def generate_rows(count: int) -> list[dict]:
    rows = []

    # --- The deliberate incident: Payment Failure spike on Android v4.8.1 (~9% of dataset) ---
    n_payment_spike = int(count * 0.09)
    version, release_date = VERSION_TIMELINE[3]
    for _ in range(n_payment_spike):
        platform = "Android" if random.random() < 0.87 else "iOS"
        text = random.choice(PAYMENT_TEMPLATES).format(v=version)
        rows.append(
            {
                "review": text,
                "rating": random.choice([1, 1, 1, 2, 2]),
                "date": _review_date_after(release_date).isoformat(),
                "app_version": version if platform == "Android" else random.choice(["4.8.0", "4.8.1"]),
                "platform": platform,
                "device": _device_for_platform(platform),
                "country": random.choice(COUNTRIES),
            }
        )

    # --- A small baseline trickle of payment complaints pre-regression (so growth % is meaningful) ---
    n_payment_baseline = int(count * 0.015)
    for _ in range(n_payment_baseline):
        version, release_date = random.choice(VERSION_TIMELINE[:3])
        platform = random.choice(PLATFORMS)
        rows.append(
            {
                "review": random.choice(PAYMENT_TEMPLATES).format(v=version),
                "rating": random.choice([1, 2]),
                "date": _review_date_after(release_date, max_days_after=12).isoformat(),
                "app_version": version,
                "platform": platform,
                "device": _device_for_platform(platform),
                "country": random.choice(COUNTRIES),
            }
        )

    # --- Other steady-state issue categories ---
    other_categories = [
        (CRASH_TEMPLATES, 0.06, (1, 2)),
        (OTP_TEMPLATES, 0.05, (2, 3)),
        (PERFORMANCE_TEMPLATES, 0.06, (2, 3)),
        (UI_TEMPLATES, 0.05, (2, 3)),
        (SEARCH_TEMPLATES, 0.03, (2, 3)),
        (SUPPORT_TEMPLATES, 0.04, (1, 2)),
    ]
    for templates, fraction, rating_range in other_categories:
        for _ in range(int(count * fraction)):
            version, release_date = _pick_version()
            platform = random.choice(PLATFORMS)
            rows.append(
                {
                    "review": random.choice(templates),
                    "rating": random.randint(*rating_range),
                    "date": _review_date_after(release_date, max_days_after=40).isoformat(),
                    "app_version": version,
                    "platform": platform,
                    "device": _device_for_platform(platform),
                    "country": random.choice(COUNTRIES),
                }
            )

    # --- Positive / neutral majority to make the dataset realistic ---
    remaining = count - len(rows)
    for _ in range(max(remaining, 0)):
        version, release_date = _pick_version()
        platform = random.choice(PLATFORMS)
        is_positive = random.random() < 0.75
        text = random.choice(POSITIVE_TEMPLATES if is_positive else NEUTRAL_TEMPLATES)
        rating = random.choice([4, 5, 5]) if is_positive else random.choice([3, 3, 4])
        rows.append(
            {
                "review": text,
                "rating": rating,
                "date": _review_date_after(release_date, max_days_after=40).isoformat(),
                "app_version": version,
                "platform": platform,
                "device": _device_for_platform(platform),
                "country": random.choice(COUNTRIES),
            }
        )

    # --- Inject a suspicious duplicate burst for the Feedback Integrity demo ---
    burst_text = "Payment failed after the 4.8.1 update, money was deducted but the order never went through."
    burst_day = VERSION_TIMELINE[3][1] + timedelta(days=5)
    for _ in range(20):
        rows.append(
            {
                "review": burst_text,
                "rating": 1,
                "date": burst_day.isoformat(),
                "app_version": "4.8.1",
                "platform": "Android",
                "device": random.choice(ANDROID_DEVICES),
                "country": "India",
            }
        )

    # --- Inject a handful of rating/text conflicts for the integrity demo ---
    for _ in range(15):
        version, release_date = _pick_version()
        rows.append(
            {
                "review": random.choice(
                    [
                        "Worst update ever, nothing works, terrible experience overall.",
                        "Absolutely awful, the app is broken and useless now.",
                        "Horrible, I hate what they did to this app.",
                    ]
                ),
                "rating": 5,  # deliberate contradiction
                "date": _review_date_after(release_date, max_days_after=40).isoformat(),
                "app_version": version,
                "platform": random.choice(PLATFORMS),
                "device": random.choice(ANDROID_DEVICES + IOS_DEVICES),
                "country": random.choice(COUNTRIES),
            }
        )

    random.shuffle(rows)
    for i, row in enumerate(rows, start=1):
        row["review_id"] = f"demo-{i:06d}"
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10000)
    parser.add_argument("--out", type=str, default=str(Path(__file__).parent / "signallens_demo.csv"))
    args = parser.parse_args()

    rows = generate_rows(args.count)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["review_id", "review", "rating", "date", "app_version", "platform", "device", "country"]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Wrote {len(rows)} synthetic demo reviews to {out_path}")
    print("NOTE: review text is template-generated, not scraped from a real app store (see module docstring).")


if __name__ == "__main__":
    main()
