from typing import Any
import hashlib

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
                add_review(person, request.form['user_review'])
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
    """
    Returns a list of ~3 places {name, photo_link, web_url}?
    TODO: This sample data should be replaced with a real API call!
    """
    print(categories)
    return [{
        'link': 'https://www.yelp.com/biz/cosi-columbus-6?adjust_creative=Ge_k4rixFmx8cwpivm0_VQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_lookup&utm_source=Ge_k4rixFmx8cwpivm0_VQ',
        'imageurl': 'https://s3-media4.fl.yelpcdn.com/bphoto/4U6hz0d0aW9sYAxumwYsZA/o.jpg',
        'name': 'COSI',
    }, {
        'link': 'https://www.yelp.com/biz/cosi-columbus-6?adjust_creative=Ge_k4rixFmx8cwpivm0_VQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_lookup&utm_source=Ge_k4rixFmx8cwpivm0_VQ',
        'imageurl': 'https://s3-media3.fl.yelpcdn.com/bphoto/2QGmeblqy2wtjMO8wvy3Sg/o.jpg',
        'name': 'Place2',
    }
    ]


def get_date_options(description):
    """
    Get options for a date
    TODO: This sample data should be replaced with a real API call!
    """

    return [{
        'name': 'Kat',
        'review': 'We met for coffee at Fox in the Snow Cafe. She had a nice and bubbly personality. '
                  'She talked a lot about politics and and her major which was Civil Engineering. '
                  'Overall, she seemed like an interesting person with a good sense of humor.',
        'keywords': ['cat', 'girl'],
        'categories': ['man'],
    }, {
        'name': 'Handsome',
        'review':
            'Met up with him for drinks and dinner.He was funny and cute. '
            'I was laughing throughout the date and had a great time. '
            'He also seemed very passionate about his career goals and his family. '
            'Would definitely like to have another date with him.',
        'contact_info': 'Go to the mountains and scream my name',
        'keywords': ['man'],
        'categories': ['man'],
    }]


def add_review(person, review: str):
    """
    Add a review to the database
    TODO: Make a real API call!
    """
    pass
