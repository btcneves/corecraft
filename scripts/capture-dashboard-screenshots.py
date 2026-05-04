#!/usr/bin/env python3
"""Capture full-page screenshots for the three CoreCraft dashboards."""

from pathlib import Path

from playwright.sync_api import Page, sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT_DIR / "docs" / "assets"
VIEWPORT = {"width": 1440, "height": 900}
DASHBOARDS = [
    ("http://localhost/atividade-1/", "activity-1-dashboard.png"),
    ("http://localhost/atividade-2/", "activity-2-events.png"),
    ("http://localhost/atividade-3/", "activity-3-wallet.png"),
]


def capture(page: Page, url: str, filename: str) -> None:
    output_path = ASSETS_DIR / filename
    page.goto(url, wait_until="networkidle", timeout=60_000)
    page.screenshot(path=output_path, full_page=True)
    print(f"saved {output_path.relative_to(ROOT_DIR)}")


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT)
        try:
            for url, filename in DASHBOARDS:
                capture(page, url, filename)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
