#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"
@app.route("/restaurants")
def restaurants():
    restaurants = Restaurant.query.all()
    if request.method == "GET":
        status_code = 200
        response_body =[restaurant.to_dict(only=('address','id','name')) for restaurant in restaurants]
    else:
        status_code = 404
        response_body = {"error": "Restaurant not found"}
    return make_response(response_body,
                          status_code,
                          {'content-type':'application/json'})
@app.route('/restaurants/<int:id>',methods=['GET','DELETE'])
def get_restaurant_by_id(id):
    restaurant =Restaurant.query.filter(Restaurant.id == id).first()
    if request.method == "GET" and restaurant:
        status_code = 200
        response_body = restaurant.to_dict()
    elif request.method == "DELETE" and restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        status_code = 204
        response_body = {"message": "Restaurant deleted successfully"}
    else:
        status_code = 404
        response_body = {"error": "Restaurant not found"}
    return make_response(response_body,
                          status_code,
                          {'content-type':'application/json'})

@app.route("/pizzas")
def get_pizzas():
    pizzas = Pizza.query.all()
    if request.method == "GET":
        status_code = 200
        response_body = [pizza.to_dict(only=('id','ingredients','name')) for pizza in pizzas]
    else:
        status_code = 404
        response_body = {"error": "Pizza not found"}
    return make_response(response_body,
                          status_code,
                          {'content-type':'application/json'})

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    pizza = Pizza.query.filter(Pizza.id == data['pizza_id']).first()
    restaurant = Restaurant.query.filter(Restaurant.id == data['restaurant_id']).first()
    if pizza and restaurant and data['price'] > 1 and data['price'] <= 30:
        new_restaurant_pizza = RestaurantPizza(price=data['price'], pizza=pizza, restaurant=restaurant)
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        status_code = 201
        response_body = new_restaurant_pizza.to_dict(rules=('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas'))

    else:
        status_code = 400
        response_body = {"errors": ["validation errors"]}
    return make_response(response_body,
                          status_code,
                          {'content-type':'application/json'})

    


if __name__ == "__main__":
    app.run(port=5555, debug=True)
