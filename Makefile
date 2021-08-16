lint: bandit black flake8 isort

bandit:
	pipenv run bandit -r asaps

black:
	pipenv run black --check --diff asaps tests
	
coveralls: test
	pipenv run coveralls

flake8:
	pipenv run flake8 asaps tests

isort:
	pipenv run isort asaps tests --diff
	
test:
	pipenv run pytest --cov=asaps
