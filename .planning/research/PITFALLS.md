# Pitfalls Research

**Domain:** Adding a model training pipeline (pandas CSV loading, preprocessing, LightGBM + TF-IDF training with RandomizedSearchCV) to an existing Flask API
**Researched:** 2026-05-16
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Data Leakage — Preprocessing Before Train/Test Split

**What goes wrong:**
Applying TF-IDF vectorization, scaling, imputation, or any `fit()`-based transformation on the full dataset before splitting into train/test. This leaks test-set statistics (vocabulary, IDF values, feature means) into the training pipeline, producing overly optimistic cross-validation scores that collapse on truly unseen data.

**Why it happens:**
The existing `preprocess.py` cleans text (lowercase, remove stopwords, deduplicate words). It's tempting to run it on the combined CSV, then split. But TF-IDF's `fit_transform()` learns vocabulary and IDF from all documents — including what should be held out. The scikit-learn docs explicitly warn: "Always split the data into train and test subsets first, particularly before any preprocessing steps."

**How to avoid:**
1. Load raw CSV → label → combine title+text → **split first** (`train_test_split` with `stratify=y`)
2. Apply `preprocess.py` cleaning to train and test separately (or use a sklearn `FunctionTransformer` inside a Pipeline)
3. Build a `Pipeline([("tfidf", TfidfVectorizer()), ("lgbm", LGBMClassifier())])` and pass it to `RandomizedSearchCV` — the Pipeline guarantees `fit_transform` only sees training folds during CV
4. **Never** call `fit()` or `fit_transform()` on test data — only `transform()`

**Warning signs:**
- CV accuracy is suspiciously high (>95%) but drops on a held-out set
- TF-IDF vocabulary size is enormous (includes rare test-only words)
- `fit_transform(X)` called before `train_test_split(X, y)`

**Phase to address:**
Model Training Pipeline phase — the training script must enforce split-first ordering.

---

### Pitfall 2: Training Blocking Flask Server Startup

**What goes wrong:**
Running the full training pipeline (CSV load + preprocessing + RandomizedSearchCV with CV folds) synchronously during Flask startup. With `n_iter=50` and `cv=5`, that's 250 model fits. LightGBM on a dataset of tens of thousands of articles can take minutes to hours. The Flask dev server won't bind to its port until training finishes, causing Docker health checks to fail and the container to restart in a loop.

**Why it happens:**
The requirement says "auto-run training on server startup when `model.pkl` is missing." A naive implementation puts `train_model()` at module level before `app.run()`, blocking the entire process.

**How to avoid:**
1. **Conditional skip**: Check `os.path.exists("model.pkl")` before any training code runs — this is already in the requirements
2. **Separate training script**: Keep `train_model.py` as a standalone script. The Dockerfile should `RUN python train_model.py` during the **build phase**, not at runtime. This ensures the model is pre-baked into the image
3. **Fallback runtime training**: If `model.pkl` is still missing at runtime (e.g., user mounts an empty volume), run training in a **background thread** so Flask can start serving `/` and `/info` immediately. Use a `/health` endpoint that returns 503 until training completes
4. **Timeout guard**: Cap training time with a signal/alarm or thread timeout; save a partial model or fail loudly

**Warning signs:**
- `docker run` exits after 30s with no logs (health check killed the container)
- Flask never prints "Running on http://..." 
- Training logs appear but no HTTP requests can be served

**Phase to address:**
Docker/Deployment phase — build-time training + runtime fallback pattern.

---

### Pitfall 3: RandomizedSearchCV Hyperparameter Search Taking Too Long

**What goes wrong:**
An unconstrained hyperparameter search with too many iterations (`n_iter`), too many CV folds, or a search space that includes extreme values (e.g., `max_depth` up to 50, `n_estimators` up to 10000). Combined with LightGBM's own internal threading, this can cause CPU oversubscription and memory explosion.

**Why it happens:**
LightGBM has its own OpenMP threading. `RandomizedSearchCV(n_jobs=-1)` spawns parallel trials. If each trial also uses all cores, the product `n_jobs_search * n_jobs_lgbm` exceeds available CPUs, causing thread contention that makes training **slower** than single-threaded. A Stack Overflow report documented 17-hour training times caused by this exact oversubscription.

**How to avoid:**
1. **Limit search scope**: Start with `n_iter=20-30`, `cv=3` (not 5 or 10), and narrow parameter ranges
2. **Thread budgeting**: Set `RandomizedSearchCV(n_jobs=1)` and `LGBMClassifier(n_jobs=-1)` — let LightGBM use all cores per trial, but run trials sequentially. Or ensure `n_jobs_search * n_jobs_lgbm <= num_cpus`
3. **Early stopping**: Use `LGBMClassifier(n_estimators=1000)` with `early_stopping_rounds=50` inside a custom CV loop, or set `n_estimators` to a moderate fixed value in the search
4. **Timebox**: Log elapsed time per iteration; abort if a single trial exceeds a threshold
5. **Use `refit=True`** so the best model is available after search completes

**Warning signs:**
- System monitor shows 100% CPU on all cores but progress bar barely moves
- Memory usage grows linearly with each CV fold
- `n_iter * cv * n_jobs` product exceeds available CPU count

**Phase to address:**
Model Training Pipeline phase — hyperparameter search configuration.

---

### Pitfall 4: Pickle/Joblib Version Mismatch Between Training and Inference

**What goes wrong:**
The model is trained and saved with one version of scikit-learn/LightGBM/NumPy, but the Flask API loads it with different versions. This causes `ValueError: node array from the pickle has an incompatible dtype`, `AttributeError: Can't get attribute '_RemainderColsList'`, or silent incorrect predictions.

**Why it happens:**
scikit-learn **does not support** loading models across versions. The docs state: "there are no supported ways to load a model trained with a different version of scikit-learn." Even minor version bumps (1.6.1 → 1.7.1) have broken pickle compatibility for `ColumnTransformer` and tree-based models. Docker images may pull latest package versions during `pip install`, diverging from the training environment.

**How to avoid:**
1. **Pin all versions** in `requirements.txt` with exact pins (`==`), not ranges (`>=`):
   ```
   scikit-learn==1.7.1
   lightgbm==4.6.0
   numpy==2.4.4
   scipy==1.17.1
   joblib==1.5.3
   ```
2. **Train inside the same Docker image** that serves the model — run `python train_model.py` as a `RUN` step in the Dockerfile so training and inference share identical dependency versions
3. **Version stamp the model**: Save a `metadata.json` alongside `model.pkl` containing the versions of all key packages used during training. On startup, the Flask app verifies versions match and warns on mismatch
4. **Test model load**: Add a test that loads `model.pkl` and runs a prediction — this catches version mismatches in CI

**Warning signs:**
- `InconsistentVersionWarning` logged at startup
- `ValueError` or `AttributeError` on `joblib.load()`
- Model loads but predictions are garbage (silent corruption)

**Phase to address:**
Model Training Pipeline phase (version pinning) + Docker/Deployment phase (build-time training).

---

### Pitfall 5: NaN/Empty String Handling After Preprocessing

**What goes wrong:**
After combining `title + " " + text` and running `preprocess.py` (removing stopwords, non-letters, duplicate words, normalizing whitespace), some rows become empty strings. Passing empty strings to TF-IDF or LightGBM causes `ValueError: empty vocabulary` or silent NaN propagation that corrupts training.

**Why it happens:**
The existing `preprocess.py` already handles empty-string detection for inference (returns error status). But the training script processes the full CSV in bulk. Rows with only stopwords, punctuation, or whitespace will be reduced to empty strings. Pandas `dropna()` only catches `NaN`, not empty strings.

**How to avoid:**
1. After preprocessing, filter out rows where the processed string is empty or whitespace-only:
   ```python
   df = df[df['processed_text'].str.strip().astype(bool)]
   ```
2. Log how many rows were dropped and why
3. Handle NaN in non-text columns explicitly: `df.fillna({'title': '', 'text': ''})` before combining
4. Validate that both classes (fake=0, true=1) still have sufficient samples after filtering

**Warning signs:**
- TF-IDF throws `ValueError: empty vocabulary; perhaps the documents only contain stop words`
- Class distribution becomes heavily skewed after filtering
- Training succeeds but model performs poorly on short inputs

**Phase to address:**
Model Training Pipeline phase — data cleaning and validation step.

---

### Pitfall 6: Label Encoding Mismatch Between Training and Inference

**What goes wrong:**
The training script labels fake=0, true=1, but the inference code expects the opposite mapping, or LightGBM internally reorders classes. The model returns predictions that are inverted (fake classified as true).

**Why it happens:**
LightGBM's `LGBMClassifier` learns class labels from the `y` array. If `y` contains strings like `"fake"` and `"true"`, LightGBM alphabetically encodes them (`"fake"` → 0, `"true"` → 1). But if the training script manually assigns 0/1 and the inference code checks against a different convention, predictions will be inverted. Additionally, if the CSV datasets have inconsistent labeling (one file uses 0 for fake, another uses 1), the combined dataset will have swapped labels.

**How to avoid:**
1. **Explicitly encode labels** as integers before training:
   ```python
   fake_df['label'] = 0  # 0 = fake
   true_df['label'] = 1  # 1 = true
   ```
2. **Verify class mapping**: After training, print `model.classes_` to confirm `[0, 1]` ordering
3. **Consistent inference**: The Flask app's `model.py` must use the same mapping. Add an assertion:
   ```python
   assert list(model.classes_) == [0, 1], f"Unexpected class order: {model.classes_}"
   ```
4. **Save label mapping** in metadata for documentation

**Warning signs:**
- Model accuracy is ~50% on a balanced dataset (random guessing due to inverted labels)
- `model.classes_` shows unexpected values
- Predictions are consistently wrong for obvious cases

**Phase to address:**
Model Training Pipeline phase — data loading and label assignment.

---

## Moderate Pitfalls

### Pitfall 7: Memory Explosion with Large Datasets + LightGBM + CV

**What goes wrong:**
Loading a large CSV (e.g., 50K+ rows) into pandas, creating TF-IDF features (sparse matrix), then running RandomizedSearchCV with multiple CV folds causes memory to spike. Each CV fold creates a copy of the data, and LightGBM creates `Dataset` objects. With `n_jobs > 1`, multiple copies exist simultaneously.

**Why it happens:**
A Stack Overflow report documented 16 GB RAM exhaustion with LightGBM + RandomizedSearchCV on a moderate dataset. Each parallel trial creates its own `lightgbm.Dataset` object, and the sparse TF-IDF matrix is duplicated across folds.

**How to avoid:**
1. Use `RandomizedSearchCV(n_jobs=1)` with `LGBMClassifier(n_jobs=-1)` — one trial at a time, but each trial uses all cores
2. Limit `max_features` in `TfidfVectorizer` (e.g., 10000-50000) to control vocabulary size
3. Use `subsample` in LightGBM to train on a fraction of data per iteration
4. Monitor memory during training; add explicit `del` and `gc.collect()` between steps

**Warning signs:**
- System swap usage increases during training
- `MemoryError` or process killed by OOM killer
- Training slows dramatically after a few CV folds

**Phase to address:**
Model Training Pipeline phase — training configuration.

---

### Pitfall 8: TF-IDF Vocabulary Drift Between Training and Inference

**What goes wrong:**
The training script fits a `TfidfVectorizer` on the training data, but the inference pipeline uses the existing `preprocess.py` function to clean text before passing it to the loaded model. If the preprocessing steps differ between training and inference (e.g., different stopword lists, different duplicate-word removal logic), the input text won't match the vocabulary the model was trained on.

**Why it happens:**
The project already has `preprocess.py` used by the Flask API for inference. The training script must apply **identical** preprocessing. Any divergence means the TF-IDF vectorizer sees different text patterns during training vs. inference.

**How to avoid:**
1. **Use the same preprocessing function** in both training and inference — import `preprocess.py` in the training script
2. **Wrap preprocessing in a sklearn transformer** (e.g., `FunctionTransformer`) inside the Pipeline so it's serialized with the model
3. **Test end-to-end**: Run a known article through the training pipeline's preprocessing, then through the inference pipeline, and verify the outputs match

**Warning signs:**
- Model performs well on training data but poorly on real API requests
- TF-IDF produces mostly zero vectors for inference inputs
- Preprocessing function was modified after model was trained

**Phase to address:**
Model Training Pipeline phase — preprocessing integration.

---

### Pitfall 9: Docker Build Caching Skips Model Training

**What goes wrong:**
The Dockerfile uses `RUN python train_model.py` during build, but Docker's layer caching skips re-running it when only the training script changes (not the CSV files or requirements). The container ships with a stale `model.pkl`.

**Why it happens:**
Docker caches layers based on file checksums. If `train_model.py` changes but the CSV files and `requirements.txt` don't, Docker may reuse the cached training layer.

**How to avoid:**
1. **Copy training script before the RUN step**, not after:
   ```dockerfile
   COPY train_model.py .
   COPY dataset/ ./dataset/
   RUN python train_model.py
   COPY app.py model.py preprocess.py ./
   ```
2. **Use `--no-cache`** for rebuilds: `docker build --no-cache -t fake-news-api .`
3. **Add a build arg** that forces cache bust: `ARG BUILD_TIMESTAMP` and pass `--build-arg BUILD_TIMESTAMP=$(date +%s)`
4. **Better approach**: Don't bake training into the Dockerfile at all. Train locally, commit `model.pkl`, and have the Dockerfile only COPY it. Use a separate CI step for retraining.

**Warning signs:**
- Model predictions don't reflect recent training script changes
- `docker build` completes in seconds (should take minutes if training runs)
- Model file timestamp is old

**Phase to address:**
Docker/Deployment phase — build configuration.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Train at runtime instead of build time | No Dockerfile changes needed | Slow startup, health check failures, inconsistent environments | **Never** for this project — Docker must preload the model |
| Skip stratified split | Simpler code | Class imbalance in train/test, unreliable metrics | Never for binary classification with imbalanced classes |
| Use `n_jobs=-1` for both search and LightGBM | "Maximum parallelism" | CPU oversubscription, slower training, memory explosion | Never — budget threads explicitly |
| Hardcode CSV paths in training script | Quick to write | Breaks in Docker, breaks on different OS | Never — use relative paths from project root |
| Don't pin dependency versions | Easier to install latest | Pickle version mismatches, silent model corruption | **Never** for ML model serialization |
| Skip metadata logging | Less code | No way to debug model version issues later | Acceptable for throwaway experiments only |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `preprocess.py` → training script | Duplicating preprocessing logic in training script | Import and reuse `preprocess.clean_text()` from existing module |
| `train_model.py` → `app.py` | Training script saves model to a different path than `app.py` loads from | Use a single constant `MODEL_PATH = "model.pkl"` shared by both |
| `requirements.txt` → Docker build | `pip install -r requirements.txt` pulls latest versions | Pin all versions with `==` and verify training/inference match |
| CSV files → Docker image | CSV files not included in Docker build context (blocked by `.dockerignore`) | Ensure `dataset/` is NOT in `.dockerignore` if training at build time |
| LightGBM → Windows dev / Linux Docker | Model trained on Windows, loaded in Linux container (path separators, binary compatibility) | Train inside the Docker image or verify cross-platform compatibility |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| TF-IDF with no `max_features` | Vocabulary grows to 100K+ terms, slow training, high memory | Set `max_features=10000` to `50000` | Dataset > 20K articles with diverse vocabulary |
| RandomizedSearchCV with `cv=10` | Training takes 10x longer than needed | Use `cv=3` for initial search, `cv=5` for final validation | Any dataset with > 5K rows |
| `n_iter=100` in RandomizedSearchCV | Diminishing returns after ~30 iterations, wasted time | Start with `n_iter=20`, increase only if needed | Any hyperparameter search |
| No early stopping for LightGBM | Model overfits, training wastes iterations on plateau | Use `n_estimators=1000` + `early_stopping_rounds=50` | Any LightGBM training |
| Loading full CSV into pandas without chunking | Memory spike on large files | Use `pd.read_csv()` with `dtype` optimization or chunking | CSV files > 500MB |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Pickle deserialization of untrusted `model.pkl` | Arbitrary code execution on model load | Only load models built by your own training pipeline; document this in README |
| Exposing training errors in API responses | Information leakage about model internals | Catch training exceptions at startup; return generic 500 to clients |
| No input length limits on `/predict` | Memory exhaustion from extremely long text | Add `max_length` validation in the Flask route before preprocessing |

## "Looks Done But Isn't" Checklist

- [ ] **Train/test split:** Verify split happens BEFORE any `fit()` or `fit_transform()` calls — not just before `model.fit()`
- [ ] **TF-IDF vocabulary:** Confirm `TfidfVectorizer` is inside a sklearn Pipeline, not fitted separately before the model
- [ ] **Preprocessing parity:** Run the same article through training preprocessing and inference preprocessing; outputs must match exactly
- [ ] **Label consistency:** Print `model.classes_` after training and verify `[0, 1]` ordering matches inference expectations
- [ ] **Empty row handling:** Count rows dropped due to empty preprocessing output; verify both classes still have sufficient samples
- [ ] **Version pinning:** All ML dependencies in `requirements.txt` use `==` pins, not `>=`
- [ ] **Docker build training:** Verify `model.pkl` is generated during `docker build`, not expected at runtime
- [ ] **Health endpoint:** `/health` returns model load status and version metadata
- [ ] **Random seeds:** `random_state` set on `train_test_split`, `RandomizedSearchCV`, and `LGBMClassifier` for reproducibility
- [ ] **Model load test:** A test exists that loads `model.pkl` and runs a prediction without errors

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Data leakage discovered after training | MEDIUM | Re-train with correct split-first ordering; compare metrics to quantify leakage impact |
| Pickle version mismatch at runtime | LOW | Pin versions to match training environment; retrain if versions must change |
| Training blocks startup (container restart loop) | LOW | Move training to Docker build phase; add conditional skip for existing `model.pkl` |
| Label encoding inverted | MEDIUM | Retrain with explicit label mapping; add assertion in inference code |
| Hyperparameter search too slow | LOW | Reduce `n_iter`, `cv`, and budget threads; retrain with constrained search |
| TF-IDF vocabulary mismatch | MEDIUM | Retrain with Pipeline wrapping TF-IDF; ensure preprocessing parity |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Data leakage (preprocessing before split) | Model Training Pipeline | Unit test: verify TF-IDF fitted only on train data; check CV scores are realistic |
| Training blocks startup | Docker/Deployment | Integration test: `docker run` starts within 30s; `/health` returns 200 |
| Hyperparameter search too long | Model Training Pipeline | Log training time; assert it completes within timeout (e.g., 10 min) |
| Pickle version mismatch | Model Training Pipeline + Docker | CI test: load `model.pkl` in clean environment; version check at startup |
| NaN/empty string handling | Model Training Pipeline | Test: verify no empty strings reach TF-IDF; log dropped row count |
| Label encoding mismatch | Model Training Pipeline | Test: assert `model.classes_ == [0, 1]`; verify predictions on known samples |
| Memory explosion | Model Training Pipeline | Monitor RAM during training; assert peak < available memory |
| Preprocessing drift | Model Training Pipeline | Test: same input through training and inference preprocessing produces identical output |
| Docker build cache skips training | Docker/Deployment | Verify `model.pkl` timestamp matches build time; use `--no-cache` flag |
| TF-IDF vocabulary drift | Model Training Pipeline | Test: Pipeline serialization includes vectorizer; inference uses loaded model's vectorizer |

## Sources

- scikit-learn 1.7/1.8 docs: "Common pitfalls and recommended practices" — data leakage prevention (Confidence: HIGH)
- scikit-learn 1.7 docs: "Model persistence" — pickle/joblib version compatibility warnings (Confidence: HIGH)
- MachineLearningMastery: "How to Avoid Data Leakage When Performing Data Preparation" (Confidence: HIGH)
- DataLemur/DataSchool: "How to prevent data leakage in pandas & scikit-learn" (Confidence: HIGH)
- Stack Overflow: LightGBM + RandomizedSearchCV memory/CPU oversubscription issues (Confidence: HIGH)
- Stack Overflow: TF-IDF fit_transform on full dataset before split (Confidence: HIGH)
- Stack Overflow: Flask model loading at startup vs per-request (Confidence: HIGH)
- GitHub issues: scikit-learn pickle compatibility breaks (1.6.1 → 1.7.1 ColumnTransformer, 1.2.2 → 1.3.0 tree models) (Confidence: HIGH)
- Flask docs: Celery background task patterns (Confidence: HIGH)
- Docker ML deployment best practices — build-time vs runtime training (Confidence: MEDIUM)

---
*Pitfalls research for: Adding model training pipeline to Flask API*
*Researched: 2026-05-16*
