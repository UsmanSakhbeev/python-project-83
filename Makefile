install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8080
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

reinstall:
	python3 -m pip install --user dist/*.whl --force-reinstall
