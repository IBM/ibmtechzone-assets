# Use an official Python runtime as the base image
FROM python:3.11-slim

RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the streamlit application code to the container
COPY src .

# Copy logo and ground truth
COPY /images /images
COPY /ground_truth /ground_truth

# Expose the port on which the streamlit application will run
EXPOSE 8501

# # Set the environment variable for Streamlit
# ENV STREAMLIT_APP=app.py

# Run the streamlit application
CMD ["streamlit", "run", "app.py"]