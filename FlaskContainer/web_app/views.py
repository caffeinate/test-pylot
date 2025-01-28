import os

from flask import Blueprint

from web_app.utils import login_required

web_view = Blueprint("web", __name__)


@web_view.route("/")
def root():

    doc = (
        "<html><body><h1>Sorry, there is a problem with the service</h1>"
        "<p>Please Try again later.</p>"
        "</body></html>"
    )
    return doc


@web_view.route("/show_env")
@login_required
def show_env():
    """
    Page with dump of environmental variables. Requires `BASIC_HTTP_AUTH` environmental variable to
    be set, see main README.md.
    """
    env_dump = "<table>"
    for k, v in os.environ.items():
        env_dump += f"<tr><td>{k}</td><td>{v}</td></tr>"
    env_dump += "</table>"

    doc = "<html><body><h1>Env dump</h1>{env_dump}</body></html>"
    return doc.replace("{env_dump}", env_dump)
