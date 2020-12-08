from databases import Database as DB


class Table:
    def __init__(self, name):
        self.name = name
        self.db = None


class Database(DB):
    def __init__(self):
        super().__init__('postgresql://postgres/bulbe', min_size=5, max_size=20)

    async def initialize(self):
        query = "CREATE TABLE configs (guild_id INTEGER PRIMARY KEY, prefix VARCHAR(100), )"
        await self.execute(query)

        query = """"""


