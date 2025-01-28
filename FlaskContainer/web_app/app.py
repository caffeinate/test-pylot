from flask import Flask


def create_app(settings_class):
    """
    :param settings_class (str or class) to Flask settings
    """
    # internal import to make it possible to mock.patch
    from web_app.views import web_view

    app = Flask(__name__)
    app.config.from_object(settings_class)

    app.register_blueprint(web_view, url_prefix="/")

    return app
