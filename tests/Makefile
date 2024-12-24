

.SUFFIXES: .sor .dummy

TARGETS := $(patsubst %.sor,%.dummy,$(wildcard *.sor))


all:
	@echo "make test"
	echo $(TARGETS)

.PHONY:
test: $(TARGETS)

.sor.dummy:
	./test.py $< 

clean:
	rm -fv *.out
