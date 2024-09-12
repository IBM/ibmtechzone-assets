FROM python:3.11.4

WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install pipenv
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 8000

# # Define environment variable
# ENV NAME World

# Run app.py when the container launches
CMD ["python", "main.py"]