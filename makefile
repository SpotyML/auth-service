install:
	pip install -r requirements.txt

lint:
	flake8 src/ tests/

test:
	pytest

run:
	python src/main.py
