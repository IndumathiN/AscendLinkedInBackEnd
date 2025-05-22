from flask import Flask
from flask_cors import CORS
from routes.bot_routes import bot_bp
from routes.resume_routes import resume_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(bot_bp)
app.register_blueprint(resume_bp)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
