# EatguAI — AI Fridge Assistant

> Snap a photo of your fridge. Get ranked recipes in seconds.

EatguAI combines **computer vision** and a **NLP-based recommendation engine** to detect ingredients from a fridge photo and suggest the best matching recipes — deployed as a production web app orginally launched via Cloud Run in GCP using Vertex AI and Gemini 2.0 flash. Due to billing costs it migrated to Hugging Face Spaces using Anthropic key.
>
For the Demo go to the link:
> 
🔗 **[Live Demo](https://huggingface.co/spaces/catoralonso/eatguai)**

### General
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/Interface-Gradio-FF7C00?logo=gradio&logoColor=white)
![Pydantic](https://img.shields.io/badge/Validation-Pydantic_v2-E92063?logo=pydantic&logoColor=white)

### Current Stack (Anthropic + HF)
![Claude](https://img.shields.io/badge/Claude_Sonnet-Anthropic-D97757?logo=anthropic&logoColor=white)
![HuggingFace](https://img.shields.io/badge/Deployed-HuggingFace_Spaces-FFD21E?logo=huggingface&logoColor=black)

### Original Infrastructure (GCP)
![Vertex AI](https://img.shields.io/badge/Vertex_AI-Google_Cloud-4285F4?logo=googlecloud&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.0_Flash-Google_AI-4285F4?logo=google&logoColor=white)
![Cloud Run](https://img.shields.io/badge/Cloud_Run-Serverless-34A853?logo=googlecloud&logoColor=white)
![Terraform](https://img.shields.io/badge/Infra-Terraform-7B42BC?logo=terraform&logoColor=white)

---

## What makes it interesting

**The problem:** Traditional recipe apps require you to type ingredients manually. That's friction nobody wants.

**The solution:** Upload one photo → Claude Vision identifies every ingredient → a TF-IDF recommender ranks 300 recipes by match score → you get step-by-step instructions in under 5 seconds.

**Key architectural decision:** Instead of training a custom YOLO model (explored and discarded due to dataset constraints and overfitting), we pivoted to zero-shot inference via a vision API. This eliminated the need for a labeled dataset, removed GPU dependency, and made the system generalizable to any real-world fridge photo.

---

## Infrastructure Evolution

This project went through a deliberate infrastructure migration that reflects real-world engineering trade-offs.

**Phase 1 — Google Cloud Platform**
The original stack was built on GCP: Vertex AI for Gemini inference, Cloud Run for serverless deployment, Artifact Registry for Docker images, and Terraform for infrastructure-as-code. This was a fully production-grade setup with automated provisioning.

The migration away from GCP was driven by two factors: **model deprecation** (Gemini 2.0 Flash 001 was discontinued for new users without notice) and **SDK instability** (the Python SDK was renamed from `google-generativeai` to `google-genai` mid-development, requiring a full migration). Neither issue was about cost — they were about reliability.

**Phase 2 — Anthropic + Hugging Face Spaces**
Claude Sonnet replaced Gemini for both vision detection and the ingredient substitution engine. Hugging Face Spaces replaced Cloud Run as the deployment target. The core ML logic — TF-IDF vectorizer, cosine similarity scoring, Pydantic models — remained unchanged. The Terraform infrastructure and Docker pipeline are preserved in the repo as documentation of the original architecture.

---

## System Architecture

```
Photo → [Claude Sonnet Vision] → ingredient list
                                        ↓
                          [Substitution Engine — Claude]
                          expands available set with culinary
                          substitutes via single API call
                                        ↓
                         [TF-IDF + Cosine Similarity]
                                        ↓
                         ranked recipes with match score
                                        ↓
                               [Gradio UI / HF Spaces]
```

---

## Tech Stack

| Layer | Current (Anthropic + HF) | Original (GCP) |
|-------|--------------------------|----------------|
| Vision | Claude Sonnet | Gemini 2.0 Flash via Vertex AI |
| Substitution | Claude Sonnet | Hardcoded dictionary |
| Recommendation | TF-IDF + Cosine Similarity (scikit-learn) | Same |
| Scoring | Weighted ingredient matching + difficulty bonus per mode | Same |
| Validation | Pydantic v2 | Same |
| Interface | Gradio | Same |
| Deployment | Hugging Face Spaces | Docker → Artifact Registry → Cloud Run |
| Infra-as-code | — | Terraform |

---

## Two Operating Modes

| Mode | Philosophy | Max missing ingredients |
|------|-----------|------------------------|
| 🧊 **Survival** | Cook strictly with what you have | 2 |
| 👨‍🍳 **Chef Pro** | Full gastronomic experience — techniques, pairings, plating | 5 |

Each mode has independent scoring weights, a distinct UI theme, and different recipe fields exposed.

---

## Dataset

300 Spanish recipes with structured fields: key ingredients (with quantities), base ingredients, step-by-step instructions, difficulty, cook time, calories, tags — plus Chef Pro fields (techniques, wine pairings, plating notes).

---

## Project Structure

```
eatguai/
├── app.py                → Entry point
├── config.py             → Centralized config (modes, colors, paths, API keys)
├── models.py             → Pydantic v2 data models
│
├── core/
│   ├── vision.py              → Claude Vision detection + ingredient normalization
│   ├── recommender.py         → TF-IDF engine with weighted scoring
│   └── substitution_engine.py → Claude-powered ingredient substitution
│
├── components/
│   ├── ui_renderer.py    → Dynamic HTML/CSS theming per mode
│   └── analytics.py      → Session analytics dashboard
│
├── infra/                → Original GCP infrastructure (preserved)
│   ├── main.tf
│   └── terraform.tfvars.example
│
└── recetas_backend_proceso_ultra.json  → 300 Spanish recipes
```

---

## Setup

### Hugging Face Spaces (current)
The app runs live at [huggingface.co/spaces/catoralonso/eatguai](https://huggingface.co/spaces/catoralonso/eatguai).

To deploy your own instance:
```bash
git clone https://github.com/catoralonso/eatguai.git
# Add ANTHROPIC_API_KEY to HF Spaces secrets
git push hf main
```

### Local
```bash
git clone https://github.com/catoralonso/eatguai.git && cd eatguai
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python app.py
```

### Original GCP Deploy (archived)
```bash
cd infra/
cp terraform.tfvars.example terraform.tfvars
# Edit project ID
terraform init
terraform apply -var-file="terraform.tfvars"
```

---

## Version History

| Version | Highlights |
|---------|-----------|
| **v4** *(current)* | Migrated to Anthropic Claude + HF Spaces. Claude-powered substitution engine replaces hardcoded dictionary. Dual modes, Pydantic v2, session analytics |
| v3 | Dark "Nevera de Noche" theme, recipe cards with match progress bar, user ratings. GCP / Vertex AI stack |
| v2 | First working integration: vision + recommendations. Cloud Run deploy |
