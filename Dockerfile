# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Update package lists and install Tesseract OCR and its development library
# RUN apt-get update && \
#     apt-get -qq -y install tesseract-ocr && \
#     apt-get -qq -y install libtesseract-dev && \
#     apt-get -qq -y install libgl1-mesa-glx

# Use the Franky1 Tesseract OCR Docker image with Tesseract 5.3.3
FROM franky1/tesseract:5.3.3

# Check the installed Tesseract version
RUN tesseract --version

# Set the working directory in the container
WORKDIR /app

# Copy the Python dependencies file to the container at /app
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Specify the default command to run on container startup
CMD ["gunicorn", "centro_secretariat.wsgi:application", "--timeout", "120"]