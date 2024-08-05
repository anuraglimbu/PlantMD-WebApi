FROM python:3.12.4-slim-bullseye

RUN mkdir /usr/src/imagestore

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && cat apt_requirements.txt | xargs apt -y --no-install-recommends install libmagic-dev ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/* \
    && apt autoremove \
    && apt autoclean

# Install Python dependencies
RUN pip install --upgrade pip gunicorn
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY . /usr/src/app/
#CMD ["cp", ".prod-env",".env"]

RUN chmod +x /usr/src/app/entrypoint.sh

#RUN chmod -R 777 /usr/src/app
EXPOSE 8000


# Set the entrypoint
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
