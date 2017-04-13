'''
Created on 23 Sep 2015

@author: si
'''
import random
import time
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


@api_views.route('/foox/<int:id>/', methods = ['GET'])
def get_foox(id):

    foo = Foo.query.filter_by(id=id).first()
    if foo == None:
        abort(404)

    sql = "delete from foo where id<>%s" % id
    db.session.execute(sql)
    
#     db.session.execute("select sleep(0.2)")

    if db.session.query(Foo).filter_by(id=id).count() != 1:
        abort(500)
    
    db.session.rollback()
    
    try:
        thread_name = threading.current_thread().name
    except:
        thread_name = "No_thread"
    try:
        pid = str(os.getpid())
    except:
        pid = "no_pid"
    
    processed_by = "%s-%s" % (pid, thread_name)

    x = foo.serialize
    x['http_by_proc-thread'] = processed_by
    return jsonify(x)


@api_views.route('/foo/<int:id>/', methods = ['GET'])
def get_foo(id):
    db.session().execute("select sleep(0.5)")
    foo = Foo.query.filter_by(id=id).first()
    if foo == None:
        abort(404)
    return jsonify(foo.serialize)

@api_views.route('/foo/', methods = ['POST'])
def make_foo():
    try:
        thread_name = threading.current_thread().name
    except:
        thread_name = "No_thread"
    try:
        pid = str(os.getpid())
    except:
        pid = "no_pid"
    
    processed_by = "%s-%s" % (pid, thread_name)

    r = request.get_json()

    if 'title' not in r:
        d = {'reason': 'title not set',
             'http_by_proc-thread': processed_by,
             }
        return jsonify(d), 400

    d = {   'title' : r['title'],
            'proc_id' : str(os.getpid()),
            'thread_name' : threading.current_thread().name,
    }

    foo = Foo(**d)
    db.session.add(foo)
    db.session.commit()
    d['id'] = foo.id
    d['success'] = True
    d['http_by_proc-thread'] = processed_by
    return jsonify(d)
