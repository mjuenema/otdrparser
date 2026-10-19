

all:
	@echo "make test"
	@echo "make build"
	@echo "make publish"
	@echo "make testpublish"



test:
	make -C tests test


build: test
	flit build --format wheel
	flit build --format sdist


testpublish: build
	flit publish --repository=testpypi --format wheel
	flit publish --repository=testpypi --format sdist

publish: build
	flit publish --repository=pypi --format wheel
	flit publish --repository=pypi --format sdist
