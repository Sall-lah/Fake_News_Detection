FROM python:3.13-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dataset (model is trained at runtime, not baked into image)
COPY dataset/ ./dataset/

# Copy application code (include train.py for startup training)
COPY app.py model.py preprocess.py train.py ./

EXPOSE 5000

# Use Flask dev server for local development
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
