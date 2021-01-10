import asyncio
import github

from gh.authorization import new_jwt, new_token, get_installation


class GithubBot:
    def __init__(self, token):
        self.client = github.GitHub(token)


async def main():
    jwt = new_jwt()
    print("jwt", jwt)

    print(await get_installation(jwt))

    token = await new_token(jwt)
    print("token", token)
    g = GithubBot(token)
    repo = await g.client.fetch_repository("nwunderly", "bulbe")
    print(repo.license.name)


asyncio.run(main())
