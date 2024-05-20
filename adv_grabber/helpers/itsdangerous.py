from itsdangerous import URLSafeTimedSerializer, BadTimeSignature, SignatureExpired
from config import settings


token_algo = URLSafeTimedSerializer(settings.itsdangerous_secret_key,
                                    salt=settings.itsdangerous_salt)


def create_safe_token(unsafe_string: str):
    _token = token_algo.dumps(unsafe_string)
    return _token


def get_from_token(token: str):
    try:
        safe_token = token_algo.loads(token, max_age=settings.itsdangerous_token_time)
    except SignatureExpired:
        print('SignatureExpired')
        return None
    except BadTimeSignature:
        print('BadTimeSignature')
        return None
    return safe_token
