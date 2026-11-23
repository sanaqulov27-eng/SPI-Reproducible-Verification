FROM python:3.13-slim
WORKDIR /pkg
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Offline run on the hashed copies shipped in the package. Use "--online" to re-download from the pinned commit.
CMD ["python", "scripts/run_all.py"]
