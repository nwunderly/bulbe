from gh.types import Repository, User, WikiPage


class WebhookEvent:
    """Base webhook event class."""

    def __init__(self, body, request):
        self._json = body
        self._request = request
        self._event_type = request.headers.get("X-GitHub-Event")

    @classmethod
    def from_request(cls, body, request):
        event_type = request.headers["X-GitHub-Event"]

        _cls = {
            "gollum": Gollum,
        }.get(event_type)

        if _cls:
            return _cls(body, request)

    async def dispatch(self, bot):
        pass


class Gollum(WebhookEvent):
    """Event representing a wiki page edit."""

    def __init__(self, body, request):
        super().__init__(body, request)
        self.pages = [WikiPage(page) for page in body["pages"]]
        self.repository = Repository(body["repository"])
        self.sender = User(body["sender"])
        self.installation = body["installation"]
