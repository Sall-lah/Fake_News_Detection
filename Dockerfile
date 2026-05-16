FROM python:3.13-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and model
COPY model.pkl .
COPY app.py model.py preprocess.py ./

EXPOSE 5000

# Use Flask dev server for local development
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
