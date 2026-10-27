import pytest
from selenium.webdriver import Keys

from surety.sdk.fakeable import fake
from surety.ui import LocalStorage

from tests.contracts.utils.ui import local_db
from tests.contracts.utils.ui.pages.login import LoginPage
from tests.contracts.utils.api import auth, tasks
from tests.contracts.utils.ui.pages.tasks import TasksPage


@pytest.fixture(scope='module', autouse=True)
def open_login_page():
    LoginPage.open()


def test_login_screen_on_page_load():
    assert LoginPage.LoginScreen.is_present()


@pytest.fixture(scope='module')
def submit_empty(open_login_page):
    LoginPage.LoginButton.click()


def test_empty_form_shows_validation_error(submit_empty):
    LoginPage.ErrorMessage.verify_text('Enter username and password.')


@pytest.fixture(scope='module')
def username(submit_empty):
    value = fake.user_name()
    LoginPage.UserInput.input(value)
    return value


def test_username_in_the_input_field(username):
    LoginPage.UserInput.verify_value(username)


@pytest.fixture(scope='module')
def submit_username(username):
    LoginPage.LoginButton.click()


def test_only_username_shows_validation_error(submit_username):
    LoginPage.ErrorMessage.verify_text('Enter username and password.')


@pytest.fixture(scope='module')
def password(submit_username):
    value = fake.password()
    LoginPage.PasswordInput.input(value)
    return value


def test_password_in_the_input_field(password):
    LoginPage.PasswordInput.verify_value(password)



@pytest.fixture(scope='module')
def submit_failed(password):
    auth.Login.reply(status=401, body=auth.ErrorResponse.with_values({
        auth.ErrorResponse.Details.name: 'Invalid credentials'
    }), reset=True)
    LoginPage.LoginButton.click()


def test_invalid_credentials_error(submit_failed):
    LoginPage.ErrorMessage.wait_for_text('Invalid credentials.')


def test_auth_request(username, password, submit_failed):
    auth.Login.verify_called(expected=auth.LoginRequest.with_values({
        auth.LoginRequest.Username.name: username,
        auth.LoginRequest.Password.name: password,
    }))


def test_password_cleared_on_failure(submit_failed):
    LoginPage.PasswordInput.verify_value('')


@pytest.fixture(scope='module')
def enter_in_password_field(submit_failed, password):
    auth.Login.reply(status=401, body=auth.ErrorResponse.with_values({
        auth.ErrorResponse.Details.name: 'Invalid credentials'
    }), reset=True)
    LoginPage.PasswordInput.input(password)
    LoginPage.PasswordInput.send_keys(Keys.ENTER)


def test_auth_request_on_password_enter(username, password,
                                        enter_in_password_field):
    auth.Login.verify_called(expected=auth.LoginRequest.with_values({
        auth.LoginRequest.Username.name: username,
        auth.LoginRequest.Password.name: password,
    }), timeout=2)


def test_password_cleared_on_enter_failure(enter_in_password_field):
    LoginPage.PasswordInput.verify_value('')


@pytest.fixture(scope='module')
def enter_in_username_field(enter_in_password_field, password):
    auth.Login.reply(status=401, body=auth.ErrorResponse.with_values({
        auth.ErrorResponse.Details.name: 'Invalid credentials'
    }), reset=True)
    LoginPage.PasswordInput.input(password)
    LoginPage.UserInput.send_keys(Keys.ENTER)


def test_auth_request_on_username_enter(username, password,
                                        enter_in_username_field):
    auth.Login.verify_called(expected=auth.LoginRequest.with_values({
        auth.LoginRequest.Username.name: username,
        auth.LoginRequest.Password.name: password,
    }), timeout=2)


def test_password_cleared_on_username_enter_failure(enter_in_username_field):
    LoginPage.PasswordInput.verify_value('')


@pytest.fixture(scope='module')
def login(enter_in_username_field, password):
    LoginPage.PasswordInput.input(password)
    api_key = fake.password()
    auth.Login.reply(body=auth.LoginResponse.with_values({
        auth.LoginResponse.ApiKey.name: api_key,
    }), reset=True)
    tasks.GetTasks.reply(times=2)
    tasks.GetTasksAssignees.reply()
    LoginPage.LoginButton.click()

    return api_key


def test_login_passed(login):
    assert LoginPage.LoginScreen.is_not_present()


def test_app_page_opened(login):
    assert TasksPage.AppScreen.is_present()


def test_login_request(login, username, password):
    auth.Login.verify_called(expected=auth.LoginRequest.with_values({
        auth.LoginRequest.Username.name: username,
        auth.LoginRequest.Password.name: password,
    }))


def test_localstorage_api_key(login):
    assert LocalStorage.get_item(local_db.Keys.ApiKey) == login


@pytest.fixture(scope='module')
def logout(login):
    TasksPage.LogoutButton.click()


def test_redirected_to_login_page_on_logout(logout):
    assert LoginPage.LoginScreen.is_present()


def test_localstorage_clears_on_logout(logout):
    assert LocalStorage.get_item(local_db.Keys.ApiKey) is None


def test_username_cleared_on_logout(logout):
    LoginPage.UserInput.verify_value('')


def test_password_cleared_on_logout(logout):
    LoginPage.PasswordInput.verify_value('')
