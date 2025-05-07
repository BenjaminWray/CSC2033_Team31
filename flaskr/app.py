from flaskr.config import app
from flaskr.views import auth_bp

app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")