import os

from surety.ui import Button, Container, Page


class BasePage(Page):
    base_url = os.getenv('DEVBOARD_URL',  'http://localhost:3010')

    LoginScreen = Container(css='#login-screen')
    AppScreen = Container(css='#app')
    LogoutButton = Button(css='button[onclick^=logout]')
