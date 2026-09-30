# Task Manager API — Docker + CI/CD to AWS EC2 (Free Tier)

A small FastAPI service used as a vehicle to demonstrate a real, working
CI/CD pipeline: every push to `main` is tested, containerized, pushed to
Docker Hub, and deployed to an AWS EC2 free-tier instance automatically.

## Pipeline

```
git push (main)
      │
      ▼
[GitHub Actions]
      │
      ├─ 1. test    → run the app's test suite
      ├─ 2. build   → build Docker image
      ├─ 3. push    → push image to Docker Hub
      └─ 4. deploy  → SSH into EC2, pull latest image, restart container
                              │
                              ▼
                     Live app on EC2 (port 80)
```

## Tech stack
Python · FastAPI · Docker · GitHub Actions · AWS EC2 (free tier) · Docker Hub

## 1. Run locally first

```bash
docker compose up --build
curl http://localhost:8000/health
```

## 2. Set up the AWS side (free tier)

1. Create an AWS account (free tier, no cost for a `t2.micro`/`t3.micro`
   instance within free-tier limits) at https://aws.amazon.com
2. Go to **EC2 → Launch Instance**:
   - AMI: **Ubuntu Server 22.04 LTS**
   - Instance type: **t2.micro** (free tier eligible)
   - Create/select a key pair — download the `.pem` file, you'll need it
   - Security group: allow inbound **SSH (22)** from your IP, and
     **HTTP (80)** from anywhere (`0.0.0.0/0`)
3. Once running, note the instance's **public IPv4 address**.
4. SSH in and install Docker:
   ```bash
   ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
   curl -fsSL https://get.docker.com | sudo sh
   sudo usermod -aG docker ubuntu
   ```
   Log out and back in for the group change to apply.

## 3. Set up Docker Hub

1. Create a free account at https://hub.docker.com
2. Go to **Account Settings → Security → New Access Token**, generate a
   token (used instead of your password in CI).

## 4. Add GitHub repo secrets

In your GitHub repo: **Settings → Secrets and variables → Actions → New
repository secret**. Add:

| Secret name | Value |
|---|---|
| `DOCKERHUB_USERNAME` | your Docker Hub username |
| `DOCKERHUB_TOKEN` | the access token from step 3 |
| `EC2_HOST` | your EC2 instance's public IP |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | the full contents of your `.pem` file |

## 5. Ship it

```bash
git add .
git commit -m "Set up CI/CD pipeline"
git push origin main
```

Watch it run under the **Actions** tab in GitHub. Once green, your app is
live at `http://<EC2_PUBLIC_IP>/health`.

## Why this design

- **Multi-stage Dockerfile** keeps the final image small (build deps don't
  ship in the runtime image).
- **Test job gates the deploy** — a failing test stops the pipeline before
  anything reaches production.
- **Zero-downtime-ish restart** — pull-then-restart is simple and fine for a
  single-instance demo; a production setup would add a load balancer and
  rolling deploys across multiple instances.

## Possible extensions
- Replace the manual EC2 SSH deploy with **Terraform** to provision the
  instance itself as code, and **Ansible** to configure it (Docker install,
  security hardening) — turns this into a full IaC pipeline.
- Add **Prometheus + Grafana** (or AWS CloudWatch) for monitoring/observability.
- Move from a single EC2 instance to **ECS** or **Kubernetes (EKS)** for
  real orchestration and rolling deploys.
- Add a staging environment and require manual approval before prod deploy.
