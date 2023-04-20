# Use node lts
FROM python:alpine

# Set working directory
WORKDIR /omega-robot/

# Install dependencies
COPY requirements.pip ./
RUN pip install -r requirements.pip

# Build
COPY . ./

CMD python3 main.py
