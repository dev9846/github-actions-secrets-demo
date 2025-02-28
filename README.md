Here’s a well-structured **README.md** for your public repository that explains various methods for passing secrets securely in a Python app using Docker and GitHub Actions.  

---

# **Secure Secrets Management in Docker & GitHub Actions**

This repository demonstrates multiple methods for securely passing secrets in a **Flask-based Python application** running inside a **Docker container**. It also includes **GitHub Actions workflows** to automate the **build, push, and deployment** process to an **EC2 instance**.

## **📌 Features**
✅ Securely read secrets using multiple methods  
✅ Run the Flask app inside a Docker container  
✅ Expose a **/health** API for checking deployment status  
✅ Automate deployment using **GitHub Actions**  
✅ Push Docker images to **Docker Hub**  
✅ Deploy the container to an **Amazon EC2 instance**  

---

## **📂 Project Structure**
```plaintext
.
├── python_app/
│   ├── app.py                 # Main Flask application
│   ├── Dockerfile             # Docker build configuration
│   ├── requirements.txt       # Python dependencies
│   ├── utils.py               # Utility functions for secrets handling
│   ├── config.py              # Configuration based on SECRET_METHOD
│   ├── README.md              # Documentation
├── .github/
│   ├── workflows/
│   │   ├── build-and-push.yml  # Builds & pushes the Docker image
│   │   ├── deploy-to-ec2.yml   # Deploys the container to EC2
│   ├── secrets-demo/           # (Optional) Demo secrets storage
├── .env.example                # Example environment file
```

---

## **🔐 Secrets Handling Methods**
Our application supports multiple methods to securely **retrieve secrets**. You can choose one by setting the **SECRET_METHOD** environment variable.

### **1️⃣ Environment Variables (Recommended)**
- Secrets are stored as **environment variables** in the container or server.
- Set them before running the app:
  ```sh
  export DB_PASSWORD="my_secure_password"
  ```

### **2️⃣ Docker Secrets**
- Secrets are securely stored in a **Docker secret file** (`/run/secrets/db_password`).
- Create a Docker secret:
  ```sh
  echo "my_secure_password" > db_password.txt
  docker secret create db_password db_password.txt
  ```
- Modify the `docker-compose.yml` to use secrets.

### **3️⃣ AWS Secrets Manager**
- Fetch secrets from **AWS Secrets Manager** dynamically.
- Set up AWS credentials and install `boto3`:
  ```sh
  pip install boto3
  ```
- Retrieve secrets programmatically:
  ```python
  import boto3
  secret_name = "my-db-password"
  client = boto3.client('secretsmanager', region_name='us-east-1')
  secret_value = client.get_secret_value(SecretId=secret_name)["SecretString"]
  ```

### **4️⃣ HashiCorp Vault**
- Fetch secrets dynamically from **Vault**.
- Install Vault CLI and authenticate:
  ```sh
  export VAULT_ADDR="http://vault-server:8200"
  export VAULT_TOKEN="my-vault-token"
  ```
- Retrieve secrets using API:
  ```sh
  vault kv get secret/db_password
  ```

### **5️⃣ GitHub Actions Secrets**
- Store secrets in **GitHub Actions → Repository Secrets**.
- Use them in workflows:
  ```yaml
  env:
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
  ```

---

## **🚀 Running the App**
### **1️⃣ Run Locally**
```sh
export SECRET_METHOD="env"
export DB_PASSWORD="my_secure_password"
python python_app/app.py
```

### **2️⃣ Run with Docker**
```sh
docker build -t my-flask-app .
docker run -d -p 80:8080 -e SECRET_METHOD="env" -e DB_PASSWORD="my_secure_password" my-flask-app
```

---

## **⚡ GitHub Actions Workflows**
### **1️⃣ Build & Push Docker Image**
This workflow automates the build and push process to **Docker Hub**.

```yaml
name: Build & Push Docker Image
on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Docker
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build & Push Docker Image
        uses: docker/build-push-action@v5
        with:
          context: ./python_app
          file: ./python_app/Dockerfile
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/my-flask-app:latest
```

---

### **2️⃣ Deploy to EC2**
This workflow connects to an **EC2 instance** via SSH and updates the running container.

```yaml
name: Deploy to EC2
on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Connect to EC2 & Deploy
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            docker stop my-flask-container || true
            docker rm my-flask-container || true
            docker pull ${{ secrets.DOCKER_USERNAME }}/my-flask-app:latest
            docker run -d -p 80:8080 --name my-flask-container \
              -e SECRET_METHOD="env" -e DB_PASSWORD="${{ secrets.DB_PASSWORD }}" \
              ${{ secrets.DOCKER_USERNAME }}/my-flask-app:latest
```

---

## **🎯 Contributing**
Feel free to contribute by submitting **issues**, **pull requests**, or suggestions.

---

## **📜 License**
This project is open-source and available under the **MIT License**.

---

Let me know if you need any modifications! 🚀