#!/bin/bash

docker build -t "trading_opa" .
docker login -u "arnolyoussa"
docker tag trading_opa arnoldyoussa/trading_opa
docker push arnoldyoussa/trading_opa