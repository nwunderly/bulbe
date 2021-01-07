import databases
import logging


logger = logging.getLogger('utils.db')


class Database:
    def __init__(self, url):
        self.conn = databases.Database(url, min_size=5, max_size=20)
        self.config = None
        self.infractions = None
        self.last_infraction_id = None
        self.role_persist = None
        self.user_history = None

    async def initialize(self):
        await self.connect()
        self.config = ConfigTable
        self.infractions = InfractionsTable
        self.last_infraction_id = LastInfractionIDTable
        self.role_persist = RolePersistTable
        self.user_history = UserHistoryTable

    async def connect(self):
        await self.conn.connect()

    async def close(self):
        await self.conn.disconnect()

    @property
    def is_connected(self):
        return self.conn.is_connected


#########################################################################


class Table:
    def __init__(self, name, db: Database):
        self.name = name
        self.db = db


class ConfigTable(Table):
    def __init__(self, db):
        super().__init__('config', db)

    async def new_guild_config(self, guild_id):
        query = r"INSERT INTO config " \
                r"(guild_id, prefix, muted_role, admin_role, mod_role, ignored_users, ignored_roles, ignored_channels, " \
                r"autoroles_user, autoroles_bot, role_persist, modlog_channel) VALUES " \
                r"($1, '+', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)"
        await self.db.conn.execute(query, guild_id)


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



