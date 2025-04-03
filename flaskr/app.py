from flask import render_template

from flaskr.config import app
from flaskr.views import auth_bp

app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
