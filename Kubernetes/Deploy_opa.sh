#! /bin/bash

kubectl apply -f namespace_opa.yml &&
kubectl apply -f service_opa.yml &&
kubectl apply -f statefulset_opa.yml &&
kubectl apply -f ingress_opa.yml
