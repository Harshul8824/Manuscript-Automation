# 📄 ManuscriptMagic
### AI-Driven Manuscript Formatting Automation

> Transform raw research drafts into publication-ready documents in minutes — powered by Claude AI, Python, and React.

---

## 📑 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution Architecture](#solution-architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Processing Pipeline](#processing-pipeline)
- [Directory Structure](#directory-structure)
- [Local Development Setup](#local-development-setup)
- [AWS Deployment Guide](#aws-deployment-guide)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Template System](#template-system)
- [Cost Analysis](#cost-analysis)
- [Team](#team)

---

## Overview

ManuscriptMagic is an AI-powered web application that automates the formatting of academic manuscripts. Researchers upload a raw `.docx` file, select a target journal template (e.g., IEEE), and receive a fully formatted, publication-ready document — without manual intervention.

**MVP Scope:** Research papers and conference papers up to 30 pages / 5MB, formatted to IEEE standard.

---

## Problem Statement

Academic researchers and publishing houses face a recurring bottleneck:

| Pain Point | Impact |
|---|---|
| Manual formatting per journal | 3–8 hours per paper |
| Inconsistency across submissions | High revision cycle rate |
| Staff overhead at publishing houses | High operational cost |
| Author unfamiliarity with style guides | Submission rejection delays |

ManuscriptMagic eliminates this bottleneck by automating the entire formatting pipeline using AI-driven document understanding.

---

## Solution Architecture

```
User (Browser)
      │
      │  Upload DOCX
      ▼
┌─────────────┐        ┌──────────────────────────────────────────┐
│  React App  │◄──────►│              Flask Backend               │
│  (Frontend) │  REST  │                                          │
└─────────────┘  API   │  ┌──────────┐      ┌─────────────────┐  │
                        │  │  Parser  │─────►│   Classifier    │  │
                        │  │          │      │  (Claude API)   │  │
                        │  └──────────┘      └────────┬────────┘  │
                        │                             │           │
                        │  ┌──────────┐      ┌────────▼────────┐  │
                        │  │Formatter │◄─────│     Mapper      │  │
                        │  │          │      │                 │  │
                        │  └────┬─────┘      └─────────────────┘  │
                        │       │                                  │
                        │  ┌────▼─────┐      ┌─────────────────┐  │
                        │  │Reference │      │  ieee.json      │  │
                        │  │ Parser   │      │  (Template)     │  │
                        │  └──────────┘      └─────────────────┘  │
                        └──────────────────────────────────────────┘
                                          │
                                   Formatted DOCX
                                          │
                                    User Downloads
```

---

## Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| React (Vite) | UI framework |
| Axios | HTTP client for Flask API calls |
| React Router | Page navigation (Upload → Progress → Download) |
| Tailwind CSS | Styling |

### Backend
| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Flask | REST API server |
| Gunicorn | WSGI production server |
| python-docx | DOCX parsing and generation |
| Anthropic Claude API | AI section classification |
| python-dotenv | Environment variable management |
| flask-cors | Cross-origin request handling |

### Infrastructure (AWS)
| Service | Purpose |
|---|---|
| EC2 t2.micro | Hosts Flask backend + Nginx |
| S3 | Hosts React static build (optional) |
| Nginx | Reverse proxy + static file server |

---

## Features

### MVP (Implemented)
- Upload `.docx` manuscript via drag-and-drop
- AI-powered section classification (Abstract, Introduction, Methodology, Results, Conclusion, References)
- Title and author extraction
- IEEE template application (fonts, margins, heading hierarchy, 2-column layout)
- Reference reformatting to IEEE citation style
- Download formatted `.docx` output
- Animated progress window with processing stages

### Planned (Post-MVP)
- Multiple template support (APA, Springer, Elsevier)
- Table and figure detection with auto-captioning
- PDF export
- Before/after document comparison view
- Batch processing

---

## Processing Pipeline

```
Raw DOCX Uploaded
        │
        ▼
  1. PARSER (parser.py)
     - Extracts all paragraphs, tables, images
     - Reads font sizes, styles, alignment
     - Returns structured raw_content dict
        │
        ▼
  2. CLASSIFIER (classifier.py)
     - Sends paragraphs to Claude API
     - Identifies: title, authors, abstract,
       section headings, body, references
     - Hybrid: rule-based first, AI for ambiguous cases
        │
        ▼
  3. MAPPER (mapper.py)
     - Maps classified paragraphs to
       structured document sections
     - Builds ordered content schema
        │
        ▼
  4. REFERENCE PARSER (reference_parser.py)
     - Detects citation style of input
     - Converts all references to IEEE format
     - Returns formatted reference strings
        │
        ▼
  5. FORMATTER (formatter.py)
     - Loads ieee.json template config
     - Creates new DOCX from scratch
     - Applies all visual formatting rules
     - Inserts structured content with proper styling
        │
        ▼
  Formatted DOCX → Saved to /tmp/ → Sent to user → Deleted
```

---

## Directory Structure

```
manuscript-magic/
│
├── .gitignore
├── README.md
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx
│   │   │   ├── AnalysisPage.jsx
│   │   │   ├── TemplateSelectPage.jsx
│   │   │   └── DownloadPage.jsx
│   │   ├── components/
│   │   │   ├── UploadBox.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   ├── TemplateCard.jsx
│   │   │   └── Navbar.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── utils/
│   │       └── progressSimulator.js
│   ├── .env
│   ├── package.json
│   └── vite.config.js
│
└── backend/
    ├── app.py
    ├── config.py
    ├── wsgi.py
    ├── routes/
    │   └── document_routes.py
    ├── services/
    │   ├── parser.py
    │   ├── classifier.py
    │   ├── mapper.py
    │   ├── formatter.py
    │   └── reference_parser.py
    ├── templates/
    │   └── ieee.json
    ├── tmp/
    │   └── .gitkeep
    ├── tests/
    │   ├── test_parser.py
    │   ├── test_classifier.py
    │   └── test_formatter.py
    ├── .env
    └── requirements.txt
```

---

## Local Development Setup

### Prerequisites

- Node.js v18+
- Python 3.10+
- pip
- An Anthropic API key ([get one here](https://console.anthropic.com))

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/manuscript-magic.git
cd manuscript-magic
```

---

### 2. Backend Setup (Flask)

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Then open .env and add your ANTHROPIC_API_KEY
```

**Start Flask development server:**

```bash
flask run --port=5000
```

Flask will be running at `http://localhost:5000`

---

### 3. Frontend Setup (React)

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# REACT_APP_API_URL=http://localhost:5000 is already set
```

**Start React development server:**

```bash
npm run dev
```

React will be running at `http://localhost:5173`

---

### 4. Verify Setup

Open `http://localhost:5173` in your browser. Upload any `.docx` research paper file. If the progress screen appears and a formatted file is returned, your local setup is complete.

---

## AWS Deployment Guide

### Prerequisites

- AWS account with $100 credit
- EC2 `t2.micro` instance running Ubuntu 22.04
- SSH access to your instance
- Your repository pushed to GitHub

---

### Step 1: Connect to EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

---

### Step 2: Install System Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx nodejs npm git
```

---

### Step 3: Clone Repository and Setup Backend

```bash
cd /home/ubuntu
git clone https://github.com/your-username/manuscript-magic.git
cd manuscript-magic/backend

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
sudo nano .env
# Add: ANTHROPIC_API_KEY=sk-ant-your-key-here
# Add: FLASK_ENV=production
```

---

### Step 4: Build React Frontend

```bash
cd /home/ubuntu/manuscript-magic/frontend
npm install
npm run build
# Output goes to frontend/dist/
```

---

### Step 5: Configure Gunicorn as System Service

```bash
sudo nano /etc/systemd/system/flask.service
```

Paste the following:

```ini
[Unit]
Description=ManuscriptMagic Flask Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/manuscript-magic/backend
Environment="PATH=/home/ubuntu/manuscript-magic/backend/venv/bin"
EnvironmentFile=/home/ubuntu/manuscript-magic/backend/.env
ExecStart=/home/ubuntu/manuscript-magic/backend/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable flask
sudo systemctl start flask
sudo systemctl status flask    # Should show: active (running)
```

---

### Step 6: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/manuscript-magic
```

Paste the following:

```nginx
server {
    listen 80;
    server_name your-ec2-public-ip;

    # Serve React static build
    location / {
        root /home/ubuntu/manuscript-magic/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API calls to Flask
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        client_max_body_size 10M;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/manuscript-magic /etc/nginx/sites-enabled/
sudo nginx -t                  # Test config — should say "ok"
sudo systemctl restart nginx
```

---

### Step 7: Open EC2 Security Group Ports

In AWS Console → EC2 → Security Groups → Inbound Rules, add:

| Type | Port | Source |
|---|---|---|
| HTTP | 80 | 0.0.0.0/0 |
| HTTPS | 443 | 0.0.0.0/0 |
| SSH | 22 | Your IP only |

---

### Step 8: Verify Deployment

Open `http://your-ec2-public-ip` in your browser. The ManuscriptMagic upload page should load. Test with a sample DOCX file to confirm full pipeline works end-to-end.

---

## Environment Variables

### Backend (`backend/.env`)

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
FLASK_ENV=development
FLASK_PORT=5000
MAX_FILE_SIZE_MB=5
TMP_DIR=./tmp
```

### Frontend (`frontend/.env`)

```env
# Local development
REACT_APP_API_URL=http://localhost:5000

# AWS production — leave empty, Nginx proxies /api/* to Flask
REACT_APP_API_URL=
```

> **Security Rule:** Never commit `.env` files to Git. Both are listed in `.gitignore`.

---

## API Reference

### `POST /api/upload`

Upload a DOCX file for processing.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | `.docx` | Yes | Raw manuscript file (max 5MB) |
| `template` | string | Yes | Template name: `"ieee"` |

**Response:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716",
  "status": "processing",
  "message": "Document received and queued"
}
```

---

### `GET /api/download/<job_id>`

Download the formatted DOCX file.

**Response:** `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

The file is streamed directly. Temp files are deleted from server after download.

---

### `GET /api/health`

Health check endpoint.

**Response:**

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## Template System

Templates are stored as JSON configuration files in `backend/templates/`. Each file defines all formatting rules for a specific journal standard. The `TemplateFormatter` class reads this config at runtime — no code changes are needed to add new templates.

**Current Templates:**

| File | Standard | Status |
|---|---|---|
| `ieee.json` | IEEE Transactions & Conferences | ✅ MVP |
| `apa.json` | APA 7th Edition | 🔜 Planned |
| `springer.json` | Springer LNCS | 🔜 Planned |

**Template config covers:** page size, margins, column layout, font family and size per section type, heading numbering style, reference citation format, table and figure caption rules.

---

## Cost Analysis

### Anthropic API (Per Document)

| Document Size | Claude API Tokens | Estimated Cost |
|---|---|---|
| Short paper (6–8 pages) | ~3,000 tokens | ~$0.003 |
| Standard paper (10–15 pages) | ~6,000 tokens | ~$0.006 |
| Long paper (25–30 pages) | ~12,000 tokens | ~$0.012 |

Using `claude-haiku` model for classification (fastest, cheapest tier).

### AWS Infrastructure (Monthly)

| Service | Cost |
|---|---|
| EC2 t2.micro | ~$8.50/mo |
| S3 storage (minimal) | ~$0.50/mo |
| Data transfer | ~$1.50/mo |
| **Total** | **~$10.50/mo** |

**$100 AWS credit covers approximately 9 months of hosting.**

### Approach Comparison

| Approach | Setup Cost | Per-Doc Cost | Accuracy | Feasibility |
|---|---|---|---|---|
| Claude API (current) | $0 | ~$0.006 | 92–95% | ✅ High |
| Rule-based only | $0 | $0.00 | 70–80% | ✅ High |
| Hybrid (rule + API) | $0 | ~$0.003 | 90–94% | ✅ High |
| Fine-tuned BERT | $100–200 GPU | $0 | 88–92% | ⚠️ Medium |
| Train from scratch | $500–2000+ | $0 | Unpredictable | ❌ Low |

---

## Team

| Name | Role |
|---|---|
| [Your Name] | Full Stack + AI Pipeline |
| [Team Member] | Frontend / UX |
| [Team Member] | Backend / DevOps |

---

## License

This project was built for a hackathon. All rights reserved by the team.

---

<p align="center">Built with ❤️ for researchers who deserve better tools</p>