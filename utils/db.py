import databases
import logging


logger = logging.getLogger('utils.db')


class Database:
    def __init__(self, url):
        self.db = databases.Database(url, min_size=5, max_size=20)
        self.config = None
        self.infractions = None
        self.last_infraction_id = None
        self.role_persist = None
        self.user_history = None

    async def initialize(self):
        await self.db.connect()
        self.config = ConfigTable
        self.infractions = InfractionsTable
        self.last_infraction_id = LastInfractionIDTable
        self.role_persist = RolePersistTable
        self.user_history = UserHistoryTable


#########################################################################


class Table:
    def __init__(self, name, db):
        self.name = name
        self.db = db


class ConfigTable(Table):
    def __init__(self, db):
        super().__init__('config', db)


class InfractionsTable(Table):
    def __init__(self, db):
        super().__init__('infractions', db)


class LastInfractionIDTable(Table):
    def __init__(self, db):
        super().__init__('last_infraction_id', db)


class RolePersistTable(Table):
    def __init__(self, db):
        super().__init__('role_persist', db)


class UserHistoryTable(Table):
    def __init__(self, db):
        super().__init__('user_history', db)



