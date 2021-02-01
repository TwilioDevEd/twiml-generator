lint:
	@echo "Running isort and black"
	@find . -name "*.py" ! -name "*_pb2*" ! -path "./venv/*" -exec black {} \+ -exec isort -m3 --tc {} \+
