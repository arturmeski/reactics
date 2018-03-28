/*
    Copyright (c) 2018
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#ifndef RS_TYPES_HH
#define RS_TYPES_HH

#include <set>
#include <map>
#include <vector>
#include <string>

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

typedef std::vector<Reaction> Reactions;
typedef std::map<Process, Reactions> ReactionsForProc;

typedef std::vector<std::string> EntitiesById;
typedef std::map<std::string, Entity> EntitiesByName;
typedef std::set<Entities> EntitiesSets;

typedef unsigned int State;
typedef std::vector<std::string> StatesById;
typedef std::map<std::string, State> StatesByName;

typedef std::map<Process, Entities> EntitiesForProc;

struct ReactionCond {
  Entities rctt;
  Entities inhib;
};

typedef std::vector<ReactionCond> ReactionConds;
typedef std::map<Entity, ReactionConds> DecompReactions;
typedef std::vector<int> StateEntityToAction;

struct CtxAutTransition {
  State src_state;
  Entities ctx;
  State dst_state;
};

typedef std::vector<CtxAutTransition> CtxAutTransitions;

#endif
