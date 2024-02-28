#!/bin/bash

unset KUBECONFIG

cd .. && docker build -f docker/Dockerfile.latest \
             -t xiabin/haval .

docker tag xiabin/haval xiabin/haval:$(date +%y%m%d)