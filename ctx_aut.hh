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
#include "rs.hh"
#include "types.hh"
#include "macro.hh"
#include "options.hh"

using std::cout;
using std::endl;

class RctSys;

class CtxAut
{
	public:
		CtxAut(Options *opts, RctSys *parent_rctsys);
		bool hasState(std::string name);
		void addState(std::string stateName);
		void setInitState(std::string stateName);
		State getInitState(void);
		State getStateID(std::string name);
		std::string getStateName(State state_id);
		void printAutomaton(void);
		void showStates(void);
		void addTransition(std::string srcStateName, std::string dstStateName);
		void showTransitions(void);
		void pushContextEntity(Entity entity_id);	
	    void setOptions(Options *opts) { this->opts = opts; }
		size_t statesCount(void) { return states_ids.size(); }
		
	private:
		RctSys *parent_rctsys;
	    Options *opts;
		StatesById states_ids;
		StatesByName states_names;
		State init_state_id;
		bool init_state_defined;
		Entities tmpEntities;
		CtxAutTransitions transitions;
};

#endif /* RS_CTX_AUT_HH */
