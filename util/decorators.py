from flask import request
from werkzeug.exceptions import BadRequest, Forbidden

from managers.auth import auth


def validate_schema(schema_name):
    def wrapper(func):
        def decorated_func(*args, **kwargs):
            data = request.get_json()
            schema = schema_name()
            errors = schema.validate(data)
            if errors:
                raise BadRequest(errors)
            return func(*args, **kwargs)

        return decorated_func

    return wrapper


def permission_required(permission):
    def wrapper(func):
        def decorated_func(*args, **kwargs):
            user = auth.current_user()
            if not permission == user.role:
                raise Forbidden("You do not have rights to access to use this resource")
            return func(*args, **kwargs)

        return decorated_func

    return wrapper
