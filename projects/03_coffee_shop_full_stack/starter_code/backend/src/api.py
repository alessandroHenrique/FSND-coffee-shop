import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = [drink.short() for drink in drinks]

    if len(formatted_drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = [drink.long() for drink in drinks]

    if len(formatted_drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink(
            title=title,
            recipe=json.dumps(recipe)
        )
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    body = request.get_json()

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink.query.get(drink_id)

        if drink is None:
            abort(404)

        if title:
            drink.title = title

        if recipe:
            drink.recipe = recipe

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception:
        abort(400)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink = Drink.query.get(drink_id)

        if not drink:
            abort(404)

        drink.delete()
        return jsonify({
            "success": True,
            "delete": drink_id
        })
    except Exception:
        abort(422)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400
