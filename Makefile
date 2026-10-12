.PHONY: demo demo-down reset load test lint docs

demo:
	docker-compose up -d --build
	@echo "Attente de la disponibilite de Postgres..."
	@timeout=60; \
	while ! docker-compose exec -T postgres pg_isready -U grc_user -d grc_db > /dev/null 2>&1; do \
		timeout=$$((timeout - 1)); \
		if [ $$timeout -le 0 ]; then \
			echo "Erreur : Timeout de 60s depasse en attendant Postgres." >&2; \
			exit 1; \
		fi; \
		sleep 1; \
	done; \
	echo "Postgres est pret !"
	@echo "Attente de la disponibilite de l'API..."
	@timeout=60; \
	while ! curl -s -f http://localhost:8000/docs > /dev/null 2>&1; do \
		timeout=$$((timeout - 1)); \
		if [ $$timeout -le 0 ]; then \
			echo "Erreur : Timeout de 60s depasse en attendant l'API FastAPI." >&2; \
			exit 1; \
		fi; \
		sleep 1; \
	done; \
	echo "L'API est prete !"
	@echo "Reinitialisation de la base de donnees..."
	docker-compose exec -T api grc reset --yes
	@echo "Chargement du referentiel GRC en base..."
	docker-compose exec -T api grc load
	@echo "Ingestion des constats SARIF (Projet 1 Trivy & Projet 3 AD Audit)..."
	docker-compose exec -T api grc ingest --source sarif --file grc/scans/projet1_trivy.sarif
	docker-compose exec -T api grc ingest --source sarif --file grc/scans/projet3_ad_audit.sarif
	@echo ""
	@echo "=========================================================="
	@echo "   Stack GRC-as-Code deployee et prete a l'emploi !"
	@echo "   Dashboard Streamlit : http://localhost:8501"
	@echo "   API FastAPI (Swagger) : http://localhost:8000/docs"
	@echo "=========================================================="

demo-down:
	docker-compose down -v

reset:
	docker-compose exec -T api grc reset --yes

load:
	docker-compose exec api grc load

test:
	pytest

lint:
	ruff check .
	ruff format --check .

docs:
	mkdocs serve
