# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    mariadb-server \
    default-mysql-client \
    libmariadb-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask app and port 3306 for MariaDB
EXPOSE 5000 3306

# Define environment variables for Flask and MySQL
ENV FLASK_APP=run.py
ENV MYSQL_ROOT_PASSWORD=admin
ENV MYSQL_DATABASE=mealmate
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=admin

# Copy the MariaDB configuration file
COPY my.cnf /etc/mysql/my.cnf

# Add the init_db.sh script
COPY init_db.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init_db.sh

# Start MariaDB service and run the Flask app
CMD ["sh", "-c", "mysqld_safe & sleep 5 && flask run --host=0.0.0.0"]
