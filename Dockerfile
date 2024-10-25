FROM ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu

ENV PATH="/root/.local/bin:${PATH}"

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
WORKDIR /app

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure poetry to not create virtual environment in container
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY ecg2af_webapp /app/ecg2af_webapp
COPY ./ml4h /app/ml4h

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["poetry", "run", "start-app"]
