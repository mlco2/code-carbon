FROM python:3.7
WORKDIR /opt
RUN apt-get update && apt-get -y install postgresql-client

WORKDIR /opt/codecarbon
# Tips : relative path is from root project folder as we use context in docker-compose
#COPY ./docker/.env.docker .env
COPY setup.py .
RUN python3 setup.py install
COPY . .
EXPOSE 5000
ENTRYPOINT ["/opt/codecarbon/docker/entrypoint.sh"]