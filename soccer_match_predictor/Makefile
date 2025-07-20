.PHONY: install setup run test clean lint format scrape-data train-model

# Installation and setup
install:
	poetry install

install-pip:
	pip install -r requirements.txt

setup: install
	cp .env.example .env
	echo "Setup complete! Edit .env file with your API keys"

# Development commands
run:
	poetry run python src/main.py

run-web:
	poetry run streamlit run streamlit_app.py

notebook:
	poetry run jupyter lab notebooks/

# Data collection
scrape-data:
	poetry run python scripts/scrape_fbref.py

collect-api-data:
	poetry run python scripts/collect_api_data.py

# Model training and evaluation
train:
	poetry run python scripts/train_model.py

evaluate:
	poetry run python scripts/evaluate_model.py

# Code quality
test:
	poetry run pytest tests/ -v

lint:
	poetry run flake8 src/ tests/

format:
	poetry run black src/ tests/ scripts/

# Cleanup
clean:
	find . -type d -name "__pycache__" -delete
	find . -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -delete

# Export requirements for deployment
requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes