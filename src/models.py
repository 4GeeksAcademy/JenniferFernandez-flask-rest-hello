from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, ForeignKey
from typing import List

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(8), nullable=False)
    favorite_people: Mapped[List["Favorites_people"]] = relationship()
    favorite_planets: Mapped[List["Favorites_planets"]] = relationship()
   

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "email": self.email
            
        }
    
class People(db.Model):
    __tablename__ = 'people'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=True)
    mass: Mapped[int] = mapped_column(Integer, nullable=True)
    birth_year: Mapped[int] = mapped_column(Integer, nullable=True)
    homeworld: Mapped[str] = mapped_column(String(50), nullable=True)
    # favorites: Mapped[List["Favorites_people"]] = relationship()
    favorites: Mapped[List["Favorites_people"]] = relationship(
        "Favorites_people",
        back_populates="people",
        cascade="all, delete-orphan"  #borrado en cascada de datos huerfanos
        
    )
    
  

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "birth_year":self.birth_year,
            "homeworld": self.homeworld
        }
    

class Planets(db.Model):
    __tablename__ = 'planets'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    climate: Mapped[str] = mapped_column(String(50), nullable=True)
    population: Mapped[int] = mapped_column(Integer, nullable=True)
    diameter: Mapped[int] = mapped_column(Integer, nullable=True)
    orbital_period: Mapped[int] = mapped_column(Integer, nullable=True)
    favorites: Mapped[List["Favorites_planets"]] = relationship(
        "Favorites_planets",
        back_populates="planet",
        cascade="all, delete-orphan"
    )
    
    
    

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population,
            "diameter": self.diameter,
            "orbital_period": self.orbital_period
        }

class Favorites_people(db.Model):
    __tablename__ = 'favorites_people'
    id: Mapped[int] = mapped_column(primary_key=True)
    # name: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    people_id: Mapped[int] = mapped_column(ForeignKey('people.id'), nullable=False)

    # user = db.relationship("User", backref="favorites_people")
    # people = db.relationship("People", backref="favorites_people")
    people = relationship("People", back_populates="favorites")

    # class Favorites_model(ModelView):
    # column_list = ('user_id', 'people_id', 'planet_id')
    # form_columns = ('user_id', 'people_id', 'planet_id')

    def serialize(self):
        return {
            "id": self.id,
            # "name": self.name,
            "user_id":self.user_id,
            "people_id":self.people_id
           
        }
    
class Favorites_planets(db.Model):
    __tablename__ = 'favorites_planets'
    id: Mapped[int] = mapped_column(primary_key=True)
    # name: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    planets_id: Mapped[int] = mapped_column(ForeignKey('planets.id'), nullable=False)
    # user = db.relationship()
    planet = relationship("Planets", back_populates="favorites")
    # user = db.relationship("User", backref="favorites_planets")
    # planets = db.relationship("Planets", backref="favorites_planets")


    def serialize(self):
        return {
            "id": self.id,
            # "name": self.name,
            "user_id":self.userid,
            "planets_id":self.planets_id
           
        }