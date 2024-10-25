FROM ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu

# Set working directory
WORKDIR /app

# Copy application code
COPY ecg2af_webapp /app/ecg2af_webapp
COPY requirements.txt /app/ecg2af_webapp/requirements.txt
COPY ml4h /app/ml4h

#install requirements
RUN pip install -r /app/ecg2af_webapp/requirements.txt

WORKDIR /app/ecg2af_webapp
# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "/app/ecg2af_webapp/app.py"]
