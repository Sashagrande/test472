postgres := postgres://postgres:postgres@localhost:5432/postgres
dbmate-args := \
    --url=${postgres}?sslmode=disable \
    --migrations-dir=./database/migrations \
  	--wait

dbmate-install:
	curl -fsSL -o /usr/local/bin/dbmate https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64
	chmod +x /usr/local/bin/dbmate

db-up:
	docker compose up postgres --detach
	dbmate ${dbmate-args} up

db-drop:
	docker compose up postgres --detach
	dbmate ${dbmate-args} drop

build:
	docker compose build service

run:
	docker compose run service

stop:
	docker compose stop