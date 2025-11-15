from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database in memoria unificato
pets = [
    {"id": 1, "name": "Fido", "kind": "dog", "weight": 15.5, "foodWeightGrams": 500},
    {"id": 2, "name": "Whiskers", "kind": "cat", "weight": 4.2, "foodWeightGrams": 150},
    {"id": 3, "name": "Tweety", "kind": "bird", "weight": 0.8, "foodWeightGrams": 30},
    {"id": 4, "name": "Rex", "kind": "dog", "weight": 28.3, "foodWeightGrams": 800},
    {"id": 5, "name": "Luna", "kind": "cat", "weight": 3.8, "foodWeightGrams": 120},
    {"id": 6, "name": "Goldie", "kind": "fish", "weight": 0.05, "foodWeightGrams": 5},
    {"id": 7, "name": "Buddy", "kind": "dog", "weight": 22.1, "foodWeightGrams": 650},
    {"id": 8, "name": "Mittens", "kind": "cat", "weight": 5.1, "foodWeightGrams": 180},
    {"id": 9, "name": "Polly", "kind": "bird", "weight": 1.2, "foodWeightGrams": 45},
    {"id": 10, "name": "Max", "kind": "dog", "weight": 18.7, "foodWeightGrams": 550},
    {"id": 11, "name": "Shadow", "kind": "cat", "weight": 4.5, "foodWeightGrams": 160},
    {"id": 12, "name": "Nemo", "kind": "fish", "weight": 0.03, "foodWeightGrams": 3},
    {"id": 13, "name": "Bella", "kind": "dog", "weight": 12.4, "foodWeightGrams": 450},
    {"id": 14, "name": "Oliver", "kind": "cat", "weight": 4.9, "foodWeightGrams": 175},
    {"id": 15, "name": "Charlie", "kind": "hamster", "weight": 0.15, "foodWeightGrams": 20}
]

next_id = 16

@app.route('/pets', methods=['GET'])
def list_pets():
    """List all pets"""
    limit = request.args.get('limit', type=int)
    
    if limit:
        return jsonify(pets[:limit])
    
    return jsonify(pets)

@app.route('/pets', methods=['POST'])
def create_pet():
    """Create a new pet"""
    global next_id
    
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({"code": 400, "message": "Name is required"}), 400
    
    new_pet = {
        "id": next_id,
        "name": data['name'],
        "kind": data.get('kind', ''),
        "weight": data.get('weight', 0.0),
        "foodWeightGrams": data.get('foodWeightGrams', 0)
    }
    
    pets.append(new_pet)
    next_id += 1
    
    return jsonify(new_pet), 201

@app.route('/pets/<pet_id>', methods=['GET'])
def get_pet(pet_id):
    """Get a specific pet by ID"""
    pet = next((p for p in pets if str(p['id']) == pet_id), None)
    
    if pet:
        return jsonify(pet)
    
    return jsonify({"code": 404, "message": "Pet not found"}), 404

@app.route('/pets/<pet_id>/weight', methods=['GET'])
def get_pet_weight(pet_id):
    """Get pet weight"""
    pet_id_int = int(pet_id)
    
    # Cerca il pet
    pet = next((p for p in pets if p['id'] == pet_id_int), None)
    
    if not pet:
        return jsonify({"code": 404, "message": "Pet not found"}), 404
    
    # Restituisce solo id e peso
    return jsonify({
        "id": pet['id'],
        "weight": pet['weight']
    })

@app.route('/pets/<pet_id>/food', methods=['GET'])
def get_pet_food(pet_id):
    """Get pet food consumption"""
    pet_id_int = int(pet_id)
    
    # Cerca il pet
    pet = next((p for p in pets if p['id'] == pet_id_int), None)
    
    if not pet:
        return jsonify({"code": 404, "message": "Pet not found"}), 404
    
    # Restituisce solo id e cibo consumato
    return jsonify({
        "id": pet['id'],
        "foodWeightGrams": pet['foodWeightGrams']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)