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
        self.guild_config_cache = {}
        self.infractions_cache = {}
        self.last_infraction_id_cache = {}
        self.role_persist_cache = {}
        self.user_history_cache = {}

    async def initialize(self):
        await self.connect()
        # self.guild_config = GuildConfigTable(self)
        # self.infractions = InfractionsTable(self)
        # self.last_infraction_id = LastInfractionIDTable(self)
        # self.role_persist = RolePersistTable(self)
        # self.user_history = UserHistoryTable(self)

    async def connect(self):
        await self.conn.connect()

    async def close(self):
        await self.conn.disconnect()

    @property
    def is_connected(self):
        return self.conn.is_connected

    # GUILD CONFIG STUFF

    def get_guild_config(self, guild_id):
        return self.guild_config_cache.get(guild_id)

    async def _query_fetch_guild_config(self, guild_id):
        query = r"SELECT * FROM guild_config WHERE guild_id = :guild_id;"
        return await self.conn.fetch_one(query, {'guild_id': guild_id})

    async def fetch_guild_config(self, guild_id):
        cached = self.get_guild_config(guild_id)
        if cached:
            return cached

        row = await self._query_fetch_guild_config(guild_id)

        if row:
            config = GuildConfigRow(row)
            self.guild_config_cache[guild_id] = config
            return config
        else:
            return None

    # MODLOG STUFF

    def get_infraction(self, guild_id, infraction_id):
        guild = self.guild_config_cache.get(guild_id)
        return guild.get(infraction_id) if guild else None

    def get_last_infraction_id(self, guild_id):
        return self.last_infraction_id_cache.get(guild_id)

    # ROLE PERSIST STUFF

    def get_role_persist_data(self, guild_id, user_id):
        guild = self.role_persist_cache.get(guild_id)
        return guild.get(user_id) if guild else None

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


class GuildConfigRow(Row):
    def __init__(self, record):
        self.guild_id = record['guild_id']
        self.muted_role = record['muted_role']
        self.admin_role = record['admin_role']
        self.mod_role = record['mod_role']
        self.ignored_users = record['ignored_users']
        self.ignored_roles = record['ignored_roles']
        self.ignored_channels = record['ignored_channels']
        self.autoroles_user = record['autoroles_user']
        self.autoroles_bot = record['autoroles_bot']
        self.role_persist = record['role_persist']
        self.modlog_channel = record['modlog_channel']
        self.prefix = record['prefix']
        
        
class InfractionsRow(Row):
    def __init__(self, record):
        self.global_id = record['global_id']
        self.guild_id = record['guild_id']
        self.infraction_id = record['infraction_id']
        self.timestamp = record['timestamp']
        self.user_id = record['user_id']
        self.mod_id = record['mod_id']
        self.infraction_type = record['infraction_type']
        self.reason = record['reason']
        self.message_id = record['message_id']
        
        
class LastInfractionIDRow(Row):
    def __init__(self, record):
        self.guild_id = record['guild_id']
        self.last_infraction_id = record['last_infraction_id']
        

class RolePersistRow(Row):
    def __init__(self, record):
        self.guild_id = record['guild_id']
        self.user_id = record['user_id']
        self.roles = record['roles']
        

class UserHistoryRow(Row):
    def __init__(self, record):
        self.guild_id = record['guild_id']
        self.user_id = record['user_id']
        self.mute = record['mute']
        self.kick = record['kick']
        self.ban = record['ban']
        self.unmute = record['unmute']
        self.unban = record['unban']


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
    sql.Column('user_id', sql.BIGINT, primary_key=True),
    sql.Column('roles', sql.ARRAY(sql.BIGINT)),
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
