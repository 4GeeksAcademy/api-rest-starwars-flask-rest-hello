"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([{"id": p.id, "name": p.name, "height": p.height, "mass": p.mass, "gender": p.gender} for p in people])

# Obtener un solo personaje por ID
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "Personaje no encontrado"}), 404
    return jsonify({"id": person.id, "name": person.name, "height": person.height, "mass": person.mass, "gender": person.gender})


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([{"id": p.id, "name": p.name, "climate": p.climate, "terrain": p.terrain} for p in planets])


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404
    return jsonify({"id": planet.id, "name": planet.name, "climate": planet.climate, "terrain": planet.terrain})


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email} for u in users])

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1  
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    
    favs = []
    for fav in favorites:
        if fav.people_id:
            favs.append({"type": "people", "id": fav.people_id})
        if fav.planet_id:
            favs.append({"type": "planet", "id": fav.planet_id})
    
    return jsonify(favs)


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = 1  
    favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Personaje agregado a favoritos"}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1  
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Planeta agregado a favoritos"}), 201


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({"error": "Personaje no está en favoritos"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Personaje eliminado de favoritos"})


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "Planeta no está en favoritos"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Planeta eliminado de favoritos"})










# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
