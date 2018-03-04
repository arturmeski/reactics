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
#include "types.hh"
#include "ctx_aut.hh"
#include "macro.hh"
#include "options.hh"
#include "memtime.hh"

using std::cout;
using std::endl;

class CtxAut;

class RctSys
{
	    friend class SymRS;
	    friend class SymRSstate;

	public:
		RctSys(void);
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

		void ctxAutEnable(void);		
		void ctxAutAddState(std::string stateName);
		void ctxAutSetInitState(std::string stateName);
		void ctxAutAddTransition(std::string srcStateName, std::string dstStateName);
		void ctxAutPushNamedContextEntity(std::string entity_name);
		
		bool initStatesDefined(void) { return initStates.size() != 0; }
		
	private:
	    Reactions reactions;
	    EntitiesSets initStates;

	    Entities actionEntities;

		CtxAut *ctx_aut;

	    EntitiesByIds entities_ids;
	    EntitiesByName entities_names;

	    Entities tmpReactants;
	    Entities tmpInhibitors;
	    Entities tmpProducts;

	    Entities tmpState;

	    Options *opts;

	    Entity getEntityID(std::string entityName);

};

#endif
