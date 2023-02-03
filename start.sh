#!/bin/bash

( cd firesat && ./gradlew startFuseki )

docker-compose up
