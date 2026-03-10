from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

recipes = []
ingredients = []
instructions = []
nutrition_info = []
favorites = []

@app.route('/')
def root():
    return jsonify({"message": "API is running", "endpoints": [
        "/api/health",
        "/api/recipes",
        "/api/recipes/:id",
        "/api/recipes/search",
        "/api/recipes/favorites",
        "/api/recipes/:id/favorite"
    ]})

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    return jsonify(recipes)

@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    data = request.get_json() or {}
    if 'title' not in data or 'ingredients' not in data or 'instructions' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    recipe = {
        'id': uuid.uuid4().hex[:8],
        'title': data['title'],
        'ingredients': data['ingredients'],
        'instructions': data['instructions']
    }
    recipes.append(recipe)
    return jsonify(recipe), 201

@app.route('/api/recipes/<id>', methods=['GET'])
def get_recipe(id):
    for recipe in recipes:
        if recipe['id'] == id:
            return jsonify(recipe)
    return jsonify({"error": "Recipe not found"}), 404

@app.route('/api/recipes/<id>', methods=['PUT'])
def update_recipe(id):
    data = request.get_json() or {}
    if 'title' not in data or 'ingredients' not in data or 'instructions' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    for recipe in recipes:
        if recipe['id'] == id:
            recipe['title'] = data['title']
            recipe['ingredients'] = data['ingredients']
            recipe['instructions'] = data['instructions']
            return jsonify(recipe)
    return jsonify({"error": "Recipe not found"}), 404

@app.route('/api/recipes/<id>', methods=['DELETE'])
def delete_recipe(id):
    for recipe in recipes:
        if recipe['id'] == id:
            recipes.remove(recipe)
            return jsonify({"message": "Recipe deleted"})
    return jsonify({"error": "Recipe not found"}), 404

@app.route('/api/recipes/search', methods=['GET'])
def search_recipes():
    query = request.args.get('q')
    results = [recipe for recipe in recipes if query in recipe['title'] or query in recipe['ingredients'] or query in recipe['instructions']]
    return jsonify(results)

@app.route('/api/recipes/favorites', methods=['GET'])
def get_favorites():
    return jsonify(favorites)

@app.route('/api/recipes/<id>/favorite', methods=['POST'])
def favorite_recipe(id):
    for recipe in recipes:
        if recipe['id'] == id:
            if recipe not in favorites:
                favorites.append(recipe)
                return jsonify({"message": "Recipe favorited"})
            else:
                return jsonify({"error": "Recipe already favorited"}), 400
    return jsonify({"error": "Recipe not found"}), 404

@app.route('/api/recipes/<id>/favorite', methods=['DELETE'])
def unfavorite_recipe(id):
    for recipe in recipes:
        if recipe['id'] == id:
            if recipe in favorites:
                favorites.remove(recipe)
                return jsonify({"message": "Recipe unfavorited"})
            else:
                return jsonify({"error": "Recipe not favorited"}), 400
    return jsonify({"error": "Recipe not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)