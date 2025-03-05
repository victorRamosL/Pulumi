from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Configuración de MongoDB Atlas
client = MongoClient("mongodb+srv://frodo:bolson@cluster0.asmcd.mongodb.net/")
db = client['victor']  # Base de datos
collection = db['ecommerce']  # Colección

# Ruta principal para mostrar la página de búsqueda
@app.route('/')
def index():
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>E-Commerce Product Search</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f9f9f9;
                    color: #333;
                }
                header {
                    background-color: #4CAF50;
                    padding: 10px;
                    text-align: center;
                    color: white;
                }
                .container {
                    padding: 20px;
                    max-width: 800px;
                    margin: 0 auto;
                }
                .search-bar {
                    display: flex;
                    margin-bottom: 20px;
                }
                .search-bar input[type="text"] {
                    flex: 1;
                    padding: 10px;
                    font-size: 16px;
                    border: 1px solid #ccc;
                    border-radius: 4px 0 0 4px;
                }
                .search-bar button {
                    padding: 10px 20px;
                    font-size: 16px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    cursor: pointer;
                    border-radius: 0 4px 4px 0;
                }
                .search-bar button:hover {
                    background-color: #45a049;
                }
                .product {
                    background-color: white;
                    margin-bottom: 10px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                .product h2 {
                    margin: 0;
                    font-size: 20px;
                }
                .product p {
                    margin: 5px 0;
                }
                .product span {
                    font-weight: bold;
                    color: #4CAF50;
                }
            </style>
        </head>
        <body>
            <header>
                <h1>E-Commerce Product Search</h1>
            </header>
            <div class="container">
                <form class="search-bar" onsubmit="performSearch(event)">
                    <input type="text" id="query" placeholder="Search for a product..." />
                    <button type="submit">Search</button>
                </form>
                <div id="results"></div>
            </div>
        
            <script>
                async function performSearch(event) {
                    event.preventDefault();
                    const query = document.getElementById('query').value;
                    const resultsDiv = document.getElementById('results');
                    resultsDiv.innerHTML = '<p>Searching...</p>';
        
                    try {
                        const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
                        const products = await response.json();
        
                        if (products.length === 0) {
                            resultsDiv.innerHTML = '<p>No products found.</p>';
                            return;
                        }
        
                        resultsDiv.innerHTML = products.map(product => `
                            <div class="product">
                                <h2>${product.name}</h2>
                                <p>${product.description}</p>
                                <p>Category: ${product.category}</p>
                                <p>Price: <span>$${product.price.toFixed(2)}</span></p>
                            </div>
                        `).join('');
                    } catch (error) {
                        resultsDiv.innerHTML = '<p>Error fetching results. Please try again.</p>';
                        console.error('Search error:', error);
                    }
                }
            </script>
        </body>
        </html>
    '''

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
