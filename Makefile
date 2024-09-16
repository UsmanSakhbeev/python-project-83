install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 5432
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:8080 page_analyzer:app

reinstall:
	python3 -m pip install --user dist/*.whl --force-reinstall

build:
	./build.sh
