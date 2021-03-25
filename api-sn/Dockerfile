FROM python:3.6.1-alpine
RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
EXPOSE 5000
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get purge -y --auto-remove gcc and-build-dependencies
CMD ["python", "api.py"]
