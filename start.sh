#!/bin/bash

( cd firesat && ./gradlew startFuseki && ./gradlew load)

docker-compose up --build
