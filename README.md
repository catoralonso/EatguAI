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

## Setup
```bash
# 1. Clone the repo
git clone https://github.com/catoralonso/EatguAI.git
cd EatguAI
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
## Project Structure

```
The-Fridge-Survival-Guide/
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

130+ Spanish recipes stored in `recetas_backend_proceso_ultra.json` with the following fields per recipe: key ingredients with quantities, step-by-step instructions, difficulty, time, calories, tags, and Chef Pro fields (techniques, pairing, plating notes).
