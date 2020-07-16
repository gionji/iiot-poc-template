from abc import ABC, abstractmethod

from pymongo import MongoClient


class Persistence(ABC):

    @abstractmethod
    def insert(self, table, timestamp, key, value) -> bool:
        pass

    @abstractmethod
    def query(self, table, query, sort):
        pass

    @abstractmethod
    def drop_table(self, table):
        pass


def compose_document(timestamp, key, value):
    document = {'key': key, 'timestamp': timestamp, 'value': value}
    return document


def flatten(doc):
    row = dict()

    row['id'] = str(doc.get('_id'))
    row['created_at'] = doc.get('_id').generation_time.strftime("%d/%m/%Y %H:%M:%S")
    row['timestamp'] = doc.get('timestamp')
    row['key'] = doc.get('key')
    row['value'] = doc.get('value')

    return row


class MongoDB(Persistence, ABC):

    def __init__(self, host, port):
        super().__init__()
        self.client = MongoClient(host=host, port=port)
        self.db = self.client.local_mongo_db
        self.collections = dict()

    def collection_exists(self, collection):
        return collection in self.collections

    def add_collections(self, collections):
        for collection in collections:
            self.collections[collection] = self.db[collection]

    def insert(self, table, timestamp, key, value) -> bool:
        if self.collection_exists(table):
            inserted = self.collections[table].insert_one(compose_document(timestamp, key, value))
            return inserted.acknowledged
        else:
            return False

    def drop_table(self, table) -> bool:
        if self.collection_exists(table):
            self.collections[table].drop()
            return True
        else:
            return False

    def query(self, table, query, sort):
        if self.collection_exists(table):
            data = self.collections[table].find(query)
            rows = []
            for doc in data:
                rows.append(flatten(doc))
            return rows
        else:
            return False
