ARG PORT
ARG DEBUG
 
# Use official Python base image
#FROM python:3-alpine AS base # python:alpine manages packages with 'apk'. I know 'apt' so selected python:slim
FROM python:3-slim AS base

# Set working directory
WORKDIR /app

# Install uv (via pipx)
RUN pip install --no-cache-dir uv 
  
COPY . .

# Create virtual environment and install deps via uv
RUN python -m uv venv && python -m uv sync

#FROM python:3.12-alpine

# Copy the rest of the app
#COPY --from=base /app /app

ENV PORT=${PORT} 

# Expose the port that the application listens on. #TODO: replace with variable
EXPOSE ${PORT}

# Command to run your script
#CMD ["uv", "run", "--env-file=/app/src/gitlab_calls/.env", "/app/src/app.py"] # DEBUG. to remove!!
CMD ["uv","run","/app/src/app.py"]
