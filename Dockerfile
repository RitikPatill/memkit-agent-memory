FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

# Full server wired in M3
CMD ["uvicorn", "memkit.server:app", "--host", "0.0.0.0", "--port", "8000"]
