FROM python:3.10

RUN mkdir -p /app
COPY . /app/
WORKDIR /app
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN /root/.local/bin/poetry env use python3.10
RUN /root/.local/bin/poetry install
ENV web=True
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/cogent-quarter-225505-0014ba86ee14.json
EXPOSE 8080
#ENTRYPOINT ["/bin/bash"]
ENTRYPOINT ["/root/.local/bin/poetry","run", "uvicorn", "nerves:app", "--host", "0.0.0.0", "--port","8080"]
