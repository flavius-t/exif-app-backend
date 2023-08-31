FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create app working directory
WORKDIR /app

# Install system dependencies
RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into container
COPY . /app/

# Expose port Flask app runs on
EXPOSE 5000

# Set the entrypoint to run Flask app
CMD ["python3", "exif.py"]