'''
Created on 23 Sep 2015

@author: si
'''
import threading
import os

from flask import abort, Blueprint, make_response, jsonify, current_app, request
from sqlalchemy.sql import text

from flask_app import db, Foo

api_views = Blueprint('api_views', __name__)

# @api_views.errorhandler(404)
# def not_found(error):
#     return make_response(jsonify( { 'error': 'Not found' } ), 404)
# 
# @api_views.after_request
# def after_request(response):
#     # avoid transaction isolation - flush should work but doesn't
#     db.session.remove()
#     return response

@api_views.route('/')
def hello():
    try:
        thread_name = threading.current_thread().name
    except:
        thread_name = "No_thread"
    try:
        pid = str(os.getpid())
    except:
        pid = "no_pid"
    return "Hello World! %s-%s" % (thread_name, pid)

@api_views.route('/foo/<int:id>/', methods = ['GET'])
def get_foo(id):
    foo = Foo.query.filter_by(id=id).first()
    if foo == None:
        abort(404)
    return jsonify(foo.serialize)

@api_views.route('/foo/', methods = ['POST'])
def make_foo():
    r = request.get_json()

    if 'title' not in r:
        d['reason'] = 'title not set'
        return jsonify({'reason':'title not set'}), 400

    d = {   'title' : r['title'],
            'proc_id' : str(os.getpid()),
            'thread_name' : threading.current_thread().name,
    }

    foo = Foo(**d)
    db.session.add(foo)
    db.session.commit()
    d['id'] = foo.id
    d['success'] = True
    return jsonify(d)
