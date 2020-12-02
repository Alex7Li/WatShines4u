from typing import Any
import hashlib
from .watson import get_matches, add_date_review
from .Yelp import business_formatter_for_frontend, query_api
from flask import (
    Blueprint,
    render_template,
    request,
)

bp = Blueprint('main', __name__, url_prefix='/initial')

# Having global variables is way simpler than dealing with a database or whatever,
# though there are some issues with refreshes
dateOptions = []
placeOptions = []
selected_date = None

@bp.route('/', methods=['GET', 'POST'])
def initial() -> Any:
    global dateOptions
    global placeOptions
    global selected_date
    stage = 1
    if 'match' in request.form:
        stage = 2
        dateOptions = get_date_options(request.form['description'])
    # Check that dateOptions isn't empty, sometimes refreshing messes us up
    if len(dateOptions) > 0:
        # The name is the end of the value option of the field from the form,
        # the value is Choose {{name}} because it propagates to the frontend.
        if 'place' in request.form:
            name = request.form['place'][7:]
            stage = 3
            selected_date = select(dateOptions, name)
            placeOptions = get_places(selected_date['categories'])
            if 'contact_info' not in selected_date:
                selected_date['contact_info'] = get_contact(selected_date['name'])
            placeOptions.append({
                'link': 'https://smartcouples.ifas.ufl.edu/dating/having-fun-and-staying-close/101-fun-dating-ideas/',
                'imageurl': '../static/lightbulb.jpg',
                'name': 'your own idea!',
            })
        # Check that placeOptions isn't empty, sometimes refreshing messes us up
        if len(placeOptions) > 0:
            if 'date' in request.form:
                stage = 4
                place = request.form['date'][7:]
                select(placeOptions, place)
            elif 'review' in request.form:
                stage = 5
            elif 'done' in request.form:
                stage = 1
                person = get_selected(dateOptions)
                add_review({"name": person["name"]}, request.form['user_review'])
    return render_template('index.html', stage=stage, dateOptions=dateOptions,
                           placeOptions=placeOptions, selected_date=selected_date)


def get_contact(name):
    return "Call me! My number is 614" + "-" + str((hash(name)*43) % 1000) + "-" + str(hash(name) % 10000)


def get_selected(array):
    """
    Get the selected element of an array
    """
    return next(x for x in array if 'selected' in x)


def select(array, name):
    """
    Add the selected element to the element of the map with
    the given name, and make the others not selected.
    Returns the selected element
    """
    selected = None
    for x in array:
        if x['name'] == name:
            x['selected'] = 'Yup'
            selected = x
        else:
            x.pop('selected', None)
    if selected is None:
        raise AssertionError(f"No element x with x['name']={name} was not in the array {array}.")
    return selected


def get_places(categories):

    response = query_api(categories[0], "Columbus")

    places = []

    for place in response:
        formatted_place = business_formatter_for_frontend(place)
        places.append(formatted_place)

    return places


def get_date_options(description):

    return get_matches(description)


def add_review(person, review: str):

    add_date_review(review, person)
