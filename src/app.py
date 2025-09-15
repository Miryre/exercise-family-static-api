"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
# from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# Create the jackson family object
jackson_family = FamilyStructure("Jackson")


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# 1. GET /members - Get all family members
@app.route('/members', methods=['GET'])
def get_all_members():
    try:
        members = jackson_family.get_all_members()
        return jsonify(members), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


# 2. GET /members/<int:member_id> - Get a specific member
@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    try:
        member = jackson_family.get_member(member_id)
        if member is None:
            return jsonify({"error": "Member not found"}), 404
        return jsonify(member), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


# 3. POST /members - Add a new member
@app.route('/members', methods=['POST'])
def add_member():
    try:
        # Get the request body
        member_data = request.get_json()
        
        # Validate required fields
        if not member_data:
            return jsonify({"error": "Request body is required"}), 400
            
        required_fields = ["first_name", "age", "lucky_numbers"]
        for field in required_fields:
            if field not in member_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate data types
        if not isinstance(member_data["first_name"], str):
            return jsonify({"error": "first_name must be a string"}), 400
            
        if not isinstance(member_data["age"], int) or member_data["age"] <= 0:
            return jsonify({"error": "age must be a positive integer"}), 400
            
        if not isinstance(member_data["lucky_numbers"], list):
            return jsonify({"error": "lucky_numbers must be a list"}), 400
        
        # Add the member
        new_member = jackson_family.add_member(member_data)
        return jsonify(new_member), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


# 4. DELETE /members/<int:member_id> - Delete a member
@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    try:
        success = jackson_family.delete_member(member_id)
        if not success:
            return jsonify({"error": "Member not found"}), 404
        return jsonify({"done": True}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
