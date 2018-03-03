/*
    Copyright (c) 2018
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#ifndef RS_CTX_AUT_HH
#define RS_CTX_AUT_HH

#include <iostream>
#include <set>
#include <map>
#include <vector>
#include <string>
#include <cstdlib>
#include "types.hh"
#include "macro.hh"
#include "options.hh"

using std::cout;
using std::endl;

class CtxAut
{
	public:
		CtxAut(Options *opts) { setOptions(opts); }
		bool hasState(std::string name);
		void addState(std::string stateName);
		State getStateID(std::string name);
		void printAutomaton(void);
		void showStates(void);
		void addTransition(std::string srcStateName, std::string dstStateName);
		void pushContextEntity(Entity entity_id);	
	    void setOptions(Options *opts) { this->opts = opts; }
		
	private:
	    Options *opts;
		StatesById states_ids;
		StatesByName states_names;
		Entities tmpEntities;	
};

#endif /* RS_CTX_AUT_HH */
