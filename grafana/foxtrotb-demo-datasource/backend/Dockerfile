# Use the official Golang image as a parent image.
FROM golang:1.22 as builder

# Set the Current Working Directory inside the container.
WORKDIR /app

# Copy the Go Modules manifests and download the dependencies.
# This will cache the downloading step unless the manifests change.
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the project's source code into the container.
COPY . .

# Install Mage.
RUN go install github.com/magefile/mage@latest

# Build your project using Mage.
# Replace 'build' with your actual build command as defined in your Magefile.
RUN go mod download



# Replace './myapp' with the path to the built application if different.
CMD ["./myapp"]
