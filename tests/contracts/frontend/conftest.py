import pytest

from surety.ui import Browser, pytest_addons


@pytest.fixture(scope='session', autouse=True)
def close_browser():
    yield
    Browser().driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    pytest_addons.save_screenshot_on_failure(outcome, item)
