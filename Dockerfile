# Dockerfile

# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /install

# Copy only requirements.txt to leverage Docker cache
COPY requirements.txt .

# Install dependencies
# แก้ไขเรื่อง click version ใน requirements.txt หรือเปลี่ยน Python version ตรงนี้เป็น 3.10+ ถ้า click ต้องการ
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix="/install" -r requirements.txt

# Stage 2: Final Application Image
FROM python:3.13-slim 

# Set the working directory inside the container
WORKDIR /app

# Create a non-root user and group for better security
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Copy installed Python packages from the builder stage
COPY --from=builder /install /usr/local 

# Copy the application source code
# Ensure .dockerignore is in place!
COPY ./src ./src
COPY ./main.py ./main.py
# COPY ./.env.example ./.env.example # ถ้าคุณมีไฟล์นี้และต้องการ copy

# --- Option 1: Bake the vector_store_index into the image ---
# If your vector_store_index is relatively small and pre-built.
# Make sure 'vector_store_index/' is NOT in your .dockerignore if you use this.
# COPY ./vector_store_index ./vector_store_index

# --- Option 2: Expect vector_store_index to be mounted as a volume (Recommended) ---
# If you use this, 'vector_store_index/' SHOULD be in your .dockerignore.

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Change ownership of the app directory
RUN chown -R appuser:appuser /app
# If using Option 1 for vector_store_index and copying it to /app/vector_store_index:
# RUN chown -R appuser:appuser /app/vector_store_index

# Switch to the non-root user
USER appuser

# Expose the port
EXPOSE 8000

# Default command
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]