from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from psycopg2.errorcodes import UNIQUE_VIOLATION
from werkzeug.exceptions import InternalServerError, BadRequest

from config import DevApplication
from db import db
from resources.routes import routes

app = Flask(__name__)
app.config.from_object(DevApplication)
db.init_app(app)

migrate = Migrate(app, db)
api = Api(app)

[api.add_resource(*r) for r in routes]


@app.after_request
def conclude_request(resp):
    try:
        db.session.commit()
    except Exception as err:
        if err.orig.pgcode == UNIQUE_VIOLATION:
            raise BadRequest("please login")
        else:
            raise InternalServerError("Server Is unavailable. Please try again later")
    return resp


if __name__ == "__main__":
    app.run()
