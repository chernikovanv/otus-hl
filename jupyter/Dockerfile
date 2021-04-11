FROM python:3.6.1
RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
EXPOSE 8888
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
CMD ["python", "-m","jupyter","lab","--allow-root","--ip","0.0.0.0","--port","8888","--no-browser","--notebook-dir='/usr/src/app/'","--NotebookApp.token=''"]
