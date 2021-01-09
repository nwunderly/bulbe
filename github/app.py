import hmac
import hashlib
import json

from fastapi import FastAPI
from starlette.requests import Request

from github.bot import GithubBot
from auth import GITHUB_WEBHOOK_SECRET


app = FastAPI(redoc_url=None, docs_url=None)
bot = GithubBot()


@app.on_event('startup')
async def startup():
    pass


@app.on_event('shutdown')
async def cleanup():
    pass


@app.post('/api')
async def post_api(request: Request):
    signature = request.headers['X-Hub-Signature-256']
    print(f"{signature=}")
    body = await request.body()
    if validate_signature(signature, bytes(body)):
        data = json.loads(body.decode())
        print(data)
        # event = WebhookEvent(data, request)
        # await bot.on_event(event)


def validate_signature(signature, body):
    real_signature = "sha256=" + hmac.new(GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    print(f"{real_signature=}")
    if hmac.compare_digest(real_signature, signature):
        print("VALID SIGNATURE")
        return True
    else:
        print("INVALID SIGNATURE")
        return False

