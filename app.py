from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Configuración de MongoDB Atlas
client = MongoClient("mongodb+srv://frodo:bolson@cluster0.asmcd.mongodb.net/")
db = client['victor']  # Base de datos
collection = db['ecommerce']  # Colección

# Ruta principal para mostrar la página de búsqueda
@app.route('/')
def index():
    return render_template('/templates/search.html')

# Ruta para realizar la búsqueda
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    products = list(collection.find({"name": {"$regex": query, "$options": "i"}}))
    print("Productos encontrados:", products)  # Log de los resultados
    return jsonify(products)
    if not query:
        return jsonify({"error": "Query is required"}), 400

    # Usar Atlas Search para realizar la consulta
    pipeline = [
        {
            "$search": {
                "index": "default",  # Nombre del índice de búsqueda en Atlas
                "text": {
                    "query": query,
                    "path": ["name", "description", "category", "tags"]  # Campos a buscar
                }
            }
        },
        {
            "$limit": 10  # Limitar los resultados
        }
    ]

    results = list(collection.aggregate(pipeline))
    return jsonify(results)

# Insertar productos de ejemplo
@app.route('/add-sample-data', methods=['POST'])
def add_sample_data():
    sample_data = [
        {"name": "Mouse", "description": "Wireless mouse", "category": "Electronics", "price": 20, "brand": "Logitech", "tags": ["wireless", "computer", "accessory"]},
        {"name": "Keyboard", "description": "Mechanical keyboard", "category": "Electronics", "price": 50, "brand": "Corsair", "tags": ["mechanical", "computer", "accessory"]},
        {"name": "Headphones", "description": "Noise-cancelling headphones", "category": "Electronics", "price": 100, "brand": "Sony", "tags": ["audio", "music", "headphones"]},
        {"name": "Smartphone", "description": "Android smartphone", "category": "Electronics", "price": 300, "brand": "Samsung", "tags": ["phone", "android", "mobile"]},
        {"name": "Desk Chair", "description": "Ergonomic desk chair", "category": "Furniture", "price": 120, "brand": "Herman Miller", "tags": ["furniture", "chair", "ergonomic"]}
    ]
    collection.insert_many(sample_data)
    return jsonify({"message": "Sample data added successfully!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
