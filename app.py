from flask import Flask
from models import db

from routes_main import main
from routes_todo import todo
from routes_lit import lit
from routes_scheduler import scheduler

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

app.register_blueprint(main)
app.register_blueprint(todo)
app.register_blueprint(lit)
app.register_blueprint(scheduler)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
