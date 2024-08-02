from flask import Flask, jsonify, request, Response
from flask.views import MethodView
import flask_bcrypt
from pydantic import ValidationError
from schema import CreateAdvertisement, UpdateAdvertisement

from models import Advertisement, Session
from sqlalchemy.exc import IntegrityError

app = Flask('app')
bcrypt = flask_bcrypt.Bcrypt(app)


class ApiError(Exception):

    def __init__(self, status_code: int, msg: str):
        self.status_code = status_code
        self.msg = msg


@app.errorhandler(ApiError)
def error_handler(error: ApiError):
    http_response = jsonify({'error': error.msg})
    http_response.status_code = error.status_code
    return http_response

@app.before_request
def before_request():
    session = Session()
    request.session = session

@app.after_request
def after_request(http_response: Response):
    request.session.close()
    return http_response


def validate(json_data: dict, schema_cls):
    try:
        return schema_cls(**json_data).dict(exclude_unset=True)
    except ValidationError as err:
        error = err.errors()[0]
        error.pop('ctx', None)
        raise ApiError(400, error)


def get_advertisement(advertisement_id: int):
    advertisement = request.session.query(Advertisement).get(advertisement_id)
    if advertisement is None:
        raise ApiError(404, "advertisement not found")
    return advertisement


def add_advertisement(advertisement: Advertisement):
    try:
        request.session.add(advertisement)
        request.session.commit()
    except IntegrityError:
        raise ApiError(409, "advertisement already exists")
    return advertisement


class AdvertisementView(MethodView):
    def get(self, advertisement_id: int):
        advertisement = get_advertisement(advertisement_id)
        return jsonify(advertisement.dict)

    def post(self):
        json_data = validate(request.json, CreateAdvertisement)
        advertisement = Advertisement(**json_data)
        add_advertisement(advertisement)
        return jsonify(advertisement.dict)

    def patch(self, advertisement_id: int):
        json_data = validate(request.json, UpdateAdvertisement)
        advertisement = get_advertisement(advertisement_id)
        for field, value in json_data.items():
            setattr(advertisement, field, value)
        add_advertisement(advertisement)
        return jsonify(advertisement.dict)

    def delete(self, advertisement_id):
        advertisement = get_advertisement(advertisement_id)
        request.session.delete(advertisement)
        request.session.commit()
        return jsonify({"status": "deleted"})

advertisement_view = AdvertisementView.as_view('advertisement_view')
app.add_url_rule(
    '/advertisement',
    view_func=advertisement_view,
    methods=['POST']
)
app.add_url_rule(
    '/advertisement/<int:advertisement_id>',
    view_func=advertisement_view,
    methods=['GET', 'PATCH', 'DELETE']
)

if __name__ == '__main__':

    app.run()