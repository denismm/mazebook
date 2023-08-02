mypy --strict $@
flake8 --extend-ignore=E203,E128,E501,E741,E302,E201,E202,E305,E124 $@
