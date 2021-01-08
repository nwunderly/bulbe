import logging

import databases as db
import sqlalchemy as sql
from typing import List
from datetime import datetime


logger = logging.getLogger('utils.db')


############
# DATABASE #
############


class Database:
    def __init__(self, database_url):
        self.conn = db.Database(database_url, min_size=5, max_size=20)
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


################
# DATA CLASSES #
################


class Row:
    def __init__(self):
        pass

    @classmethod
    def from_record(cls, record):
        row = cls()
        for name, value in record.values():
            row.__setattr__(name, value)
        return row


class GuildConfig(Row):
    pass


#############
# ORM STUFF #
#############


guild_config = sql.Table(
    'guild_config',
    sql.MetaData(),
    sql.Column('guild_id', sql.BIGINT, primary_key=True),
    sql.Column('muted_role', sql.BIGINT),
    sql.Column('admin_role', sql.BIGINT),
    sql.Column('mod_role', sql.BIGINT),
    sql.Column('ignored_users', sql.ARRAY(sql.BIGINT)),
    sql.Column('ignored_roles', sql.ARRAY(sql.BIGINT)),
    sql.Column('ignored_channels', sql.ARRAY(sql.BIGINT)),
    sql.Column('autoroles_user', sql.ARRAY(sql.BIGINT)),
    sql.Column('autoroles_bot', sql.ARRAY(sql.BIGINT)),
    sql.Column('role_persist', sql.ARRAY(sql.BIGINT)),
    sql.Column('modlog_channel', sql.BIGINT),
    sql.Column('prefix', sql.TEXT),
)

infractions = sql.Table(
    'infractions',
    sql.MetaData(),
    sql.Column('global_id', sql.BIGINT),
    sql.Column('guild_id', sql.BIGINT, primary_key=True),
    sql.Column('infraction_id', sql.BIGINT, primary_key=True),
    sql.Column('timestamp', sql.TIMESTAMP, default=datetime.now),
    sql.Column('user_id', sql.BIGINT),
    sql.Column('mod_id', sql.BIGINT),
    sql.Column('infraction_type', sql.TEXT),
    sql.Column('reason', sql.TEXT),
    sql.Column('message_id', sql.BIGINT),
)

last_infraction_id = sql.Table(
    'last_infraction_id',
    sql.MetaData(),
    sql.Column('guild_id', sql.BIGINT, primary_key=True),
    sql.Column('last_infraction_id', sql.BIGINT),
)

role_persist = sql.Table(
    'role_persist',
    sql.MetaData(),
    sql.Column('guild_id', sql.BIGINT, primary_key=True),
    sql.Column('role_id', sql.BIGINT, primary_key=True),
    sql.Column('users', sql.ARRAY(sql.BIGINT)),
)

user_history = sql.Table(
    'user_history',
    sql.MetaData(),
    sql.Column('guild_id', sql.BIGINT, primary_key=True),
    sql.Column('user_id', sql.BIGINT, primary_key=True),
    sql.Column('mute', sql.ARRAY(sql.BIGINT)),
    sql.Column('kick', sql.ARRAY(sql.BIGINT)),
    sql.Column('ban', sql.ARRAY(sql.BIGINT)),
    sql.Column('unmute', sql.ARRAY(sql.BIGINT)),
    sql.Column('unban', sql.ARRAY(sql.BIGINT)),
)


############
# TABLES #
############


class Table:
    def __init__(self, name, _db: Database):
        self.name = name
        self.db = _db
        self.conn = _db.conn
        self.cache = {}

    @staticmethod
    def where_expr(**checks):
        exprs = []
        values = {}
        for var, value in checks.items():
            exprs.append(f"{var} = :{var}")
            values[var] = value
        where_expr = " AND ".join(exprs)
        return where_expr, values

    async def fetch_row(self, **checks):
        where_expr, values = self.where_expr(**checks)
        query = f"SELECT * FROM {self.name} WHERE {where_expr}"
        return await self.conn.fetch_one(query, values)

    async def fetch_row_cached(self, **primary_key_checks):
        primary_key = list(primary_key_checks.keys())

        if primary_key in self.cache:
            return self.cache[primary_key]

        return await self.fetch_row(**primary_key_checks)


class ConfigTable(Table):
    ROWS = {
        'guild_id': int,
        'prefix': str,
        'muted_role': int,
        'admin_role': int,
        'mod_role': int,
        'ignored_users': List[int],
        'ignored_roles': List[int],
        'ignored_channels': List[int],
        'autoroles_user': List[int],
        'autoroles_bot': List[int],
        'role_persist': List[int],
        'modlog_channel': List[int],
    }

    def __init__(self, _db):
        super().__init__('config', _db)

    async def exists(self, guild_id):
        query = r"SELECT exists(SELECT 1 FROM config WHERE guild_id = $1)"
        exists = await self.conn.fetch_val(query, guild_id)
        return exists

    async def new_guild_config(self, guild_id):
        query = r"INSERT INTO config (guild_id) VALUES (:guild_id) RETURNING *"
        row = await self.conn.fetch_one(query, {'guild_id': guild_id})
        config = GuildConfig.from_record(row)
        self.cache[guild_id] = config
        return config

    async def get_guild_config(self, guild_id):
        if guild_id in self.cache:
            return self.cache[guild_id]

        query = r"SELECT * FROM config WHERE guild_id = :guild_id"
        row = await self.conn.fetch_one(query, {'guild_id': guild_id})
        config = GuildConfig.from_record(row)
        self.cache[guild_id] = config
        return config

    async def set_prefix(self, guild_id, prefix):
        if not await self.exists(guild_id):
            await self.new_guild_config(guild_id)
        query = r"UPDATE config SET prefix = :prefix WHERE guild_id = :guild_id RETURNING *"
        row = await self.conn.fetch_one(query, {'guild_id': guild_id, 'prefix': prefix})
        config = GuildConfig.from_record(row)
        self.cache[guild_id] = config
        return config



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



