import urllib.parse

from decimal import ROUND_HALF_UP, Decimal

from surety.sdk.fakeable import fake_string_attr
from surety import (
    Array, Bool, DateTime, Enum, Float, Dictionary, Int, Raw, String, Uuid,
)
from surety.api import ApiContract, HttpMethod
from surety.config import Cfg
from surety.sdk import dates
from surety.sdk.fakeable import fake


SERVICE = 'api/auth/'
BASE_URL = Cfg.App.api_url


class LoginRequest(Dictionary):
    Username = String(name='username')
    Password = String(name='password')


class LoginResponse(Dictionary):
    ApiKey = String(name='api_key')


class ErrorResponse(Dictionary):
    Details = String(name='details')


class Login(ApiContract):
    method = HttpMethod.POST
    url = 'login'
    req_body = LoginRequest
    resp_body = LoginResponse
