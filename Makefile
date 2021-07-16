all: bandit black flake8 isort pylama

bandit:
	pipenv run bandit -r asaps tests --skip B101

black:
	pipenv run black --check --diff asaps tests

flake8:
	pipenv run flake8 asaps tests

isort:
	pipenv run isort . --diff

pylama:
	pipenv run pylama asaps tests
