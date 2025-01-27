from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import torch

app = Flask(__name__)
CORS(app)

model = SentenceTransformer('all-MiniLM-L6-v2')

books = [
    {"title": "Understanding AI", "description": "A comprehensive guide to artificial intelligence and its applications."},
    {"title": "Adventures in Space", "description": "A thrilling journey through the cosmos with astronauts."},
    {"title": "Mystery of the Lost Island", "description": "A gripping tale of adventure and mystery on a deserted island."},
    {"title": "Cooking 101", "description": "Learn the basics of cooking with easy and fun recipes."},
    {"title": "The Art of Data Science", "description": "A detailed exploration of data analysis and machine learning techniques."},
]

book_descriptions = [book["description"] for book in books]
book_embeddings = model.encode(book_descriptions, convert_to_tensor=True)

@app.route('/api/search', methods=['POST'])
def search_books():
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 3)

        query_embedding = model.encode(query, convert_to_tensor=True)

        similarity_scores = util.pytorch_cos_sim(query_embedding, book_embeddings)[0]

        top_results = torch.topk(similarity_scores, k=min(top_k, len(books)))

        results = []
        for score, idx in zip(top_results.values, top_results.indices):
            results.append({
                "title": books[idx]["title"],
                "description": books[idx]["description"],
                "score": float(score)
            })

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
