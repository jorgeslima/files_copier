#!/usr/bin/pyton3.5

import os
from pathlib import Path
from tinydb import TinyDB, Query

class DbHandler(object):

    def __init__(self):
        dbpath = "%s/db/fcdb.json" % os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.dbpath = dbpath
        self.DB = TinyDB(dbpath)
        self.DB.table('dirs')
        self.DB.table('files')

    def insert(self,table,value):
        record = self.exists(table,value)
        if not record:
            return self.DB.table(table).insert(value)
        else:
            return record

    def exists(self,table,value):
        q = Query()
        match = self.DB.table(table).get(q.path==value['path'])
        if match is not None:
            return match.doc_id
        return None

    def getPendingDirs(self):
        q = Query()
        return self.DB.table('dirs').search(q.status==False)

    def getPendingFiles(self,parent_dir):
        q = Query()
        return self.DB.table('files').search((q.status==False) & (q.dir_id==parent_dir))

    def markAsCreated(self,table,path):
        q = Query()
        return self.DB.table(table).update({'status':True},q.path == path)

    def clear(self):
        self.DB.purge_tables()