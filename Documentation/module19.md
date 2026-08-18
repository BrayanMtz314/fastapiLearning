# Module 19: Deploy with Docker - Serverless Containers and Custom Domain

In this final module, we explore a modern deployment approach by containerizing our application with Docker and deploying it to a serverless cloud service (Google Cloud Run).

## 1. Health Checks & Security Headers
Before deploying, we need to ensure our application is production-ready.

* **Health Check Endpoint:** We added a simple `/health` endpoint. Cloud providers use this to constantly ping our container; if it returns a 200 OK, the cloud knows the container is alive and healthy.
* **Security Headers Middleware:** In a traditional VPS setup (like Module 18), Nginx handles adding security headers to all responses. Because Google Cloud Run does not have Nginx sitting in front of our app in the same way, we must manually inject these headers using a FastAPI middleware to tell browsers our site is secure.

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    if "Referrer-Policy" not in response.headers:
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.hostname not in ("localhost", "127.0.0.1"):
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains"
        )
    return response
```

## 2. Containerizing with Docker
Docker packages our application and all its dependencies into a single, standardized unit.

* **Dockerfile:** A recipe that tells Docker how to build your environment.

* **Image:** The built, read-only result of that recipe.

* **Container:** A live, running instance of an image.

* **Multi-stage Build:** Our Dockerfile uses two stages. A "builder" stage installs all dependencies, and a "production" stage copies only the necessary compiled files. This keeps our final image small and secure.

* **.dockerignore:** Just like .gitignore, this prevents sensitive files (like .env or local databases) from being copied into the container image.

## 3. Serverless Databases (Neon.tech)
Containers on Cloud Run are **stateless**. If the container spins down, any local files (like our SQLite database) are permanently lost. To solve this, we use a managed PostgreSQL service called Neon.

We configure two database URLs in our `.env` file:

1. **Direct Connection:** Used strictly for Alembic migrations.

2. **Pooled Connection:** Used by the FastAPI application at runtime. Connection pooling manages multiple simultaneous database requests efficiently, preventing the database from being overwhelmed when Cloud Run scales up multiple containers.

## 4. Local Docker Testing
Before pushing to the cloud, we test the image on our own machine:
```bash
# Build the image and tag it as 'fastapi-app'
docker build -t fastapi-app .

# Run the container, injecting our .env variables, and mapping port 8080
docker run -p 8080:8080 --env-file .env fastapi-app
```

## 5. Google Cloud Setup & Artifact Registry
We created a Google Cloud project named FastAPI-Blog and installed the Google Cloud CLI. We then enabled the necessary cloud APIs:
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Enable Artifact Registry API
gcloud services enable artifactregistry.googleapis.com
```
**What this does:** Artifact Registry is Google Cloud's next-generation container registry. It acts as a secure, private cloud folder specifically designed to store and manage your built Docker images.

* **Create the Repository:**
```bash
gcloud artifacts repositories create fastapi-repo --repository-format=docker --location=us-east4
```
**What this does:** This creates the specific Docker repository named fastapi-repo inside the Artifact Registry located in the US-East server region.

## 6. Building and Deploying to Cloud Run
With our registry ready, we send our code to Google to be built and hosted.

* **Submit the Build:**
```bash
gcloud builds submit --tag us-east4-docker.pkg.dev/YOUR_PROJECT_ID/fastapi-repo/fastapi-app
```
Google takes our source code and Dockerfile, builds the image on their servers, and saves it in the Artifact Registry.

* **Deploy the Service:**
```bash
gcloud run deploy fastapi-service \
    --image us-east4-docker.pkg.dev/YOUR_PROJECT_ID/fastapi-repo/fastapi-app \
    --region us-east4 \
    --allow-unauthenticated
```

### Fixing the Port Timeout Error
Upon first deployment, you will likely get a timeout error (`The user-provided container failed to start...`). This is expected! Our container crashed because it lacks the necessary environment variables (Database URL, S3 Keys, etc.) to start up.

* **The Fix:** Go to the Google Cloud Run Console, click "Edit & Deploy New Revision", and navigate to the "Variables & Secrets" tab. Input all your `.env` variables here (making sure to use the newly generated Cloud Run URL for the `FRONTEND_URL`), and redeploy.

## 7. Custom Domain Mapping
***Note: In complex production environments, traffic is usually routed through a Load Balancer, Firebase Hosting, or Cloudflare. For simplicity, we mapped the domain directly to Cloud Run.***

1. Verify your domain ownership via the Google Search Console.

2. Generate the DNS records using the CLI:
```bash
gcloud beta run domain-mappings create --service=fastapi-service --domain=<Your domain name> --region=us-east4
```
3. Copy the provided A/AAAA/CNAME records into your domain provider's DNS settings.

4. Verify the SSL certificates:
```bash
gcloud beta run domain-mappings describe --domain=<Your domain> --region=us-east4
```
If you get here and the verification return true, Congratulation! you have a web application in your domain name right now.

## 8. Updating the Application
Whenever you make changes to your code, deploying the update is incredibly simple. You can use this combined command to build and deploy simultaneously:
```bash
gcloud run deploy fastapi-service --source . --region us-east4
```
If a Dockerfile exists in the current directory, Google automatically builds the image and deploys the new revision without downtime.

## Conclusion: Manual VPS vs. Managed Serverless Cloud
Deploying an application can generally take two paths:

1. **Manual VPS Deployment (e.g., DigitalOcean Droplet, AWS EC2, Linode)**
When using a Virtual Private Server, you are renting a raw Linux computer. You are completely responsible for updating the operating system, configuring the firewall, installing Python, managing SSL certificates (Certbot), configuring Nginx as a reverse proxy, and keeping the server running using tools like systemd or supervisor. If your app suddenly gets a million users, the server will crash unless you manually upgrade its hardware. It is cheaper, but requires heavy system administration work.

2. **Managed Serverless Containers (e.g., Google Cloud Run, AWS App Runner)**
With Serverless platforms, all underlying infrastructure is abstracted away. You don't care about Linux updates, Nginx, or SSL certificates—Google handles all of that automatically. You simply hand Google a Docker container and say, "Run this."
The biggest advantage is Auto-scaling: if no one is visiting your site, Cloud Run scales down to zero (costing you nothing). If your app goes viral, Cloud Run automatically duplicates your container hundreds of times to handle the traffic, then scales back down when it's over. It allows developers to focus 100% on writing code rather than managing servers.

# Return to Readme.md
[**Readme.md**](../README.md)

