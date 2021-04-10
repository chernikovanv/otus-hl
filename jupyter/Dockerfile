FROM jupyter/scipy-notebook
EXPOSE 8888
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
CMD ["python", "-m","jupyter","lab","--allow-root","--ip","0.0.0.0","--port","8888","--no-browser","--NotebookApp.token=''"]
