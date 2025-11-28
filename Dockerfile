FROM python:3.14-slim

# Set docker related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /tech2C_challenge

# Install Python dependencies
COPY requirements.txt /tech2C_challenge/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /tech2C_challenge/