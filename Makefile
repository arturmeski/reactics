
clean:
	rm -rf rs/__pycache__ smt/rs/__pycache__ __pycache__
	find . -name '*.pyc' -exec rm -f {} \;
	
cleanall: clean
	rm -rf *.log