eval "$(conda shell.bash hook)"

conda activate llamaindex-docs

cd /app/
uvicorn main:app --port 8000 --host 0.0.0.0