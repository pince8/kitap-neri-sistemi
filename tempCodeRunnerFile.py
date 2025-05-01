from flask import Flask, render_template, request, jsonify
from model import recommend_books

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("index.html", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        book_title = data.get("title", "").strip()

        if not book_title:
            return jsonify({"error": "Kitap adı gerekli!"}), 400

        recommendations = recommend_books(book_title)

        if not recommendations:
            return jsonify({"message": "Öneri bulunamadı, farklı bir kitap deneyin."}), 404

        return jsonify(recommendations)

    except Exception as e:
        return jsonify({"error": f"Sunucu hatası: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
