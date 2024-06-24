#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db, batch_mode=True)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()
        scientist_list = []
        for scientist in scientists:
            scientist_dict = {
                'id': scientist.id,
                'name': scientist.name,
                'field_of_study': scientist.field_of_study
            }
            scientist_list.append(scientist_dict)
        response = make_response(scientist_list, 200)
        return response
    
    def post(self):
        request_dict = request.get_json()
        try:
            new_scientist = Scientist(
                name=request_dict.get('name'),
                field_of_study=request_dict.get('field_of_study')
            )
        except:
            return {"errors": ["validation errors"]}, 400
        if new_scientist:
            db.session.add(new_scientist)
            db.session.commit()
            response = make_response(new_scientist.to_dict(), 201)
            return response
        else:
            return {'errors': ["validation errors"]}, 400

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            response = make_response(scientist.to_dict(), 200)
            return response
        else:
            return {"error": "Scientist not found"}, 404
    
    def patch(self, id):
        updated_entry = request.get_json()
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            try:
                scientist.name = updated_entry.get('name', scientist.name)
                scientist.field_of_study = updated_entry.get('field_of_study', scientist.field_of_study)

                db.session.commit()
                updated_scientist = Scientist.query.filter_by(id=id).first()
                response = make_response(updated_scientist.to_dict(), 202)
                return response
            except:
                return {"errors": ["validation errors"]}, 400
        else:
            return {"error": "Scientist not found"}, 404
    
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()

            return {}, 204
        else:
            return {"error": "Scientist not found"}, 404

class Planets(Resource):
    def get(self):
        planets = Planet.query.all()
        planet_list = []
        for planet in planets:
            planet_dict = {
                'id': planet.id,
                'name': planet.name,
                'distance_from_earth': planet.distance_from_earth,
                'nearest_star': planet.nearest_star
            }
            planet_list.append(planet_dict)
        response = make_response(planet_list, 200)
        return response

class Missions(Resource):
    def post(self):
        request_dict = request.get_json()
        try:
            new_mission = Mission(
                name=request_dict.get('name'),
                scientist_id=request_dict.get('scientist_id'),
                planet_id=request_dict.get('planet_id')
            )
            db.session.add(new_mission)
            db.session.commit()
            new_mission = new_mission.to_dict()
            planet_id = new_mission.get('planet_id')
            planet = Planet.query.filter_by(id=planet_id).first()
            scientist_id = new_mission.get('scientist_id')
            scientist = Scientist.query.filter_by(id=scientist_id).first()
            response_object = {
                'id': new_mission['id'],
                'name': new_mission['name'],
                'planet': planet.to_dict(),
                'planet_id': planet.id,
                'scientist': scientist.to_dict(),
                'scientist_id': scientist.id
            }
            return response_object, 201
        except:
            return {"errors": ["validation errors"]}, 400


api.add_resource(Scientists, '/scientists', endpoint='scientists')
api.add_resource(ScientistById, '/scientists/<int:id>', endpoint='scientists/<int:id>')
api.add_resource(Planets, "/planets", endpoint="planets")
api.add_resource(Missions, "/missions", endpoint="missions")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
