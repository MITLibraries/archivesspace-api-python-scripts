all: bandit black flake8 pylama

bandit:
	pipenv run bandit -r asaps tests --skip B101

black:
	pipenv run black --check --diff asaps tests

flake8:
	pipenv run flake8 asaps tests

pylama:
	pipenv run pylama asaps tests
