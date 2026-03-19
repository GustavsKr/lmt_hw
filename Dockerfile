# 1. Use an official Python base image
FROM python:3.13-slim

# 2. Set the working directory inside the container
WORKDIR /code

# 3. Copy only requirements first (helps with Docker caching)
COPY ./requirements.txt /code/requirements.txt

# 4. Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 5. Copy your application code
COPY ./app /code/app

# 6. Run the app using the FastAPI CLI
# --port 80 is standard for containers, --proxy-headers is best practice
CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]