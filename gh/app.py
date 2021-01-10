import hmac
import hashlib
import json

from fastapi import FastAPI
from starlette.requests import Request

from gh.bot import GithubBot
from gh.event import WebhookEvent
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
    body = await request.body()
    if validate_signature(signature, bytes(body)):
        data = json.loads(body.decode())
        event = WebhookEvent.from_request(data, request)
        await bot.dispatch(event)


def validate_signature(signature, body):
    real_signature = "sha256=" + hmac.new(GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(real_signature, signature)

