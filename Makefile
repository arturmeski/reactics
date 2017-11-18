CC = g++
CUDD_PATH = cudd
CUDD_INCLUDE = $(CUDD_PATH)/obj/cuddObj.o $(CUDD_PATH)/cudd/libcudd.a $(CUDD_PATH)/mtr/libmtr.a \
	$(CUDD_PATH)/st/libst.a $(CUDD_PATH)/util/libutil.a \
	$(CUDD_PATH)/epd/libepd.a $(CUDD_PATH)/obj/libobj.a
INCLUDES=-Icudd/include
CPPFLAGS = -Wall $(INCLUDES) #-Werror
#CPPFLAGS = -Wall -DNDEBUG
CXXFLAGS = -std=c++14 -O3 -DPUBLIC_RELEASE -DNDEBUG #-g
LDLIBS = $(CUDD_INCLUDE) #-lcuddobj #/lib64/libcudd.so.2 #$(CUDD_INCLUDE)

OBJ = rs.o symrs.o mc.o rsin_driver.o rsin_parser.o rsin_parser.lex.o formrsctl.o 

all: main

cleanly:
	rm -f *.lex.cc *.lex.o location.hh stack.hh position.hh rsin_parser.cc rsin_parser.hh

clean: cleanly
	rm -f *.o main *~ makefile.dep tags

cleanall: clean

makefile.dep: *.cc *.hh
	for i in *.cc; do g++ $(INCLUDES) -MM -MG "$${i}"; done > $@

include makefile.dep

main: main.o $(OBJ)

rsin_parser.hh: rsin_parser.cc

rsin_parser.cc: rsin_parser.yy
	bison -o rsin_parser.cc rsin_parser.yy

rsin_parser.o: rsin_parser.cc

rsin_parser.lex.cc: rsin_parser.ll
	flex rsin_parser.ll
	mv lex.yy.c rsin_parser.lex.cc

