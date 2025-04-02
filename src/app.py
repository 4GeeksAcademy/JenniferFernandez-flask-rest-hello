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
# from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import NoResultFound
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
    
@app.route('/user', methods=['POST'])
def create_user():
    try:
        request_body = request.json
        print(request_body)
        # email = request.json.get("email", None)
        # password = request.json.get("password", None)

        # Verifica si la persona ya existe en la base de datos
        existing_user = db.session.execute(
            db.select(User).filter_by(email=request_body["email"])
        ).scalar_one_or_none()

        if existing_user:
            return jsonify({"result": "user exists"}), 400
        
        # Si no existe, instanciar y agregar la nueva persona
        new_user = User(
            name=request_body["name"],
            last_name=request_body["last_name"],
            email=request_body["email"],
            password=request_body["password"]
            
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"msg": "created"}), 201
        # Genera el token JWT
        # access_token = create_access_token(identity=email)
        # return jsonify({"access_token": access_token, "User": new_user.serialize()}), 201
    except KeyError as e:
        # Manejo de errores cuando faltan campos en el cuerpo de la solicitud
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    
    except Exception as e:
        # Manejo de otros errores generales
        return jsonify({"error": str(e)}), 500
    
# @app.route("/register", methods=["POST"])
# def register():
#     try:
#         email = request.json.get("email", None)
#         password = request.json.get("password", None)

#         # Comprueba si el usuario ya existe
#         existing_user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
#         if existing_user:
#             return jsonify({"msg": "User already exists"}), 400

#         # Crea un nuevo usuario
#         hashed_password = generate_password_hash(password)  # Almacena la contraseña de forma segura
#         new_user = User(email=email, password=hashed_password)
#         db.session.add(new_user)
#         db.session.commit()

#         # Genera el token JWT
#         access_token = create_access_token(identity=email)
#         return jsonify({"access_token": access_token, "User": new_user.serialize()}), 201

#     except Exception as e:
#         return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    
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
    
#no puedo eliminar people por ID por la relación de favoritos entre tablas




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
        # required_fields = ["name", "climate", "diameter", "orbital_period", "population"]
        # for field in required_fields:
        #     if field not in request_body:
        #         return jsonify({"error": f"Missing field: {field}"}), 400

        # Verificar si el planeta ya existe
        planet = db.session.execute(db.select(Planets).filter_by(name = request_body["name"])).scalar_one_or_none()
        
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
        planet = db.session.execute(db.select(Planets).filter_by(id=id)).scalar_one()
        
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


#FAVORITOS

@app.route("/favorites", methods=["GET"])
#portero, pide la autenticación
# @jwt_required()
def protected():
    # current_user = get_jwt_identity()
    user = db.session.execute(db.select(User).filter_by(id=id)).scalar_one()
    print(user.id)
    
    # Access the identity of the current user with get_jwt_identity
    
    favorites = list(db.session.execute(db.select(Favorites_people).filter_by(user_id = user.id)).scalars())
    print(user.favorites)
    results = list(map(lambda item: item.serialize(),user.favorites))
    print(results)
    return jsonify({"results":results}), 200


@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    try:
        # Obtener el usuario por ID
        user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()
        
        if user is None:
            return jsonify({"msg": "User not found"}), 404
        
        # Obtener los favoritos de personas
        favorite_people_ids = db.session.execute(
            db.select(Favorites_people.people_id).filter_by(user_id=user_id)
        ).scalars().all()
        
        # Obtener los favoritos de planetas
        favorite_planets_ids = db.session.execute(
            db.select(Favorites_planets.planets_id).filter_by(user_id=user_id)
        ).scalars().all()
        
        # Obtener detalles de las personas favoritas
        favorite_people = []
        if favorite_people_ids:
            favorite_people = db.session.scalars(
                db.select(People).filter(People.id.in_(favorite_people_ids))
            ).all()
        
        # Obtener detalles de los planetas favoritos
        favorite_planets = []
        if favorite_planets_ids:
            favorite_planets = db.session.scalars(
                db.select(Planets).filter(Planets.id.in_(favorite_planets_ids))
            ).all()
        
        # Serializa los resultados
        serialized_people = [person.serialize() for person in favorite_people]
        serialized_planets = [planet.serialize() for planet in favorite_planets]
        
        # Construir la respuesta
        response_body = {
            "favorite_people": serialized_people,
            "favorite_planets": serialized_planets
        }
        
        return jsonify(response_body), 200

    except Exception as e:
        # Maneja cualquier otro tipo de error
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500
    

# @app.route('/favorite/planet', methods=['POST'])
# def create_planet():
#     try:
#         # Obtener el cuerpo de la solicitud
#         request_body = request.json
        
#         # Validar que el cuerpo de la solicitud tenga los campos requeridos
#         # required_fields = ["name", "climate", "diameter", "orbital_period", "population"]
#         # for field in required_fields:
#         #     if field not in request_body:
#         #         return jsonify({"error": f"Missing field: {field}"}), 400

#         # Verificar si el planeta ya existe
#         planet = db.session.execute(db.select(Planets).filter_by(name = request_body["name"])).scalar_one_or_none()
        
#         if planet:
#             return jsonify({"result": "planet exists"}), 400
        
#         # Crear una nueva instancia de Planets
#         planet = Planets(
#             name=request_body["name"],
#             climate=request_body["climate"],
#             diameter=request_body["diameter"],
#             orbital_period=request_body["orbital_period"],
#             population=request_body["population"]
#         )
        
#         # Agregar el planeta a la sesión y confirmar los cambios
#         db.session.add(planet)
#         db.session.commit()
        
#         return jsonify({"msg": "planet created"}), 201  # Cambiar a 201 para indicar creación exitosa
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500  # Capturar cualquier otro error inesperado

# [GET] /people Listar todos los registros de people en la base de datos. -----------
# [GET] /people/<int:people_id> Muestra la información de un solo personaje según su id.----------
# [GET] /planets Listar todos los registros de planets en la base de datos.----------
# [GET] /planets/<int:planet_id> Muestra la información de un solo planeta según su id.-----------
# Adicionalmente, necesitamos crear los siguientes endpoints para que podamos tener usuarios y favoritos en nuestro blog:

# [GET] /users Listar todos los usuarios del blog.----------
# [GET] /users/favorites Listar todos los favoritos que pertenecen al usuario actual.----¿por id?
# [POST] /favorite/planet/<int:planet_id> Añade un nuevo planet favorito al usuario actual con el id = planet_id.
# [POST] /favorite/people/<int:people_id> Añade un nuevo people favorito al usuario actual con el id = people_id.
# [DELETE] /favorite/planet/<int:planet_id> Elimina un planet favorito con el id = planet_id.
# [DELETE] /favorite/people/<int:people_id> Elimina un people favorito con el id = people_id.

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    try:
        # Suponiendo que tienes un método para obtener el usuario actual
        # Esto puede ser a través de un token de sesión, JWT, etc.
        user = get_current_user()  # Implementa esta función según tu lógica de autenticación
        
        if user is None:
            return jsonify({"msg": "User not found"}), 404
        
        # Obtener los favoritos de personas
        favorite_people_ids = db.session.execute(
            db.select(Favorites_people.people_id).filter_by(user_id=user.id)  # Usa user.id
        ).scalars().all()
        
        # Obtener los favoritos de planetas
        favorite_planets_ids = db.session.execute(
            db.select(Favorites_planets.planets_id).filter_by(user_id=user.id)  # Usa user.id
        ).scalars().all()
        
        # Obtener detalles de las personas favoritas
        favorite_people = []
        if favorite_people_ids:
            favorite_people = db.session.scalars(
                db.select(People).filter(People.id.in_(favorite_people_ids))
            ).all()
        
        # Obtener detalles de los planetas favoritos
        favorite_planets = []
        if favorite_planets_ids:
            favorite_planets = db.session.scalars(
                db.select(Planets).filter(Planets.id.in_(favorite_planets_ids))
            ).all()
        
        # Serializa los resultados
        serialized_people = [person.serialize() for person in favorite_people]
        serialized_planets = [planet.serialize() for planet in favorite_planets]
        
        # Construir la respuesta
        response_body = {
            "favorite_people": serialized_people,
            "favorite_planets": serialized_planets
        }
        
        return jsonify(response_body), 200

    except Exception as e:
        # Maneja cualquier otro tipo de error
        return jsonify({"msg": "An error occurred", "error": str(e)}), 500

# def get_current_user():
#     # Implementa la lógica para obtener el usuario actual
#     # Por ejemplo, podrías extraer el token de autenticación de los headers
#     # y usarlo para buscar el usuario en la base de datos
#     current_user = get_jwt_identity()
#     user = db.session.execute(db.select(User).filter_by(email=current_user)).scalar_one()
#     auth_header = request.headers.get('Authorization')
#     results = list(map(lambda item: item.serialize(),user.favorites))
#     print(results)
#     return jsonify({"results":results}), 200

# def protected():
#     current_user = get_jwt_identity()
#     user = db.session.execute(db.select(User).filter_by(email=current_user)).scalar_one()
#     print(user.id)
#     print(user.favorites)
#     # Access the identity of the current user with get_jwt_identity
#     # favorites = list(db.session.execute(db.select(Favorites).filter_by(user_id = user.id)).scalars())
#     results = list(map(lambda item: item.serialize(),user.favorites))
#     print(results)
#     return jsonify({"results":results}), 200




















# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
