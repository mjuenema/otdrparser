

all:
	@echo "make test"
	@echo "make build"
	@echo "make publish"
	@echo "make testpublish"



test:
	make -C tests test


build: test
	flit build --setup-py --format wheel
	flit build --setup-py --format sdist


testpublish: build
	flit publish --repository=testpypi --setup-py --format wheel
	flit publish --repository=testpypi --setup-py --format sdist

publish: build
	flit publish --repository=pypi --setup-py --format wheel
	flit publish --repository=pypi --setup-py --format sdist
