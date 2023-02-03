#!/bin/bash

( cd firesat && ./gradlew stopFuseki )

docker-compose up stop
