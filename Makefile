linting: bandit flake8 isort
	
testing: coveralls pytest

bandit:
	pipenv run bandit -r asaps
	
coveralls: 
	pipenv run coveralls

flake8:
	pipenv run flake8 .

isort:
	pipenv run isort . --diff
	
pytest:
	pipenv run pytest
