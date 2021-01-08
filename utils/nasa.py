import aionasa

from auth import NASA_API_KEY


class NASA:
    def __init__(self, session):
        self.session = session
        self.apod = aionasa.APOD(NASA_API_KEY, session=self.session)
        self.insight = aionasa.InSight(NASA_API_KEY, session=self.session)
        self.epic = aionasa.EPIC(NASA_API_KEY, session=self.session)
        self.neows = aionasa.NeoWs(NASA_API_KEY, session=self.session)
        self.exoplanet = aionasa.Exoplanet(NASA_API_KEY, session=self.session)