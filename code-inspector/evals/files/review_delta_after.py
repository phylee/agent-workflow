import hashlib
import subprocess


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def export_report(name):
    subprocess.run(["cat", "reports/" + name], check=True)
