# 🇬🇧 EngLearn - Full-Stack English Learning Platform

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-092E20?style=flat-square&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

A production-ready web application designed to make learning English interactive and structured. Built with a robust backend architecture, it features grammar modules, a massive vocabulary database, and automated testing to track user progress.

🌍 **Live Application:** [best-devs.studio](https://best-devs.studio)

---

## 🌟 Key Features

* **Smart Vocabulary Management:** A curated dictionary of over 4,000+ words parsed and seeded into the database via custom Django management scripts, complete with conflict-resolution logic.
* **Interactive Testing System:** Automated quiz modules with instant validation and progression tracking.
* **Structured Grammar Paths:** Categorized learning modules adapted for different English proficiency levels (A1 to C2).
* **Production-Grade Architecture:** Fully containerized environment using Docker, protected by an Nginx reverse proxy and automated Let's Encrypt SSL certificates.
* **Seamless Deployment:** Integrated CI/CD pipeline using GitHub Actions for zero-downtime automated deployments to an Azure Ubuntu server.

---

## 🛠 Tech Stack

### Backend & Core
* **Python 3.13** & **Django 5.x**
* **Django REST Framework (DRF)**
* **PostgreSQL** (Primary Relational Database)

### Infrastructure & DevOps
* **Docker & Docker Compose** (Containerization & Orchestration)
* **Nginx** (Web Server & Reverse Proxy)
* **GitHub Actions** (Continuous Integration & Deployment)
* **Microsoft Azure** (Cloud Hosting - Ubuntu 24.04 LTS)

### Frontend
* **Django Templates** (Server-side rendering)
* **HTML5, CSS3, JavaScript** (Interactivity & asynchronous data loading)

---

## 🚀 Local Development Setup

To run this project locally on your machine, ensure you have **Docker** and **Git** installed.

**1. Clone the repository:**

git clone [https://github.com/oleksandrivancenko17/eng_site.git](https://github.com/oleksandrivancenko17/eng_site.git)
cd eng_site

2. Setup environment variables:
Rename the provided example file to .env and fill in your local credentials.

Bash
cp .env.example .env
3. Build and launch the containers:

Bash
docker compose up -d --build
4. Run database migrations & collect static files:

Bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
5. Create a superuser (Admin access):

Bash
docker compose exec web python manage.py createsuperuser
6. Access the application:

Main website: http://localhost:8000

Admin panel: http://localhost:8000/admin

🔄 CI/CD Pipeline
This project implements a continuous deployment workflow. Every push to the main branch triggers a GitHub Actions job that securely connects to the Azure production server via SSH, pulls the latest code, rebuilds the Docker containers, applies database migrations, and collects static files automatically.

👨‍💻 Author
Oleksandr Ivanchenko
Backend Developer | Information Technology Student at Cherkasy State Technological University

📍 Cherkasy, Ukraine

💼 Portfolio / Other Projects: medwedivka.me

🐙 GitHub: @oleksandrivancenko17

If you find this project interesting or helpful, feel free to give it a ⭐!
