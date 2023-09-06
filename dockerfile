FROM python:3.10

RUN mkdir -p /app
COPY . /app/
WORKDIR /app
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-cache
ENV web=True
#ENV GOOGLE_APPLICATION_CREDENTIALS=/app/cogent-quarter-225505-0014ba86ee14.json
ENV OPENAI_API_KEY=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
EXPOSE 8080
#ENTRYPOINT ["/bin/bash"]
ENTRYPOINT ["uvicorn", "nerves:app", "--host", "0.0.0.0", "--port","8080"]
#ENTRYPOINT ["panel", "serve", "nerves.py", "--port", "8080"]