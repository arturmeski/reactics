/*
    Copyright (c) 2018
    Artur Meski <meski@ipipan.waw.pl>
*/

#ifndef RS_TYPES_HH
#define RS_TYPES_HH

#include <set>
#include <map>
#include <vector>
#include <string>
#include "cudd.hh"

typedef unsigned char Oper;

typedef std::vector<BDD> BDDvec;

typedef unsigned int Entity;
typedef std::set<Entity> Entities;
struct Reaction {
  Entities rctt;
  Entities inhib;
  Entities prod;
};

typedef unsigned int Process;
typedef std::vector<std::string> ProcessesById;
typedef std::map<std::string, Process> ProcessesByName;
typedef std::set<Process> ProcSet;

typedef std::vector<Reaction> Reactions;
typedef std::map<Process, Reactions> ReactionsForProc;

typedef std::vector<std::string> EntitiesById;
typedef std::map<std::string, Entity> EntitiesByName;
typedef std::set<Entities> EntitiesSets;

typedef unsigned int State;
typedef std::vector<std::string> StatesById;
typedef std::map<std::string, State> StatesByName;

typedef std::map<Process, Entities> EntitiesForProc;

typedef std::map<Entity, unsigned int> EntiesToLocalIndex;
typedef std::map<Process, EntiesToLocalIndex> LocalIndicesForProcEntities;

struct ReactionCond {
  Entities rctt;
  Entities inhib;
};

typedef std::vector<ReactionCond> ReactionConds;
typedef std::map<Entity, ReactionConds> DecompReactions;
typedef std::vector<int> StateEntityToAction;

class StateConstr;
struct CtxAutTransition {
  State src_state;
  EntitiesForProc ctx;
  StateConstr *state_constr;
  State dst_state;
};

typedef std::vector<CtxAutTransition> CtxAutTransitions;

#endif
