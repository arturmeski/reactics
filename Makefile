CC = g++
CUDD_PATH = cudd
CUDD_INCLUDE=cudd/lib/libcudd.a
INCLUDES=-Icudd/include
CPPFLAGS_SILENT = $(INCLUDES)
CPPFLAGS = -Wall $(CPPFLAGS_SILENT) #-Werror
#CPPFLAGS = -Wall $(INCLUDES) -DNDEBUG 
CXXFLAGS_SILENT = -O3 -g
CXXFLAGS = -std=c++14 $(CXXFLAGS_SILENT)
#CXXFLAGS = -std=c++14 -O3 -DPUBLIC_RELEASE -DNDEBUG #-g
LDLIBS = $(CUDD_INCLUDE) 

OBJ = rs.o ctx_aut.o symrs.o mc.o rsin_driver.o rsin_parser.o rsin_parser.lex.o formrsctl.o 

all: main

cleanly:
	rm -f *.lex.cc *.lex.o location.hh stack.hh position.hh rsin_parser.cc rsin_parser.hh

clean: cleanly
	rm -f *.o main *.orig *~ makefile.dep tags

cleanall: clean

makefile.dep: *.cc *.hh
	for i in *.cc; do g++ $(INCLUDES) -MM -MG "$${i}"; done > $@

include makefile.dep

main: main.o $(OBJ)

rsin_parser.hh: rsin_parser.cc

rsin_parser.cc: rsin_parser.yy
	bison -o rsin_parser.cc rsin_parser.yy

rsin_parser.o: rsin_parser.cc

rsin_parser.lex.o: rsin_parser.lex.cc
	$(CC) $(CXXFLAGS_SILENT) $(CPPFLAGS_SILENT) -c -o $@ rsin_parser.lex.cc

rsin_parser.lex.cc: rsin_parser.ll
	flex rsin_parser.ll
	mv lex.yy.c rsin_parser.lex.cc

style:
	astyle --max-code-length=130 --break-closing-brackets --convert-tabs --add-brackets --max-instatement-indent=40 -s2 -C -xG -S -f -p -H -k1 -c --style=kr --align-pointer=name *.cc *.hh	

commit: style
	git commit -a
