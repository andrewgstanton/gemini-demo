#!/bin/bash

echo "clearing old version of database.db"

rm -r -f database.db

echo "🛑 Stopping all running containers..."
docker ps -q | xargs -r docker stop

echo "🧹 Removing all containers..."
docker ps -aq | xargs -r docker rm

echo "🧼 Removing all images..."
docker images -q | xargs -r docker rmi -f

echo "✅ Docker cleanup complete."