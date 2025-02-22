FROM condaforge/miniforge3

WORKDIR /app/
COPY shell /app/shell/
COPY environment.yml /app/
COPY docker/*.py /app/
COPY data /app/data/

RUN bash shell/conda_env.shell
RUN bash shell/qdrant_setup.shell

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]