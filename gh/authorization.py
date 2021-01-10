import jwt
import aiohttp

from datetime import datetime, timedelta, timezone
from jwt.utils import get_int_from_datetime

from auth import GITHUB_PEM_FILE, GITHUB_APP_ID

instance = jwt.JWT()


def new_jwt():
    """Generate a new JSON Web Token signed by RSA private key."""
    with open(GITHUB_PEM_FILE, 'rb') as fp:
        signing_key = jwt.jwk_from_pem(fp.read())
    payload = {
        'iat': get_int_from_datetime(datetime.now()),
        'exp': get_int_from_datetime(datetime.now(timezone.utc) + timedelta(minutes=10)),
        'iss': GITHUB_APP_ID
    }
    compact_jws = instance.encode(payload, signing_key, alg='RS256')
    return compact_jws


async def new_token(_jwt):
    authorization = f"Bearer {_jwt}"
    headers = {
        "Authorization": authorization,
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/app/installations/{GITHUB_APP_ID}/access_tokens"
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers) as resp:
            print(resp.status)
            token = await resp.read()
    return token


async def get_installation(_jwt):
    authorization = f"Bearer {_jwt}"
    headers = {
        "Authorization": authorization,
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/app/installations/{GITHUB_APP_ID}"
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            print(resp.status)
            print(await resp.read())


