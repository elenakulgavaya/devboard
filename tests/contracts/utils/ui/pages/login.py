import random

from surety.ui import Button, Container, Label, Page, TextInput
from surety.ui.browser import Elements

from tests.contracts.utils.ui.pages.base import BasePage


class LoginPage(BasePage):
    UserInput = TextInput(css='#login-user')
    PasswordInput = TextInput(css='#login-pass')
    ErrorMessage = Label(css='#login-err')
    LoginButton = Button(css='button')
