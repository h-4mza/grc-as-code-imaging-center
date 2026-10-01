.PHONY: demo load test lint docs reset

demo:
	docker-compose up --build

reset:
	docker-compose down -v

load:
	docker-compose exec api grc load

test:
	pytest

lint:
	ruff check .
	ruff format --check .

docs:
	mkdocs serve
