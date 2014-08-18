#!/usr/bin/env python3
# Wentao Han (wentao.han@gmail.com)

import pymongo
import tornado.ioloop
import tornado.web

from bson.objectid import ObjectId


connection = pymongo.Connection()
db = connection['test']


def make_object_link(db, object_id):
    collection_names = db.collection_names(False)
    for collection_name in collection_names:
        collection = db[collection_name]
        object = collection.find_one({'_id': object_id})
        if object is not None:
            name = object['name']
            link = '<a href="/{collection_name}/{object_id}">{name}</a>'.format(**locals())
            break
    else:
        link = 'unknown object'
    return link


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('<h1>Main</h1>')


class ObjectHandler(tornado.web.RequestHandler):

    def initialize(self, db):
        self.db = db

    def get(self, collection_name, id):
        db = self.db
        collection = db[collection_name]
        object_id = ObjectId(id)
        object = collection.find_one({'_id': object_id})
        name = object['name']
        items = []
        for key, value in sorted(object.items()):
            if key == 'name' or key.startswith('_'):
                continue
            if isinstance(value, ObjectId):
                value = make_object_link(db, value)
            else:
                value = str(value)
            items.append((key, value))
        self.render('object.html', name=name, items=items)


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/([a-z]+)/([0-9a-f]+)', ObjectHandler, dict(db=db)),
])


if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
