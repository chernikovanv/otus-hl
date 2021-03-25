FROM python:3.6.1-alpine
RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
EXPOSE 5000
RUN apk add --no-cache gcc \
    && apk add libc-dev \
    && pip install --upgrade pip \
    && pip install -r requirements.txt
CMD ["python", "api.py"]
