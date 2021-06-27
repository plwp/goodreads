#!/bin/bash
rm -r ./db/rabbitmq-test
rm -r ./db/postgres-data-test
docker-compose down
docker-compose -f docker-compose.test.yaml build
docker-compose -f docker-compose.test.yaml up -d

echo 'Waiting for RabbitMQ...'
sleep 30

python3 ./API/integrationtests.py

echo 'Running averager unit tests...'
docker exec -it goodreads_averager_1 python3 /app/averager.unittest.py
echo 'Running DataModel.commands unit tests...'
docker exec -it goodreads_averager_1 python3 /app/DataModel/commands.unittest.py

docker-compose down
rm -r ./db/rabbitmq-test
rm -r ./db/postgres-data-test

echo '...done.'
