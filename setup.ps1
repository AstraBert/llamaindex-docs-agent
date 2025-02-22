docker compose up vector_db -d

conda env create -f environment.yml

conda activate environment.yml

python3 .\scripts\loadData.py

Set-Location .\scripts\

uvicorn main:app --host 0.0.0.0 --port 8000

conda deactivate