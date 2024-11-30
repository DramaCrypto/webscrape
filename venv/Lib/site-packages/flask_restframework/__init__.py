import logging

from flask import jsonify
from werkzeug.exceptions import default_exceptions

__author__ = 'stas'
__version__ = "0.2.1"

from flask_restframework.serializer import BaseSerializer
from flask_restframework.exceptions import BaseException

def common_exception_handler(e):
    logging.getLogger(
        "flask_restframework"
    ).getChild("exception_handler").exception(
        "Getted common exception: %s", e,
        extra={"meta": e}
    )
    resp = jsonify({
        "error": e.__class__.__name__,
        "code": 500,
        "description": str(e)
    })

    resp.status_code = 500

    return resp

def http_exception_handler(e):
    logging.getLogger(
        "flask_restframework"
    ).getChild("exception_handler").error(
        "Getted http exception: %s", e, exc_info=True,
        extra={"meta": e}
    )
    resp = jsonify({
        "error": e.name,
        "code": e.code,
        "description": e.description
    })

    resp.status_code = e.code

    return resp

def base_exception_handler(e):
    #type: (BaseException)->None

    data = getattr(e, "data")
    status = e.status

    out = jsonify(data or {})
    out.status_code = status

    return out

class RestFramework(object):

    def __init__(self, app=None):
        self.init_app(app)

    def init_app(self, app):
        self.app = app

        return self

    def init_errorhandlers(self):
        self.app.errorhandler(Exception)(common_exception_handler)
        self.app.errorhandler(BaseException)(base_exception_handler)

        for code, ex in default_exceptions.items():
            self.app.errorhandler(code)(http_exception_handler)

        return self
