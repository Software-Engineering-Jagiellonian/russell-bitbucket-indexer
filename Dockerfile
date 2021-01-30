FROM python:3.8-buster
WORKDIR /app

RUN pip3 install fregeindexerlib==0.4.0 && pip3 install requests

COPY main.py .
COPY bitbucket_indexer.py .
COPY bitbucket_indexer_config.py .
COPY utils.py .

CMD ["python3", "main.py"]
