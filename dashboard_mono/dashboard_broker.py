from flask import Flask
from dashboard_mono.core.routes import dashboard_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)

if __name__ == "__main__":
    print("🚀 Avvio dashboard web su http://127.0.0.1:5000")
    app.run(debug=True)