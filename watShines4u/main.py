from typing import Any
from .watson import get_matches
from .Yelp import business_formatter_for_frontend, query_api

from flask import (
    Blueprint,
    render_template,
    request
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
            '''
            TODO get actual places
            '''
            placeOptions = get_places()
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
                add_review(person, request.form['user_review'])
    return render_template('index.html', stage=stage, dateOptions=dateOptions,
                           placeOptions=placeOptions, selected_date=selected_date)


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


def get_places():
    # TODO: How do we get the right query?
    response = query_api("gaming bars", "Columbus")

    places = []

    for place in response:
        formatted_place = business_formatter_for_frontend(place)
        places.append(formatted_place)

    return places


def get_date_options(description):
    all_dates = []

    # API call to Watson to get possible dates
    reviews = get_matches(description)

    # Format data for frontend
    for date_option in reviews:
        date = {
            'name': date_option['name'],
            'review': date_option['description']
        }

        all_dates.append(date)

    return all_dates


def add_review(person, review: str):
    """
    Add a review to the database
    TODO: Make a real API call!
    """
    pass

def main():
    d = get_date_options("someone who I can get drinks with")
    print(d)

if __name__ == '__main__':
    main()