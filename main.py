from __future__ import annotations

import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import (
    JavascriptException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


REELS_URL = "https://www.instagram.com/reels/"
PAGE_WAIT_SECONDS = 300
MAX_REEL_WAIT_SECONDS = 180
SCROLL_PAUSE_SECONDS = 1.5
EDGE_TEST_PROFILE = Path.home() / "insta-web-scroller-edge-profile"


def create_driver() -> webdriver.Edge:
    """Start Edge with a profile dedicated to this project."""
    EDGE_TEST_PROFILE.mkdir(parents=True, exist_ok=True)
    options = webdriver.EdgeOptions()
    options.add_argument(f"--user-data-dir={EDGE_TEST_PROFILE}")
    options.add_argument("--start-maximized")
    return webdriver.Edge(options=options)


def is_reels_page(driver: webdriver.Edge) -> bool:
    """Return whether the browser is currently on Instagram's Reels page."""
    return "instagram.com/reels" in driver.current_url.lower()


def wait_for_reels_page(driver: webdriver.Edge) -> None:
    """Wait for the user to finish logging in and reach the Reels page."""
    print("Edge opened Instagram Reels.")
    print("This is a separate testing profile for the scroller.")
    print("Log in to Instagram in this Edge window when prompted.")
    print(f"Waiting up to {PAGE_WAIT_SECONDS} seconds for the Reels page...")

    try:
        WebDriverWait(driver, PAGE_WAIT_SECONDS).until(
            lambda current_driver: is_reels_page(current_driver)
        )
    except TimeoutException as exc:
        raise TimeoutException(
            "The Instagram Reels page was not detected. "
            "Log in and open https://www.instagram.com/reels/ in the Edge window."
        ) from exc

    print("\nSUCCESS: Instagram Reels page detected.")
    print("Each Reel will play until its video finishes, then the next Reel will be selected.")
    print("Press Ctrl+C in this terminal to stop.\n")


def select_next_reel(driver: webdriver.Edge) -> None:
    """Scroll once to the next full-screen Reel, with a keyboard fallback."""
    before = driver.execute_script("return window.scrollY;")
    try:
        ActionChains(driver).scroll_by_amount(0, 700).perform()
    except WebDriverException:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
    time.sleep(SCROLL_PAUSE_SECONDS)
    after = driver.execute_script("return window.scrollY;")
    if after == before:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(SCROLL_PAUSE_SECONDS)


def wait_for_current_reel(driver: webdriver.Edge) -> float:
    """Wait for the visible Reel to finish and return its detected duration."""
    print("Reading the current Reel duration...")
    started_at = time.monotonic()
    last_duration = 0.0
    previous_time = 0.0
    last_progress_at = started_at

    while True:
        try:
            state = driver.execute_script(
                """
                const videos = [...document.querySelectorAll('video')];
                const visible = videos
                    .filter(video => {
                        const rect = video.getBoundingClientRect();
                        return rect.width > 0 && rect.height > 0;
                    })
                    .sort((a, b) => b.getBoundingClientRect().height -
                                   a.getBoundingClientRect().height)[0];
                if (!visible) return null;
                return {
                    duration: Number.isFinite(visible.duration) ? visible.duration : 0,
                    currentTime: visible.currentTime,
                    ended: visible.ended,
                };
                """
            )
        except JavascriptException:
            state = None

        if state:
            duration = float(state["duration"])
            current_time = float(state["currentTime"])
            last_duration = max(last_duration, duration)
            looped = (
                duration > 0
                and previous_time > 2
                and current_time < previous_time - 1
            )
            if state["ended"] or looped or (duration > 0 and current_time >= duration - 0.25):
                return last_duration
            if current_time > previous_time:
                last_progress_at = time.monotonic()
            previous_time = current_time

        # Instagram may leave a rendered video paused while loading the next Reel.
        # Advance instead of blocking the feed when playback stops progressing.
        if time.monotonic() - last_progress_at >= 15:
            print("The current Reel stopped reporting playback; advancing.")
            return last_duration
        if time.monotonic() - started_at >= MAX_REEL_WAIT_SECONDS:
            print("The Reel did not expose a completion event; advancing now.")
            return last_duration
        time.sleep(0.5)


def run() -> None:
    driver: webdriver.Edge | None = None
    try:
        print("Launching Microsoft Edge...")
        driver = create_driver()
        driver.get(REELS_URL)
        wait_for_reels_page(driver)

        reel_number = 1
        while True:
            duration = wait_for_current_reel(driver)
            select_next_reel(driver)
            reel_number += 1
            if duration:
                print(f"Reel finished after approximately {duration:.1f} seconds.")
            else:
                print("Reel duration was unavailable; moved to the next Reel.")
            print(f"Moved to reel {reel_number}.")
    except KeyboardInterrupt:
        print("\nInsta Scroller stopped.")
    except (RuntimeError, WebDriverException) as exc:
        print(f"\nBrowser automation stopped: {exc}")
    finally:
        if driver is not None:
            driver.quit()
            print("Edge closed.")


if __name__ == "__main__":
    run()
