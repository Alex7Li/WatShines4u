from typing import Any

from flask import (
    Blueprint,
    render_template,
)

bp = Blueprint('main', __name__, url_prefix='/initial')

@bp.route("/", methods=["GET", "POST"])
def initial() -> Any:
    return render_template("index.html")
