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
from models import db, User, People, Planets, Favorites_people, Favorites_planets
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_current_user,  JWTManager
from sqlalchemy.exc import NoResultFound


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

#ENDPOINTS PARA USERS:


@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        data = db.session.scalars(db.select(User)).all()

        if not data:
            return jsonify({"msg": "No users found"}), 404
        
        result = list(map(lambda item: item.serialize(), data))
        response_body = {
            "results": result
        }
        
        return jsonify(response_body), 200

    except Exception as e:
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500


@app.route('/user', methods=['POST'])
def create_user():
    try:
        request_body = request.json
        
        email = request_body["email"]
        password = request_body["password"]

        # Verifica si el usuario ya existe
        existing_user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one()

        if existing_user:
            # access_token = create_access_token(identity=email)
            return jsonify({
                # "access_token": access_token,
                # "user": existing_user.serialize(),
                "message": "User already exists, logged in successfully"
            }), 200

        # Crear nuevo usuario
        new_user = User(
            name=request_body["name"],
            last_name=request_body["last_name"],
            email=email,
            password=password,
            # is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "user": new_user.serialize(),
            "message": "User created successfully"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#ENDPOINTS PARA FAVORITOS

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorite(user_id):
    try:
        # Obtener el usuario por ID
        user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()
        
        if user is None:
            return jsonify({"msg": "User not found"}), 404
        
        favorite_people_ids = db.session.execute(
            db.select(Favorites_people.people_id).filter_by(user_id=user_id)
        ).scalars().all()
        
        favorite_planets_ids = db.session.execute(
            db.select(Favorites_planets.planets_id).filter_by(user_id=user_id)
        ).scalars().all()
        
        # Obtener detalles, ¿Eran necesarios estos detalles?
        favorite_people = []
        if favorite_people_ids:
            favorite_people = db.session.scalars(
                db.select(People).filter(People.id.in_(favorite_people_ids))
            ).all()
        
        favorite_planets = []
        if favorite_planets_ids:
            favorite_planets = db.session.scalars(
                db.select(Planets).filter(Planets.id.in_(favorite_planets_ids))
            ).all()
        
        # Serializar 
        serialized_people = [person.serialize() for person in favorite_people]
        serialized_planets = [planet.serialize() for planet in favorite_planets]
        
        response_body = {
            "favorite_people": serialized_people,
            "favorite_planets": serialized_planets
        }
        
        return jsonify(response_body), 200

    except Exception as e:
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    try:
        data = request.get_json()

        if not data or "user_id" not in data:
            return jsonify({"error": "Missing required field: user_id"}), 400

        user_id = data["user_id"]

        user = db.session.execute(
            db.select(User).filter_by(id=user_id)
        ).scalar_one_or_none()
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        planet = db.session.execute(
            db.select(Planets).filter_by(id=planet_id)
        ).scalar_one_or_none() 
        if not planet:
            return jsonify({"error": "Planet not found"}), 404

        existing_fav = db.session.execute(
            db.select(Favorites_planets).filter_by(user_id=user_id, planet_id=planet_id)
        ).scalar_one_or_none()  
        if existing_fav:
            return jsonify({"error": "Planet already in favorites"}), 409

        new_fav_planet = Favorites_planets(user_id=user_id, planet_id=planet_id)
        db.session.add(new_fav_planet)
        db.session.commit()

        return jsonify({"message": "Favorite added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    try:
        data = request.get_json()

        if not data or "user_id" not in data:
            return jsonify({"error": "Missing required field: user_id"}), 400

        user_id = data["user_id"]

        user = db.session.execute(
            db.select(User).filter_by(id=user_id)
        ).scalar_one_or_none()
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        person = db.session.execute(
            db.select(People).filter_by(id=people_id)
        ).scalar_one_or_none() 
        if not person:
            return jsonify({"error": "Person not found"}), 404

        # Evitar duplicados
        existing_fav = db.session.execute(
            db.select(Favorites_people).filter_by(user_id=user_id, people_id=people_id)
        ).scalar_one_or_none()  
        if existing_fav:
            return jsonify({"error": "Person already in favorites"}), 409

        new_fav_person = Favorites_people(user_id=user_id, people_id=people_id)
        db.session.add(new_fav_person)
        db.session.commit()

        return jsonify({"message": "Favorite added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/favorites/planet/<int:id>', methods=['DELETE'])
def delete_favorites_planet(id):
    try:

        favorite_planet = db.session.execute(db.select(Favorites_planets).filter_by(id=id)).scalar_one()
        
        if favorite_planet is None:
            return jsonify({"msg": "Planet favorite not found"}), 404
        
        db.session.delete(favorite_planet)
        db.session.commit()

        return jsonify({"msg": "Favorite planet deleted successfully"}), 200

    except Exception as e:
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    
@app.route('/favorites/people/<int:id>', methods=['DELETE'])
def delete_favorites_people(id):
    try:
      
        favorite_people = db.session.execute(db.select(Favorites_people).filter_by(id=id)).scalar_one()
        
        if favorite_people is None:
            return jsonify({"msg": "Person favorite not found"}), 404
        
        db.session.delete(favorite_people)
        db.session.commit()

        return jsonify({"msg": "Favorite planet deleted successfully"}), 200

    except Exception as e:
     
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500


#RUTAS PEOPLE:

@app.route('/people', methods=['GET'])
def get_all_people():
    try:
        data = db.session.scalars(db.select(People)).all()
        
        if not data:
            return jsonify({"msg": "No people found"}), 404
        
        result = list(map(lambda item: item.serialize(), data))
    
        response_body = {
            "results": result
        }
        
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    

@app.route('/people/<int:id>', methods=['GET'])
def get_one_person(id):
    try:
        person = db.session.execute(db.select(People).filter_by(id=id)).scalar_one()
       
        if person is None:
            return jsonify({"msg": "No person found"}), 404

        result = person.serialize()
        
        response_body = {
            "result": result
        }
        
        return jsonify(response_body), 200

    except Exception as e:
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    
@app.route('/people', methods=['POST'])
def create_person():
    try:
        request_body = request.json
        print(request_body)

        existing_person = db.session.execute(
            db.select(People).filter_by(name=request_body["name"])
        ).scalar_one()

        if existing_person:
            return jsonify({"result": "person exists"}), 400
        
        # Si no existe, instanciar y agregar la nueva persona
        new_person = People(
            name=request_body["name"],
            height=request_body["height"],
            mass=request_body["mass"],
            birth_year=request_body["birth_year"],
            homeworld=request_body["homeworld"]
        )
        
        db.session.add(new_person)
        db.session.commit()
        
        return jsonify({"msg": "created"}), 201

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/people/<int:people_id>', methods=['PUT'])
def updated_people(people_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        person = db.session.execute(
            db.select(People).filter_by(id=people_id)
        ).scalar_one_or_none()

        if not person:
            return jsonify({"error": "Person not found"}), 404

        if 'name' in data:
            person.name = data['name']
        if 'height' in data:
            person.height = data['height']
        if 'mass' in data:
            person.mass = data['mass']
        if 'birth_year' in data:
            person.birth_year = data['birth_year']
        if 'homeworld' in data:
            person.homeworld = data['homeworld']

        db.session.commit()
        return jsonify({"message": "Person updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/people/<int:id>', methods=['DELETE'])
def delete_people(id):
    try:
       
        person = db.session.execute(db.select(People).filter_by(id=id)).scalar_one()
        
        if person is None:
            return jsonify({"msg": "Person not found"}), 404
        
        db.session.delete(person)
        db.session.commit()

        return jsonify({"msg": "Person deleted successfully"}), 200

    except Exception as e:
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500

  
#RUTAS PLANETAS

@app.route('/planets', methods=['GET'])
def get_all_planets():
    try:
        data = db.session.scalars(db.select(Planets)).all()

        if not data:
            return jsonify({"msg": "No planets found"}), 404
        
        result = list(map(lambda item: item.serialize(), data))
        
        response_body = {
            "results": result
        }
        
        return jsonify(response_body), 200

    except Exception as e:
    
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    
@app.route('/planet/<int:id>', methods=['GET'])
def get_one_planet(id):
    try:
   
        planet = db.session.execute(db.select(Planets).filter_by(id=id)).scalar_one()
        
        if planet is None:
            return jsonify({"msg": "No planet found"}), 404
        
        result = planet.serialize()
        
        response_body = {
            "result": result
        }
        
        return jsonify(response_body), 200

    except Exception as e:
      
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500


@app.route('/planet', methods=['POST'])
def create_planet():
    try:
      
        request_body = request.json
        planet = db.session.execute(db.select(Planets).filter_by(name = request_body["name"])).scalar_one()
        
        if planet:
            return jsonify({"result": "planet exists"}), 400
        
     
        planet = Planets(
            name=request_body["name"],
            climate=request_body["climate"],
            diameter=request_body["diameter"],
            orbital_period=request_body["orbital_period"],
            population=request_body["population"]
        )
        
        db.session.add(planet)
        db.session.commit()
        
        return jsonify({"msg": "planet created"}), 201 
    except Exception as e:
        return jsonify({"error": str(e)}), 500  

@app.route('/planet/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        planet = db.session.execute(
            db.select(Planets).filter_by(id=planet_id)
        ).scalar_one_or_none()

        if not planet:
            return jsonify({"error": "Planet not found"}), 404

        if "name" in data:
            planet.name = data["name"]
        if "climate" in data:
            planet.climate = data["climate"]
        if "diameter" in data:
            planet.diameter = data["diameter"]
        if "orbital_period" in data:
            planet.orbital_period = data["orbital_period"]
        if "population" in data:
            planet.population = data["population"]

        db.session.commit()
        return jsonify({"message": "Planet updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/planet/<int:id>', methods=['DELETE'])
def delete_planet(id):
    try:
   
        planet = db.session.execute(db.select(Planets).filter_by(id=id)).scalar_one()
        
       
        if planet is None:
            return jsonify({"msg": "Planet not found"}), 404
        
        db.session.delete(planet)
        db.session.commit()

        return jsonify({"msg": "Planet deleted successfully"}), 200

    except Exception as e:
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
