import os
import pytest
from playwright.sync_api import Page

BASE_URL   = os.getenv("DEVBOARD_URL",  "https://localhost:3001")
ADMIN_USER = os.getenv("DEVBOARD_USER", "admin")
ADMIN_PASS = os.getenv("DEVBOARD_PASS", "admin")


def do_login(page: Page) -> None:
    page.goto(BASE_URL, timeout=90_000)   # generous for Render cold-start
    page.set_default_timeout(30_000)
    page.locator("#login-screen").wait_for(state="visible")
    page.locator("#login-user").fill(ADMIN_USER)
    page.locator("#login-pass").fill(ADMIN_PASS)
    page.locator("button", has_text="Sign in").click()
    page.locator("#app").wait_for(state="visible")


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    do_login(page)
    return page
