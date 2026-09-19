from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# Load model once at startup, with error handling
try:
    model = joblib.load("uptor_004.pkl")
except FileNotFoundError:
    raise RuntimeError("Model file 'uptor_004.pkl' not found. Place it in the working directory.")

# Define ALL routes here before app.run()
@app.route("/")
def home():
    return "Welcome to my program"

@app.route("/uptor_04")
def AI_ML():
    return jsonify({
        "course": "AI & ML",
        "description": "This is the AI & ML Class",
        "status": "active"
    })

@app.route("/predict", methods=["POST"])
def predict():
    input_data = request.get_json(silent=True)
    if input_data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    normalized = {k.lower(): v for k, v in input_data.items()}

    if "sizes" not in normalized:
        return jsonify({"error": "Missing 'sizes' key"}), 400

    sizes = normalized["sizes"]

    # Accept either a single number or a list of numbers
    if isinstance(sizes, (int, float)):
        sizes = [sizes]
        single_input = True
    elif isinstance(sizes, list):
        if len(sizes) == 0:
            return jsonify({"error": "'sizes' list cannot be empty"}), 400
        if not all(isinstance(s, (int, float)) for s in sizes):
            return jsonify({"error": "'sizes' must contain only numbers"}), 400
        single_input = False
    else:
        return jsonify({"error": "'sizes' must be a number or a list of numbers"}), 400

    try:
        predictions = model.predict([[s] for s in sizes])
        results = [{"size": s, "predicted_price": float(p)} for s, p in zip(sizes, predictions)]
        return jsonify(results[0] if single_input else results)
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

# Run the app (must be last)
if __name__ == "__main__":
    app.run(port=5001, debug=True)  # set debug=False in production