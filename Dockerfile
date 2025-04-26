# Stage 1: Build React Frontend
FROM node:18-alpine as frontend
WORKDIR /app

# Install frontend dependencies (cached layer)
COPY client/package.json client/package-lock.json ./
RUN npm ci --silent

# Copy source and build
COPY client/ .
RUN npm run build

# Stage 2: Python Backend with Production React
FROM python:3.9-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY chatbot_backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY chatbot_backend/ .

# Copy built React app from Stage 1
COPY --from=frontend /app/build ./client/build

# Runtime config
ENV FLASK_ENV=production
EXPOSE 5000

# Start Flask server (serves both API and React)
CMD ["gunicorn", "chatbot:app", "--bind", "0.0.0.0:5000", "--workers", "4"]