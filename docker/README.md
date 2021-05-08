# Usage of CodeCarbon with Docker

## Pre-requisis

Clone the project
```sh
git clone https://github.com/mlco2/codecarbon/codecarbon.git
```

Prepare configuration :
```sh
cd codecarbon
cp docker/docker.env .env
```


## Run

```sh
docker-compose up -d
```
This will run :
 - Postgresql on localhost:5480
 - PGAdmin 4 on [http://localhost:5080](http://localhost:5080) login : *test@test.com* , password : *test* (Dans PGAdmin, use the host *postgres_codecarbon* and port *5432* for in docker network access)
 - CodeCarbon API on [http://localhost:5080](http://localhost:5080)
 

## Stop

```sh
docker-compose down
```

Postgres database and PGAdmin configuration are saved in separate volumes.

## View logs

```sh
docker logs codecarbon-api_codecarbon_api_1
```

## Execute tests
```sh
docker exec codecarbon-api_codecarbon_api_1 tox
```

## Force build
```sh
docker-compose up --build
```


## Cleaning
Delete all files :
```sh
docker-compose down -v
docker image rm codecarbon-api
```