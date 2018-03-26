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
typedef std::vector<Reaction> Reactions;
typedef std::vector<std::string> EntitiesByIds;
typedef std::map<std::string, Entity> EntitiesByName;
typedef std::set<Entities> EntitiesSets;

typedef unsigned int State;
typedef std::vector<std::string> StatesById;
typedef std::map<std::string, State> StatesByName;

struct Transition {
	State src_state;
	Entities ctx;
	State dst_state;
};

typedef std::vector<Transition> Transitions;

#endif
