from flask import Flask, render_template, request, jsonify
from agents.inventory_agent import run_inventory_agent
from config import DB_PATH, BASE_DIR

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    if user_input:
        result = run_inventory_agent(user_input)
        return jsonify({"output": result})
    return jsonify({"output": "No input received."})

if __name__ == "__main__":
    app.run(debug=True)

