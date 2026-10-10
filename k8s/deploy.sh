#!/bin/sh
set -e

cd "$(dirname "$0")/.."

docker compose build backend web
docker save football-community-backend:latest football-community-web:latest | sudo k3s ctr images import -

kubectl apply -f k8s/00-namespace.yaml
kubectl -n football create secret generic app-env --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f k8s/

kubectl -n football rollout restart deployment/backend deployment/web
kubectl -n football rollout status statefulset/db --timeout=300s
kubectl -n football rollout status deployment/backend --timeout=300s
kubectl -n football rollout status deployment/web --timeout=120s
kubectl -n football get pods
