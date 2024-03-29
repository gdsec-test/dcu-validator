#!/bin/sh
# FOR TESTING WITH DEV domainservice (read-only)
kubectl --context dev-admin -n abuse-api-dev port-forward --address 0.0.0.0 service/domainservice-rest 8080:8080 &
# FOR TESTING WITH PROD domainservice (read-only)
# kubectl --context prod-admin -n abuse-api-prod port-forward --address 0.0.0.0 service/domainservice-rest 8080:8080 &
DOMAIN_SERVICE=$!

while true; do sleep 10s; done

kill $DOMAIN_SERVICE
