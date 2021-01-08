import json
import boto3

from boto3.dynamodb.conditions import Key

from databases import Database


MIGRATION = 'DYNAMO_TO_JSON'
# MIGRATION = 'JSON_TO_POSTGRES'

DYNAMO_TABLE = 'Bulbe'
JSON_FILE = 'bulbe_database.json'
POSTGRES_DATABASE = 'bulbe'
POSTGRES_TABLE = 'config'


class DynamoTable:
    def __init__(self, table_name):
        self.name = table_name
        self.resource = boto3.resource('dynamodb', region_name='us-east-2')
        self.table = self.resource.Table(table_name)
        self.primary_key = self.table.key_schema[0]['AttributeName']
        self.sort_key = self.table.key_schema[1]['AttributeName']
        print(f'Dynamodb table initialized. ({table_name})')

    def put(self, data, key_data=None):
        print(f"'Writing to table: {self.name} ({key_data if key_data else ''}) - {data}'")
        if key_data is not None:
            for i, key in enumerate(key_data):
                data[[self.primary_key, self.sort_key][i]] = key
        self.table.put_item(Item=data)
        print('Successfully wrote to table.')
        return True

    def get(self, key_data):
        print(f'Reading table: {self.name} ({key_data})')
        keys = dict()
        if len(key_data) != 2:
            return None
        for i, key in enumerate(key_data):
            keys[[self.primary_key, self.sort_key][i]] = key
        response = self.table.get_item(Key=keys)
        item = response['Item']
        print('Successfully read table.')
        return item

    def read(self, sort_key):
        print(f'Bulk reading table: {self.name} - {sort_key}.')
        # try:
        response = self.table.scan(FilterExpression=Key(self.sort_key).eq(sort_key))
        items = response['Items']
        print(f'Successfully bulk read table {self.name} - {sort_key}')
        return items

    def read_to_dict(self, sort_key):
        response = self.read(sort_key)
        data = dict()
        key_schema = [self.primary_key, self.sort_key]
        for item in response:
            data[int(item.pop(key_schema[0]))] = item
            item.pop(key_schema[1])
        return data

    def write(self, items, sort_key=None):
        print(f'Reading table: {self.name}')
        with self.table.batch_writer() as batch:
            for item in items:
                if sort_key:
                    item[self.sort_key] = sort_key
                batch.put_item(Item=item)

    def write_from_dict(self, data, sort_key):
        items = list()
        for key, value in data.items():
            value[self.primary_key] = key
            value[self.sort_key] = sort_key
            items.append(value)
        self.write(items)


def dynamo_to_json():
    print('Migrating from DynamoDB to JSON')
    table = DynamoTable('Bulbe')
    data = table.read_to_dict('config')
    print(f'Successfully pulled data from DynamoDB. Dumping to {JSON_FILE}')
    with open(JSON_FILE, 'w') as fp:
        json.dump(data, fp)
    print('Done.')


def json_to_postgres():
    return NotImplementedError


if __name__ == '__main__':
    if MIGRATION == 'DYNAMO_TO_JSON':
        dynamo_to_json()
    elif MIGRATION == 'JSON_TO_POSTGRES':
        json_to_postgres()
    else:
        print('ERROR: NO MIGRATION TYPE SPECIFIED.')
