from flask import Flask, jsonify
import os
import boto3
import hvac

app = Flask(__name__)

def get_db_password():
    """
    Fetch DB password based on SECRET_METHOD.
    """
    secret_method = os.getenv("SECRET_METHOD", "env")

    if secret_method == "env":
        return os.getenv("DB_PASSWORD", "No password set")

    elif secret_method == "docker":
        return read_from_file("/run/secrets/db_password")

    elif secret_method == "k8s":
        return read_from_file("/etc/secrets/db_password")

    elif secret_method == "aws":
        return fetch_from_aws_secrets_manager(os.getenv("AWS_SECRET_NAME", "db-password"))

    elif secret_method == "vault":
        return fetch_from_vault()

    else:
        return "Invalid SECRET_METHOD"

def read_from_file(filepath):
    """ Reads secret from a file (Docker/K8s methods) """
    try:
        with open(filepath, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Secret file not found"

def fetch_from_aws_secrets_manager(secret_name):
    """ Fetch secret from AWS Secrets Manager """
    try:
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager")
        response = client.get_secret_value(SecretId=secret_name)
        return response["SecretString"]
    except Exception as e:
        return f"AWS Secret Error: {e}"

def fetch_from_vault():
    """ Fetch secret from HashiCorp Vault """
    try:
        vault_addr = os.getenv("VAULT_ADDR")
        vault_token = os.getenv("VAULT_TOKEN")
        vault_client = hvac.Client(url=vault_addr, token=vault_token)
        secret = vault_client.secrets.kv.v2.read_secret_version(path="db-password")
        return secret["data"]["data"]["password"]
    except Exception as e:
        return f"Vault Secret Error: {e}"

# Securely log masked password
db_password = get_db_password()
masked_password = db_password[:2] + "*" * (len(db_password) - 2)
app.logger.info(f"DB Password (Masked): {masked_password}")

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/test-secret")
def test_secret():
    return jsonify({"message": f"DB Password is {masked_password}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
