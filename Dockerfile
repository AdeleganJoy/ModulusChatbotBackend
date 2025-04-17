FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5005

# Start both Rasa and Rasa Actions in the background
CMD rasa run --enable-api --cors "*" -p 5005 & rasa run actions
