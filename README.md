# 🧊 EatguAI 🧊

AI-powered fridge assistant that detects ingredients from a photo using Gemini Vision and recommends recipes using TF-IDF cosine similarity — built on Google Cloud Vertex AI.

## How it works

1. Upload a photo of your fridge
2. Gemini Vision detects all visible ingredients
3. The recommendation engine matches them against a database of 130+ recipes
4. Get ranked recipes with step-by-step instructions

## Tech Stack

- **Vision:** Google Gemini 2.0 Flash via Vertex AI
- **Recommendation:** TF-IDF + Cosine Similarity + Fuzzy Matching (scikit-learn)
- **Validation:** Pydantic v2
- **Interface:** Gradio
- **Cloud:** Google Cloud Vertex AI Workbench

## Setup for Virtual Machine en Vertex AI
```bash
# 1. Clone the repo
git clone https://github.com/catoralonso/eatguai.git
cd eatguai
pip install -r requirements.txt

# 2. Google Cloud authentication
gcloud auth login
gcloud auth application-default login

# 3. Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# 4. Set project
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)

# 5. Launch
python app_gradiov4.py
```

> **Note:** On a new Qwiklabs lab the API takes 2-3 minutes to activate after step 3.
> The app will enable it automatically on startup, but wait a few minutes before uploading a photo.

## Setup for docker in CloudRun
```bash
# 1. Clone the Repo
git clone https://github.com/catoralonso/eatguai.git
cd eatguai

# 2. Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data
ENV PORT=8080
EXPOSE 8080
CMD ["python", "app_gradiov4.py"]
EOF

# 3. Set variables
AR_REPO='eatguai'
SERVICE_NAME='grupo2'
GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
GOOGLE_CLOUD_REGION='us-central1'

# 4. Create repository in artifact registry
gcloud artifacts repositories create "$AR_REPO" \
  --location="$GOOGLE_CLOUD_REGION" \
  --repository-format=Docker

# 5. API activation
gcloud services enable aiplatform.googleapis.com run.googleapis.com

# 6. Build and upload image
gcloud builds submit --tag "$GOOGLE_CLOUD_REGION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/$AR_REPO/$SERVICE_NAME"

# 7. Launch CloudRun
gcloud run deploy "$SERVICE_NAME" \
  --image "$GOOGLE_CLOUD_REGION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/$AR_REPO/$SERVICE_NAME" \
  --platform managed \
  --region "$GOOGLE_CLOUD_REGION" \
  --allow-unauthenticated \
  --memory 2Gi \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT"
```

## Project Structure
```
eatguai/
├── app_gradiov4.py          → Application entry point 
├── config.py                → Centralized configuration (colors, routes, modes)
├── models.py                → Pydantic data validation models
├── requirements.txt
│
├── core/
│   ├── vision.py            → Gemini Vision ingredient detection module
│   └── recommender.py       → TF-IDF recommendation engine
│
├── components/
│   ├── ui_renderer.py       → HTML/CSS rendered (night fridge theme)
│   ├── detector.py          → Detection wrapper with error handling
│   └── analytics.py         → User analytics dashboard
│
├── releases/                → Previous app versions log
│   ├── app_gradiov2.py
│   └── app_gradiov3.py
│
└── data/                    → Local only (not included in the repository)
    └── recetas_backend_proceso_ultra.json
```

## Modes

| Mode | Description | Max missing ingredients |
|------|-------------|------------------------|
| 🧊 Survival | Cook with what you have right now | 2 |
| 👨‍🍳 Chef Pro | Full gastronomic experience with techniques and pairings | 5 |

## Version Log

### v4 — Pro Edition *(current)*
- Modular architecture: `core/` + `components/` separation
- Smart recommender: fuzzy matching + ingredient substitutions
- Pydantic v2 validation across all data layers
- Two modes: Survival and Chef Pro with dynamic UI
- Session analytics dashboard
- Centralized config with environment variable support
- Professional error handling with logging

### v3
- Improved interface, design and user experience
- Dark theme "Nevera de Noche"
- Expandable recipe cards with match progress bar
- User ratings saved to CSV

### v2
- Basic interface
- Ingredient detection from photo
- Recipe recommendations

## Dataset

200+ Spanish recipes stored in `recetas_backend_proceso_ultra.json` with the following fields per recipe: key ingredients with quantities, step-by-step instructions, difficulty, time, calories, tags, and Chef Pro fields (techniques, pairing, plating notes).
