eval "$(conda shell.bash hook)"

conda activate llamaindex-docs

python3 /app/loadData.py

conda deactivate