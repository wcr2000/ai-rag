# Dockerfile

# Base Image
FROM python:3.13-slim

# Set working directory
WORKDIR /usr/src/app
# Copy requirements and source code
COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 80

# Run the application
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]