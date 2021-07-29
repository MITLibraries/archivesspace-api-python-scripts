lint: bandit flake8 isort
	
test: coveralls 

bandit:
	pipenv run bandit -r asaps
	
coveralls: test
	pipenv run coveralls

flake8:
	pipenv run flake8 .

isort:
	pipenv run isort . --diff
	
test:
	pipenv run pytest --cov=asaps
