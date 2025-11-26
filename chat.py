from flask import Flask, request, render_template_string
from agents.inventory_agent import run_inventory_agent

app = Flask(__name__)

HTML = """
<html lang="en">
  <head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body style="background:url('https://cdn.ionnova.com/img/lessons/agentic_ai/grocry_store.png') no-repeat center top; background-size:cover;">
    <div class="container-fluid">
      <div class="card position-fixed bottom-0 end-0 m-3 shadow" style="width: 22rem;">
        <div class="card-header bg-primary text-white">
          Inventory Agent
        </div>
        <div class="card-body">
          {% if answer %}
            <p><strong>Agent:</strong> {{ answer }}</p>
          {% else %}
            <p>Ask me about inventory, suppliers, or thresholds.</p>
          {% endif %}
        </div>
        <div class="card-footer">
          <form method="post" class="d-flex">
            <input type="text" name="user_input" class="form-control me-2" placeholder="Type your message">
            <button type="submit" class="btn btn-primary">Send</button>
          </form>
        </div>
      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def chat():
    answer = None
    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        if user_input:
            answer = run_inventory_agent(user_input)
    return render_template_string(HTML, answer=answer)

if __name__ == "__main__":
    app.run(debug=True)

 