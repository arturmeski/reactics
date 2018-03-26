/*
    Copyright (c) 2012-2014
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#ifndef RS_SYMRSSTATE_HH
#define RS_SYMRSSTATE_HH

#include <vector>
#include <algorithm>
#include <map>
#include <cassert>
#include "cudd.hh"
#include "types.hh"
#include "macro.hh"
#include "bdd_macro.hh"
#include "rs.hh"
#include "options.hh"
#include "memtime.hh"

using std::cout;
using std::cerr;
using std::endl;
using std::vector;
using std::map;

class SymRS
{
    friend class ModelChecker;
    friend class FormRSCTL;

    RctSys *rs;
    Cudd *cuddMgr;
    Options *opts;

    StateEntityToAction stateToAct;

    BDD *initStates;
    vector<BDD> *pv;
    vector<BDD> *pv_act;
    vector<BDD> *pv_succ;
    BDD *pv_E;
    BDD *pv_act_E;
    BDD *pv_succ_E;

    vector<BDD> *pv_noact;
    vector<BDD> *partTrans;

    BDD *monoTrans;

    unsigned int totalReactions;
    unsigned int totalStateVars;
    unsigned int totalActions;

    BDD encEntity_raw(Entity entity, bool succ) const;
    BDD encEntity(Entity entity) const {
        return encEntity_raw(entity, false);
    }
    BDD encActEntity(Entity entity) const {
		assert(entity < pv_act->size());
        return (*pv_act)[entity];
    }
    BDD encEntitySucc(Entity entity) const {
        return encEntity_raw(entity, true); 
    }
    BDD encEntitiesConj_raw(const Entities &entities, bool succ);
    BDD encEntitiesConj(const Entities &entities) {
        return encEntitiesConj_raw(entities, false);
    }
    BDD encEntitiesConjSucc(const Entities &entities) {
        return encEntitiesConj_raw(entities, true);
    }
    BDD encEntitiesDisj_raw(const Entities &entities, bool succ);
    BDD encEntitiesDisj(const Entities &entities) {
        return encEntitiesDisj_raw(entities, false);
    }
    BDD encEntitiesDisjSucc(const Entities &entities) {
        return encEntitiesDisj_raw(entities, true);
    }
    BDD encStateActEntitiesConj(const Entities &entities);
    BDD encStateActEntitiesDisj(const Entities &entities);

    /**
     * @brief Complements an encoding of a given state by negating all the variables that are not set to true
     *
     * @return Returns the encoded state
     */
    BDD compState(const BDD &state) const;

    BDD compContext(const BDD &context) const;

    std::string decodedStateToStr(const BDD &state);
    void printDecodedStates(const BDD &states);

	BDD encNoContext(void);

    void initBDDvars(void);
    void encodeTransitions(void);
    void encodeTransitions_old(void);
    void encodeInitStates(void);
    void mapStateToAct(void);
    void encode(void);

    int getMappedStateToActID(int stateID) const { assert(stateID < static_cast<int>(totalStateVars)); return stateToAct[stateID]; }

public:
    SymRS(RctSys *rs, Options *opts)
    {
        this->rs = rs;
        this->opts = opts;
        totalStateVars = rs->getEntitiesSize();
        totalReactions = rs->getReactionsSize();
        totalActions = rs->getActionsSize();

        partTrans = nullptr;
        monoTrans = nullptr;

        encode();
    }
    vector<BDD> *getEncPV(void) { return pv; }
    vector<BDD> *getEncPVsucc(void) { return pv_succ; }
    BDD *getEncPV_E(void) { return pv_E; }
    BDD *getEncPVsucc_E(void) { return pv_succ_E; }
    BDD *getEncPVact_E(void) { return pv_act_E; }
    vector<BDD> *getEncPartTrans(void) { return partTrans; }
    BDD *getEncMonoTrans(void) { return monoTrans; }
    BDD getEncState(const Entities &entities);
    BDD *getEncInitStates(void) { return initStates; }
    Cudd *getCuddMgr(void) { return cuddMgr; }
    unsigned int getTotalStateVars(void) { return totalStateVars; }
    BDD encEntity(std::string name) const {
        return encEntity(rs->getEntityID(name));
    }
    BDD encActStrEntity(std::string name) const;
    BDD getBDDtrue(void) const { return BDD_TRUE; }
    BDD getBDDfalse(void) const { return BDD_FALSE; }
};

#endif

