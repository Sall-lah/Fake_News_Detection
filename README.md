# Fake News Detection API

A local Flask API that classifies news articles as **fake** or **true** using a LightGBM classifier with TF-IDF vectorization. Trains on startup if no pre-trained model exists — no manual training step required.

---

## Table of Contents

- [Dataset](#dataset)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
  - [Local (Conda)](#local-conda)
  - [Docker](#docker)
- [API Endpoints](#api-endpoints)
- [Training Pipeline](#training-pipeline)
- [Model Evaluation](#model-evaluation)
- [Testing](#testing)
- [Project Structure](#project-structure)

---

## Dataset

The model is trained on the **Fake News Detection** dataset from Kaggle, consisting of two CSV files:

| File         | Rows    | Columns                                                   |
|--------------|---------|-----------------------------------------------------------|
| `Fake.csv`   | 23,537  | `title`, `text`, `subject`, `date` — labeled `0` (fake)   |
| `True.csv`   | 21,417  | `title`, `text`, `subject`, `date` — labeled `1` (true)   |

**Total:** ~44,954 articles after combining.

The dataset contains news articles from various subjects. Fake articles span subjects like *News*, *Politics*, *Government News*, *Left-wing*, *US_News*, *Middle-east*, and *World News*. True articles come from *politicsNews* and *worldnews* subjects (Reuters).

The dataset is included in the repository under `dataset/` and is automatically loaded during training.

---

## How It Works

1. **Cold start** — If `model.pkl` does not exist, the app runs `train()` on startup, which loads the CSV files, preprocesses text, trains a TF-IDF + LightGBM pipeline, and saves `model.pkl`.
2. **Warm start** — If `model.pkl` already exists, it loads directly (seconds).
3. **Prediction** — Incoming `title` + `text` is cleaned, vectorized through the same TF-IDF, and classified by LightGBM.

**Text preprocessing** (`preprocess.py`):
- Lowercase normalization
- Remove non-alphabetic characters
- Strip English stop words
- Deduplicate tokens
- Normalize whitespace

---

## Installation

### Prerequisites

- Python 3.13+
- Conda (recommended) or pip

### Conda (recommended)

```bash
# Create environment
conda create -n fake_news_detection python=3.13
conda activate fake_news_detection

# Install dependencies
pip install -r requirements.txt
```

### Pip (standalone)

```bash
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux
pip install -r requirements.txt
```

---

## Usage

### Local (Conda)

```bash
conda activate fake_news_detection
python app.py
```

On first run, you'll see training output:
```
No pre-trained model found. Running training...
Fitting 2 folds for each of 5 candidates, totalling 10 fits
Training Complete
Accuracy: 0.9987
...
Model saved to ...\model.pkl
Model loaded successfully. API is ready.
```

Subsequent runs load `model.pkl` instantly:
```
Model loaded from existing model.pkl. API is ready.
```

The API starts on `http://localhost:5000`.

### Docker

```bash
# Build
docker build -t fake-news-detection .

# Run
docker run -p 5000:5000 fake-news-detection
```

The Docker image uses `python:3.13-slim`, installs dependencies, copies the dataset, and trains the model at container startup (model is not baked into the image).

---

## API Endpoints

### `GET /`

HTML documentation page — describes available endpoints with examples.

### `GET /info`

Machine-readable API metadata.

```bash
curl http://localhost:5000/info
```

Response:
```json
{
  "status": "ok",
  "name": "Fake News Detection API",
  "version": "1.0.0",
  "endpoints": {
    "GET /": "API documentation (HTML)",
    "GET /info": "API metadata (this endpoint)",
    "POST /predict": "Classify news article (JSON)"
  },
  "predict_request": {
    "title": "string (optional)",
    "text": "string (required)"
  },
  "predict_response": {
    "status": "ok | error",
    "label": "fake | true"
  }
}
```

### `POST /predict`

Classify a news article.

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"title": "Breaking News", "text": "Article content here"}'
```

Response:
```json
{"status": "ok", "label": "fake"}
```

| Status Code | Condition                     |
|-------------|-------------------------------|
| `200`       | Prediction succeeded          |
| `400`       | Empty input after cleaning    |
| `503`       | Model not loaded              |
| `500`       | Prediction error              |

---

## Training Pipeline

The training pipeline (`train.py`) performs the following steps:

1. **Load** `Fake.csv` and `True.csv`, assign labels (`0` = fake, `1` = true)
2. **Concatenate** into a single DataFrame
3. **Combine** `title` + `text` into a single `string` column
4. **Clean** text using the shared `clean_text()` function (lowercase, remove non-letters, stop words, dedupe)
5. **Filter** empty/NA rows
6. **Split** 80/20 stratified train/test
7. **Build pipeline** — `TfidfVectorizer(max_features=20000, ngram_range=(1,1), min_df=1)` → `LGBMClassifier`
8. **Hyperparameter tuning** — `RandomizedSearchCV` with 5 iterations, 2-fold CV, scoring accuracy
9. **Evaluate** on test set
10. **Save** model to `model.pkl` via `joblib`

---

## Model Evaluation

After hyperparameter tuning, the best pipeline achieves:

| Metric    | Value   |
|-----------|---------|
| Accuracy  | 99.87%  |

**Best hyperparameters found:**
```yaml
tfidf__max_features: 20000
tfidf__ngram_range: (1, 1)
tfidf__min_df: 1
classifier__n_estimators: 200
classifier__learning_rate: 0.1
classifier__num_leaves: 15
classifier__max_depth: -1
```

---

## Testing

Tests use **pytest** and require the conda environment and `model.pkl`.

```bash
conda activate fake_news_detection
pytest tests/ -v
```

**26 tests** across 3 files:

| File                  | Tests | Scope                              |
|-----------------------|-------|------------------------------------|
| `test_endpoints.py`   | 9     | API routes, cold/warm start, /predict |
| `test_model.py`       | 11    | Model loading, prediction, training   |
| `test_preprocess.py`  | 6     | Text cleaning edge cases              |

---

## Project Structure

```
Fake_News_Detection/
├── app.py              # Flask API — startup, predict, /info, /
├── train.py            # Training pipeline (dataset → model.pkl)
├── model.py            # Model loading utilities (load_model, get_model)
├── preprocess.py       # Shared text cleaning (clean_text)
├── requirements.txt    # Pinned Python dependencies
├── Dockerfile          # Docker build (python:3.13-slim)
├── .dockerignore       # Docker build exclusions
├── dataset/
│   ├── Fake.csv        # Labeled fake news articles
│   └── True.csv        # Labeled true news articles
├── tests/
│   ├── conftest.py     # Shared test fixtures
│   ├── test_endpoints.py
│   ├── test_model.py
│   └── test_preprocess.py
├── model.pkl           # Pre-trained model (auto-generated)
├── .gitignore
├── AGENTS.md           # AI assistant instructions
└── README.md           # This file
```
