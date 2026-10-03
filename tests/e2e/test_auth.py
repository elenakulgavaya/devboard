import pytest
from playwright.sync_api import Page, expect
from conftest import BASE_URL, ADMIN_USER, ADMIN_PASS, do_login


def test_login_screen_shown_on_first_visit(page: Page):
    page.goto(BASE_URL, timeout=90_000)
    page.set_default_timeout(30_000)
    expect(page.locator("#login-screen")).to_be_visible()
    expect(page.locator("#app")).to_be_hidden()


def test_successful_login_shows_app(page: Page):
    do_login(page)
    expect(page.locator("#app")).to_be_visible()
    expect(page.locator("#login-screen")).to_be_hidden()


def test_invalid_credentials_shows_error(page: Page):
    page.goto(BASE_URL, timeout=90_000)
    page.set_default_timeout(30_000)
    page.locator("#login-screen").wait_for(state="visible")
    page.locator("#login-user").fill(ADMIN_USER)
    page.locator("#login-pass").fill("wrong-password")
    page.locator("button", has_text="Sign in").click()
    expect(page.locator("#login-err")).to_have_text("Invalid credentials.")
    expect(page.locator("#app")).to_be_hidden()


def test_empty_form_shows_validation_error(page: Page):
    page.goto(BASE_URL, timeout=90_000)
    page.set_default_timeout(30_000)
    page.locator("#login-screen").wait_for(state="visible")
    page.locator("button", has_text="Sign in").click()
    expect(page.locator("#login-err")).to_have_text("Enter username and password.")


def test_only_username_filled_shows_validation_error(page: Page):
    page.goto(BASE_URL, timeout=90_000)
    page.set_default_timeout(30_000)
    page.locator("#login-screen").wait_for(state="visible")
    page.locator("#login-user").fill(ADMIN_USER)
    page.locator("button", has_text="Sign in").click()
    expect(page.locator("#login-err")).to_have_text("Enter username and password.")


def test_login_with_enter_key_in_password_field(page: Page):
    page.goto(BASE_URL, timeout=90_000)
    page.set_default_timeout(30_000)
    page.locator("#login-screen").wait_for(state="visible")
    page.locator("#login-user").fill(ADMIN_USER)
    page.locator("#login-pass").fill(ADMIN_PASS)
    page.locator("#login-pass").press("Enter")
    expect(page.locator("#app")).to_be_visible()


def test_login_with_enter_key_in_username_field(page: Page):
    page.goto(BASE_URL, timeout=90_000)
    page.set_default_timeout(30_000)
    page.locator("#login-screen").wait_for(state="visible")
    page.locator("#login-user").fill(ADMIN_USER)
    page.locator("#login-user").press("Enter")
    # no credentials yet — should show validation, not crash
    expect(page.locator("#login-screen")).to_be_visible()


def test_api_key_stored_in_localstorage_after_login(logged_in_page: Page):
    key = logged_in_page.evaluate("() => localStorage.getItem('devboard_api_key')")
    assert key and len(key) > 0


def test_logout_shows_login_screen(logged_in_page: Page):
    logged_in_page.locator("button", has_text="Sign out").click()
    expect(logged_in_page.locator("#login-screen")).to_be_visible()
    expect(logged_in_page.locator("#app")).to_be_hidden()


def test_logout_clears_localstorage(logged_in_page: Page):
    logged_in_page.locator("button", has_text="Sign out").click()
    key = logged_in_page.evaluate("() => localStorage.getItem('devboard_api_key')")
    assert key is None


def test_login_form_cleared_after_logout(logged_in_page: Page):
    logged_in_page.locator("button", has_text="Sign out").click()
    expect(logged_in_page.locator("#login-user")).to_have_value("")
    expect(logged_in_page.locator("#login-pass")).to_have_value("")
    expect(logged_in_page.locator("#login-err")).to_have_text("")
