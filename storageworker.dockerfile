FROM python:3

RUN mkdir -p /opt/src/warehouse
WORKDIR /opt/src/warehouse

COPY warehouse/StorageWorker.py ./application.py
COPY warehouse/configuration.py ./configuration.py
COPY warehouse/RoleCheckDecorator.py ./RoleCheckDecorator.py
COPY warehouse/models.py ./models.py
#COPY warehouse/requirements.txt ./requirements.txt
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/warehouse"

ENTRYPOINT ["python", "./application.py"]