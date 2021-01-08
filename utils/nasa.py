import aiohttp
import aionasa

from auth import NASA_API_KEY


class NASA:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.apod = aionasa.APOD(NASA_API_KEY, session=self.session)
        self.insight = aionasa.InSight(NASA_API_KEY, session=self.session)
        self.epic = aionasa.EPIC(NASA_API_KEY, session=self.session)
        self.neows = aionasa.NeoWs(NASA_API_KEY, session=self.session)
        self.exoplanet = aionasa.Exoplanet(NASA_API_KEY, session=self.session)

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

