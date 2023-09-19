FROM ubuntu:20.04

# Install wkhtmltopdf
RUN apt-get update && apt-get install -y \
    curl \
    fontconfig \
    libfreetype6 \
    libjpeg-turbo8 \
    libpng16-16 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    xfonts-75dpi \
    xfonts-base \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LJO "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb" \
    && dpkg -i wkhtmltox_0.12.6-1.focal_amd64.deb \
    && rm wkhtmltox_0.12.6-1.focal_amd64.deb

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip3 install -r requirements.txt

# Copy the application files
COPY school1.py .
COPY config.py .
COPY school1.db .

# Run the application
CMD ["python3", "school1.py"]
