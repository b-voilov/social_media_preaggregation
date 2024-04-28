# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app
COPY . .
RUN ./install.sh
# Set the command to run the application
CMD ["sleep", "infinity"]