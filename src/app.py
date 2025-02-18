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

# @app.route('/user', methods=['GET'])
# def handle_hello():

#     response_body = {
#         "msg": "Hello, this is your GET /user response "
#     }

#     return jsonify(response_body), 200

#RUTAS USUARIO:

@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        # Realiza la consulta a la base de datos
        data = db.session.scalars(db.select(User)).all()
        
        # Comprueba si hay resultados
        if not data:
            return jsonify({"msg": "No users found"}), 404
        
        # Serializa los resultados
        result = list(map(lambda item: item.serialize(), data))
        
        # Construye la respuesta
        response_body = {
            "results": result
        }
        
        return jsonify(response_body), 200

    except Exception as e:
        # Maneja cualquier otro tipo de error
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    
# @app.route('/users/favorites', methods=['GET'])
# def get_favorites_users():
#     try:
#         # Realiza la consulta a la base de datos
#         data = db.session.scalars(db.select(Favorites_people)).all()
        
#         # Comprueba si hay resultados
#         if not data:
#             return jsonify({"msg": "No users found"}), 404
        
#         # Serializa los resultados
#         result = list(map(lambda item: item.serialize(), data))
        
#         # Construye la respuesta
#         response_body = {
#             "results": result
#         }
        
#         return jsonify(response_body), 200

#     except Exception as e:
#         # Maneja cualquier otro tipo de error
#         return jsonify({"msg": "An error occurred", "error": str(e)}), 500


#RUTAS PEOPLE:

@app.route('/people', methods=['GET'])
def get_all_people():
    try:
        # Realiza la consulta a la base de datos
        data = db.session.scalars(db.select(People)).all()
        
        # Comprueba si hay resultados
        if not data:
            return jsonify({"msg": "No people found"}), 404
        
        # Serializa los resultados
        result = list(map(lambda item: item.serialize(), data))
        
        # Construye la respuesta
        response_body = {
            "results": result
        }
        
        return jsonify(response_body), 200

    except Exception as e:
        # Maneja cualquier otro tipo de error
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    

@app.route('/people/<int:id>', methods=['GET'])
def get_one_person(id):
    try:
        # Obtiene la persona de la base de datos
        person = db.session.execute(db.select(People).filter_by(id=id)).scalar_one()
        
        # Comprueba si hay resultados
        if person is None:
            return jsonify({"msg": "No person found"}), 404
        
        # Serializa el resultado
        result = person.serialize()
        
        # Construye la respuesta
        response_body = {
            "result": result
        }
        
        return jsonify(response_body), 200

    except Exception as e:
        # Maneja cualquier otro tipo de error
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    
@app.route('/people', methods=['POST'])
def create_person():
    try:
        request_body = request.json
        print(request_body)

        # Verifica si la persona ya existe en la base de datos
        existing_person = db.session.execute(
            db.select(People).filter_by(name=request_body["name"])
        ).scalar_one_or_none()

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
        # Manejo de errores cuando faltan campos en el cuerpo de la solicitud
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    
    except Exception as e:
        # Manejo de otros errores generales
        return jsonify({"error": str(e)}), 500


@app.route('/people/<int:id>', methods=['DELETE'])
def delete_people(id):
    try:
        # Obtiene el personaje de la base de datos
        person = db.session.execute(db.select(People).filter_by(id=id)).scalar_one_or_none()
        
        # Comprueba si el personaje existe
        if person is None:
            return jsonify({"msg": "Person not found"}), 404
        
        # Elimina el personaje
        db.session.delete(person)
        db.session.commit()

        return jsonify({"msg": "Person deleted successfully"}), 200

    except Exception as e:
        # Maneja cualquier otro tipo de error
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    





#RUTAS PLANETAS

@app.route('/planets', methods=['GET'])
def get_all_planets():
    try:
     # Realiza la consulta a la base de datos
        data = db.session.scalars(db.select(Planets)).all()

        # Comprueba si hay resultados
        if not data:
            return jsonify({"msg": "No planets found"}), 404
        
        # Serializa los resultados
        result = list(map(lambda item: item.serialize(), data))
        
        # Construye la respuesta
        response_body = {
            "results": result
        }
        
        return jsonify(response_body), 200

    except Exception as e:
        # Maneja cualquier otro tipo de error
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    
@app.route('/planets/<int:id>', methods=['GET'])
def get_one_planet(id):
    try:
        # Obtiene la persona de la base de datos
        planet = db.session.execute(db.select(Planets).filter_by(id=id)).scalar_one()
        
        # Comprueba si hay resultados
        if planet is None:
            return jsonify({"msg": "No planet found"}), 404
        
        # Serializa el resultado
        result = planet.serialize()
        
        # Construye la respuesta
        response_body = {
            "result": result
        }
        
        return jsonify(response_body), 200

    except Exception as e:
        # Maneja cualquier otro tipo de error
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500


@app.route('/planet', methods=['POST'])
def create_planet():
    try:
        # Obtener el cuerpo de la solicitud
        request_body = request.json
        
        # Validar que el cuerpo de la solicitud tenga los campos requeridos
        required_fields = ["name", "climate", "diameter", "orbital_period", "population"]
        for field in required_fields:
            if field not in request_body:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Verificar si el planeta ya existe
        planet = db.session.execute(db.select(Planets).filter_by(name=request_body["name"])).scalar_one_or_none()
        
        if planet:
            return jsonify({"result": "planet exists"}), 400
        
        # Crear una nueva instancia de Planets
        planet = Planets(
            name=request_body["name"],
            climate=request_body["climate"],
            diameter=request_body["diameter"],
            orbital_period=request_body["orbital_period"],
            population=request_body["population"]
        )
        
        # Agregar el planeta a la sesión y confirmar los cambios
        db.session.add(planet)
        db.session.commit()
        
        return jsonify({"msg": "planet created"}), 201  # Cambiar a 201 para indicar creación exitosa
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Capturar cualquier otro error inesperado


@app.route('/planet/<int:id>', methods=['DELETE'])
def delete_planet(id):
    try:
        # Obtiene el planeta de la base de datos
        planet = db.session.execute(db.select(Planets).filter_by(id=id)).scalar_one_or_none()
        
        # Comprueba si el planeta existe
        if planet is None:
            return jsonify({"msg": "Planet not found"}), 404
        
        # Elimina el planeta
        db.session.delete(planet)
        db.session.commit()

        return jsonify({"msg": "Planet deleted successfully"}), 200

    except Exception as e:
        # Maneja cualquier otro tipo de error
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500




































# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
