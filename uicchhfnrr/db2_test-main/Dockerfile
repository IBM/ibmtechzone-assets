# Use the official Python image as a base image
FROM python:3.12

RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any dependencies specified in requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire current directory into the container at /app
COPY . /app/

# Expose port 80 to the outside world
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "test_db2_connection:app", "--host", "0.0.0.0", "--port", "8000"]
