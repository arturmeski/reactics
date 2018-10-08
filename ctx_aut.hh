/*
    Copyright (c) 2018
    Artur Meski <meski@ipipan.waw.pl>
*/

#ifndef RS_CTX_AUT_HH
#define RS_CTX_AUT_HH

#include <iostream>
#include <set>
#include <map>
#include <vector>
#include <string>
#include <cstdlib>
// #include "rs.hh"
#include "types.hh"
// #include "options.hh"
// #include "stateconstr.hh"

using std::cout;
using std::endl;

class RctSys;
class Options;
class StateConstr;

class CtxAut
{
    friend class SymRS;

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
    void addTransition(std::string srcStateName, std::string dstStateName, StateConstr *stateConstr);
    void showTransitions(void);
    void makeProgressive(void);
    void pushContextEntity(Entity entity_id);
    void saveCurrentContextSet(Process proc_id);
    void setOptions(Options *opts)
    {
      this->opts = opts;
    }
    size_t statesCount(void)
    {
      return states_ids.size();
    }

  private:
    RctSys *parent_rctsys;
    Options *opts;
    StatesById states_ids;
    StatesByName states_names;
    State init_state_id;
    bool init_state_defined;
    EntitiesForProc tmpProcEntities;
    Entities tmpEntities;
    CtxAutTransitions transitions;
};

#endif /* RS_CTX_AUT_HH */
