init:
	sudo pip install -r requirements.txt

test:
	nosetests tests

test-coverage:
	nosetests tests --with-coverage --cover-min-percentage=60 --cover-inclusive --cover-package=logtrust

check-style:
	pep8 assignments/*.py tests/*.py
