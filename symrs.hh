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

    struct ReactionCond {
        RctSys::Atoms rctt;
        RctSys::Atoms inhib;
    };
    typedef vector<ReactionCond> ReactionConds;
    typedef map<RctSys::Atom,ReactionConds> DecompReactions;
    typedef std::vector<int> StateAtomToAction; 

    StateAtomToAction stateToAct;

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

    BDD encAtom_raw(RctSys::Atom atom, bool succ) const;
    BDD encAtom(RctSys::Atom atom) const {
        return encAtom_raw(atom, false);
    }
    BDD encActAtom(RctSys::Atom atom) const {
		assert(atom < pv_act->size());
        return (*pv_act)[atom];
    }
    BDD encAtomSucc(RctSys::Atom atom) const {
        return encAtom_raw(atom, true); 
    }
    BDD encAtomsConj_raw(const RctSys::Atoms &atoms, bool succ);
    BDD encAtomsConj(const RctSys::Atoms &atoms) {
        return encAtomsConj_raw(atoms, false);
    }
    BDD encAtomsConjSucc(const RctSys::Atoms &atoms) {
        return encAtomsConj_raw(atoms, true);
    }
    BDD encAtomsDisj_raw(const RctSys::Atoms &atoms, bool succ);
    BDD encAtomsDisj(const RctSys::Atoms &atoms) {
        return encAtomsDisj_raw(atoms, false);
    }
    BDD encAtomsDisjSucc(const RctSys::Atoms &atoms) {
        return encAtomsDisj_raw(atoms, true);
    }
    BDD encStateActAtomsConj(const RctSys::Atoms &atoms);
    BDD encStateActAtomsDisj(const RctSys::Atoms &atoms);

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
        totalStateVars = rs->getAtomsSize();
        totalReactions = rs->getReactionsSize();
        totalActions = rs->getActionsSize();

        partTrans = NULL;
        monoTrans = NULL;

        encode();
    }
    vector<BDD> *getEncPV(void) { return pv; }
    vector<BDD> *getEncPVsucc(void) { return pv_succ; }
    BDD *getEncPV_E(void) { return pv_E; }
    BDD *getEncPVsucc_E(void) { return pv_succ_E; }
    BDD *getEncPVact_E(void) { return pv_act_E; }
    vector<BDD> *getEncPartTrans(void) { return partTrans; }
    BDD *getEncMonoTrans(void) { return monoTrans; }
    BDD getEncState(const RctSys::Atoms &atoms);
    BDD *getEncInitStates(void) { return initStates; }
    Cudd *getCuddMgr(void) { return cuddMgr; }
    unsigned int getTotalStateVars(void) { return totalStateVars; }
    BDD encAtom(std::string name) const {
        return encAtom(rs->getAtomID(name));
    }
    BDD encActStrAtom(std::string name) const;
    BDD getBDDtrue(void) const { return BDD_TRUE; }
    BDD getBDDfalse(void) const { return BDD_FALSE; }
};

#endif

