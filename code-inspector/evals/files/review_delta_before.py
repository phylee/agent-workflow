import hashlib
import os

SECRET_KEY = "prod-secret"


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def export_report(name):
    os.system("cat reports/" + name)
