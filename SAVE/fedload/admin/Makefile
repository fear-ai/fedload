.PHONY: all setup run test clean docker

setup:
	python -m venv venv
	. venv/bin/activate && pip install -r fed_load/requirements.txt

run:
	. venv/bin/activate && python fed_load/main.py

test:
	. venv/bin/activate && pytest fed_load/tests/

docker:
	docker build -t fedload .
	docker run --rm fedload

clean:
	rm -rf __pycache__ *.csv .pytest_cache .ipynb_checkpoints
