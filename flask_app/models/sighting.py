# import the function that will return an instance of a connection
from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_bcrypt import Bcrypt
from flask_app.models import user
import re

DB = "belt_exam"

class Sighting:
    
    def __init__(self, sighting):
        self.id = sighting["id"]
        self.location = sighting["location"]
        self.what_happened = sighting["what_happened"]
        self.date = sighting["date"]
        self.sasquatches = sighting["sasquatches"]
        self.created_at = sighting["created_at"]
        self.updated_at = sighting["updated_at"]
        self.user = None

    @classmethod
    def create_valid_sighting(cls, sighting_dict):
        if not cls.is_valid(sighting_dict):
            return False
        
        query = """INSERT INTO sightings (location, what_happened, date, sasquatches, user_id) VALUES (%(location)s, %(what_happened)s, %(date)s, %(sasquatches)s, %(user_id)s);"""
        sighting_id = connectToMySQL(DB).query_db(query, sighting_dict)
        sighting = cls.get_by_id(sighting_id)

        return sighting

    @classmethod
    def get_by_id(cls, sighting_id):
        print(f"get sighting by id {sighting_id}")
        data = {"id": sighting_id}
        query = """SELECT sightings.id, sightings.created_at, sightings.updated_at, location, what_happened, date, sasquatches,
                    users.id as user_id, first_name, last_name, email, password, users.created_at as uc, users.updated_at as uu
                    FROM sightings
                    JOIN users on users.id = sightings.user_id
                    WHERE sightings.id = %(id)s;"""
        
        result = connectToMySQL(DB).query_db(query,data)
        print("result of query:")
        print(result)
        result = result[0]
        sighting = cls(result)
        
        sighting.user = user.User(
                {
                    "id": result["user_id"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "email": result["email"],
                    "password": result["password"],
                    "created_at": result["uc"],
                    "updated_at": result["uu"]
                }
            )

        return sighting

    @classmethod
    def delete_sighting_by_id(cls, sighting_id):

        data = {"id": sighting_id}
        query = "DELETE from sightings WHERE id = %(id)s;"
        connectToMySQL(DB).query_db(query,data)

        return sighting_id


    @classmethod
    def update_sighting(cls, sighting_dict, session_id):

        sighting = cls.get_by_id(sighting_dict["id"])
        if sighting.user.id != session_id:
            flash("You must be the creator to update this sighting.")
            return False

        if not cls.is_valid(sighting_dict):
            return False
        
        query = """UPDATE sightings
                    SET location = %(location)s, what_happened = %(what_happened)s, date = %(date)s, sasquatches = %(sasquatches)s
                    WHERE id = %(id)s;"""
        result = connectToMySQL(DB).query_db(query,sighting_dict)
        sighting = cls.get_by_id(sighting_dict["id"])
        
        return sighting

    @classmethod
    def get_all(cls):
        query = """SELECT 
                    sightings.id, sightings.created_at, sightings.updated_at, location, what_happened, date, sasquatches,
                    users.id as user_id, first_name, last_name, email, password, users.created_at as uc, users.updated_at as uu
                    FROM sightings
                    JOIN users on users.id = sightings.user_id;"""
        sighting_data = connectToMySQL(DB).query_db(query)

        sightings = []

        for sighting in sighting_data:

            sighting_obj = cls(sighting)

            sighting_obj.user = user.User(
                {
                    "id": sighting["user_id"],
                    "first_name": sighting["first_name"],
                    "last_name": sighting["last_name"],
                    "email": sighting["email"],
                    "password": sighting["password"],
                    "created_at": sighting["uc"],
                    "updated_at": sighting["uu"]
                }
            )
            sightings.append(sighting_obj)


        return sightings

    @staticmethod
    def is_valid(sighting_dict):
        valid = True
        flash_string = " field is required and must be at least 3 characters."
        if len(sighting_dict["location"]) < 3:
            flash("Location " + flash_string)
            valid = False
        if len(sighting_dict["what_happened"]) < 3:
            flash("This " + flash_string)
            valid = False
        if len(sighting_dict["date"]) <= 0:
            flash("Date is required.")
            valid = False
        if len(sighting_dict["sasquatches"]) <= 0:
            flash("Please report the number of Sasquatches seen.")
            valid = False

        return valid
        