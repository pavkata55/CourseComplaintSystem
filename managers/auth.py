from datetime import datetime, timedelta

import jwt
from decouple import config
from flask_httpauth import HTTPTokenAuth
from werkzeug.exceptions import BadRequest

from models import ComplainerModel, ApproverModel


class AuthManager:
    pass

    @staticmethod
    def encode_token(user):
        payload = {
            "sub": user.id,
            "exp": datetime.utcnow() + timedelta(days=int(config("JWT_TIME"))),
            "role": user.role.value,
        }
        return jwt.encode(payload, key=config("JWT_KEY"), algorithm="HS256")

    @staticmethod
    def decode_token(token):
        try:
            data = jwt.decode(token, key=config("JWT_KEY"), algorithms=["HS256"])
            return data
        except jwt.ExpiredSignatureError:
            raise BadRequest("Token Expired")
        except jwt.InvalidTokenError:
            raise BadRequest("Invialid Token")


auth = HTTPTokenAuth(scheme="Bearer")


@auth.verify_token
def verify_token(token):
    model = {
        "approver": ApproverModel,
        "complainer": ComplainerModel,
        # 'admin' : TODO
    }
    token_decoded = AuthManager.decode_token(token)
    user = model[token_decoded["role"]].query.filter_by(id=token_decoded["sub"]).first()
    return user
