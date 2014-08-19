#!/usr/bin/env python3
# Wentao Han (wentao.han@gmail.com)

import tornado.ioloop
import tornado.web

from bson.objectid import ObjectId
from bson.dbref import DBRef


def load_settings():
    import settings
    result = {}
    for key, value in settings.__dict__.items():
        if key.startswith('_'):
            continue
        result[key] = value
    if result.get('debug', False):
        print(result)
    return result

def make_collection_link(db, collection_name):
    name = collection_name.title()
    link = '<a href="/{collection_name}/">{name}</a>'.format(**locals())
    return link

def make_object_link(db, collection_name, object):
    object_id = object['_id']
    name = object.get('name', object_id)
    link = '<a href="/{collection_name}/{object_id}/">{name}</a>'.format(**locals())
    return link

def find_object_link(db, collection_name, object_id):
    collection_names = db.collection_names(False)
    collection_names.insert(0, collection_name)
    for collection_name in collection_names:
        collection = db[collection_name]
        object = collection.find_one({'_id': object_id})
        if object is not None:
            link = make_object_link(db, collection_name, object)
            break
    else:
        link = 'unknown object'
    return link

def render_as_html(object, db=None, collection_name=None):
    if isinstance(object, ObjectId):
        result = find_object_link(db, collection_name, object)
    elif isinstance(object, DBRef):
        result = make_object_link(db, object.collection, db.dereference(object))
    elif isinstance(object, list):
        result = '<ul class="list-unstyled">\n' + '\n'.join('<li>' + render_as_html(e, db, collection_name) + '</li>' for e in object) + '</ul>'
    else:
        result = str(object)
    return result


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        db = self.settings['db']
        collection_names = db.collection_names(False)
        items = []
        for collection_name in sorted(collection_names):
            link = make_collection_link(db, collection_name)
            items.append(link)
        self.render('index.html', name='Main', items=items)


class CollectionHandler(tornado.web.RequestHandler):

    @tornado.web.addslash
    def get(self, collection_name):
        db = self.settings['db']
        collection = db[collection_name]
        objects = collection.find()
        items = []
        for object in sorted(objects, key=lambda x: x.get('name', str(x['_id']))):
            link = make_object_link(db, collection_name, object)
            items.append(link)
        self.render('collection.html', name=collection_name.title(), items=items)


class ObjectHandler(tornado.web.RequestHandler):

    @tornado.web.addslash
    def get(self, collection_name, id):
        db = self.settings['db']
        collection = db[collection_name]
        object_id = ObjectId(id)
        object = collection.find_one({'_id': object_id})
        name = object.get('name', object_id)
        items = []
        for key, value in sorted(object.items()):
            if key == 'name' or key.startswith('_'):
                continue
            value = render_as_html(value, db=db, collection_name=collection_name)
            items.append((key, value))
        self.render('object.html', name=name, items=items)


settings = load_settings()

application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/([_a-z]+)/?', CollectionHandler),
    (r'/([_a-z]+)/([0-9a-f]+)/?', ObjectHandler),
], **settings)


if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
