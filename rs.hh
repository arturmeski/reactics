/*
    Copyright (c) 2012-2014
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#ifndef RS_RS_HH
#define RS_RS_HH

#include <iostream>
#include <set>
#include <map>
#include <vector>
#include <string>
#include <cstdlib>
#include "macro.hh"
#include "options.hh"
#include "memtime.hh"

using std::cout;
using std::endl;

class RctSys
{
    friend class SymRS;
    friend class SymRSstate;
	friend class CtxAut;
public:
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
private:
    Reactions reactions;
    EntitiesSets initStates;

    Entities actionEntities;

    EntitiesByIds entities_ids;
    EntitiesByName entities_names;

    Entities tmpReactants;
    Entities tmpInhibitors;
    Entities tmpProducts;

    Entities tmpState;

    Entity getEntityID(std::string entityName);

    Options *opts;

public:
    void setOptions(Options *opts)
    {
        this->opts = opts;
    }
    bool hasEntity(std::string entityName);
    void addEntity(std::string entityName);
    std::string getEntityName(Entity entityID);
    void pushReactant(std::string entityName);
    void pushInhibitor(std::string entityName);
    void pushProduct(std::string entityName);
    void commitReaction(void);
    std::string entityToStr(const Entity entity) {
        return entities_ids[entity];
    }
    std::string entitiesToStr(const Entities &entities);
    void showReactions(void);
    void pushStateEntity(std::string entityName);
    void commitInitState(void);
    void addActionEntity(std::string entityName);
    bool isActionEntity(Entity entity);
    void resetInitStates(void) {
        initStates.clear();
    }
    unsigned int getEntitiesSize(void) {
        return entities_ids.size();
    }
    unsigned int getReactionsSize(void) {
        return reactions.size();
    }
    unsigned int getActionsSize(void) {
        return actionEntities.size();
    }
    void showInitialStates(void);
    void showActionEntities(void);
    void printSystem(void);
};

// Context Automaton
class CtxAut
{
    typedef unsigned int State;
    typedef std::set<State> States;
	struct Transition {
		State src_state;
		State dst_state;
	};
};


#endif

