from flask import Flask
from models import db
from main_routes import main
from todo_routes import todo
from lit_routes import lit

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

app.register_blueprint(main)
app.register_blueprint(todo)
app.register_blueprint(lit)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
