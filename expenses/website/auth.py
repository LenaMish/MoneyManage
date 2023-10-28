import jwt
from . import app
from datetime import datetime


def get_user_id_from_token(token):
    if not token:
        return None
    token = token.replace("Bearer ", "")
    try:
        data = jwt.decode(jwt=token, key=app.config["SECRET_KEY"], algorithms="HS256")
        date_until = data["exp"] # czas w tokenie przechowywany jest w sekundach liczonych od roku 1970 (tzw timestamp)
        if datetime.now() > datetime.fromtimestamp(date_until): # fromtimestamp zamienia czas w sekundach na normalna date typu datetime
            return None
        return data["id"]
    except Exception as e:
        print(e)
        return None
