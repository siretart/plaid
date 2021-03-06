from flask import Response, Blueprint
from flask import g, render_template, url_for

from flask.ext import login

from app.models import Patch

bp = Blueprint('patch', __name__, url_prefix='/patch/<patch_id>')

@bp.url_value_preprocessor
def get_patch(endpoint, values):
    patch_id = values.pop('patch_id')
    g.patch = Patch.query.filter_by(id=patch_id).first_or_404()

@bp.route('/')
def index():
    series = g.patch.series
    patches = Patch.query.filter_by(series_id=series.id)

    if patches.count() > 1:
        patches = patches.order_by(Patch.date)
        def endpoint(page_index):
            patch = patches.paginate(page_index, 1).items[0]
            return url_for('patch.index', patch_id=patch.id)

        page = patches.paginate(1 + patches.all().index(g.patch), 1)
        return render_template('patch.html',
                               user=login.current_user,
                               patch=g.patch,
                               series=series,
                               page=page,
                               endpoint=endpoint)
    else:
        return render_template('patch.html',
                               user=login.current_user,
                               patch=g.patch)


@bp.route('/mbox')
def mbox():
    return Response(g.patch.mbox, mimetype='application/mbox')

@bp.route('/patch')
def patch():
    return Response(g.patch.content, mimetype='text/x-patch')

