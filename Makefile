.PHONY: up
up:
	docker-compose up -d

.PHONY: down
down:
	docker-compose down

.PHONY: exec
exec:
	docker-compose exec develop python3 main.py

.PHONY: build
build:
	docker build . --no-cache
	
