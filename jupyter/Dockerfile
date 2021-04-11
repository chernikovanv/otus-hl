FROM python:3.6.1
RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
RUN git clone https://github.com/chernikovanv/otus-hl-scripts.git
EXPOSE 88
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
CMD ["python", "-m","jupyter","lab","--allow-root","--ip","0.0.0.0","--port","88","--no-browser","--notebook-dir='/usr/src/app/otus-hl-scripts/'","--NotebookApp.token=''"]
