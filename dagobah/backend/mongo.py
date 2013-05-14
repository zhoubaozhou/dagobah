""" Mongo Backend class built on top of base Backend """

from datetime import datetime

try:
    from pymongo import MongoClient
except ImportError:
    from pymongo import Connection

try:
    from pymongo.objectid import ObjectId
except ImportError:
    from bson.objectid import ObjectId

from dagobah.backend.base import BaseBackend


class MongoBackend(BaseBackend):
    """ Mongo Backend implementation """

    def __init__(self, host, port, db, dagobah_collection='dagobah',
                 job_collection='dagobah_job', log_collection='dagobah_log'):
        super(MongoBackend, self).__init__()

        self.host = host
        self.port = port
        self.db_name = db

        try:
            self.client = MongoClient(self.host, self.port)
        except NameError:
            self.client = Connection(self.host, self.port)

        self.db = self.client[self.db_name]

        self.dagobah_coll = self.db[dagobah_collection]
        self.job_coll = self.db[job_collection]
        self.log_coll = self.db[log_collection]


    def __repr__(self):
        return '<MongoBackend (host: %s, port: %s)>' % (self.host, self.port)


    def get_new_dagobah_id(self):
        while True:
            candidate = ObjectId()
            if not self.dagobah_coll.find_one({'_id': candidate}):
                return candidate


    def get_new_job_id(self):
        while True:
            candidate = ObjectId()
            if not self.job_coll.find_one({'_id': candidate}):
                return candidate


    def get_new_log_id(self):
        while True:
            candidate = ObjectId()
            if not self.log_coll.find_one({'_id': candidate}):
                return candidate


    def get_dagobah_json(self, dagobah_id):
        return self.dagobah_coll.find_one({'_id': dagobah_id})


    def commit_dagobah(self, dagobah_json):
        dagobah_json['_id'] = dagobah_json['dagobah_id']
        append = {'save_date': datetime.utcnow()}
        self.dagobah_coll.save(dict(dagobah_json.items() + append.items()))


    def delete_dagobah(self, dagobah_id):
        """ Deletes the Dagobah and all child Jobs from the database.

        Run logs are not deleted.
        """

        rec = self.dagobah_coll.find_one({'_id': dagobah_id})
        for job in rec.get('jobs', []):
            if 'job_id' in job:
                self.delete_job(job['job_id'])
        self.dagobah_coll.remove({'_id': dagobah_id})


    def commit_job(self, job_json):
        job_json['_id'] = job_json['job_id']
        append = {'save_date': datetime.utcnow()}
        self.job_coll.save(dict(job_json.items() + append.items()))


    def delete_job(self, job_id):
        self.job_coll.remove({'_id': job_id})


    def commit_log(self, log_json):
        log_json['_id'] = log_json['log_id']
        append = {'save_date': datetime.utcnow()}
        self.log_coll.save(dict(log_json.items() + append.items()))