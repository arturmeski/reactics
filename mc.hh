#ifndef RS_MC_HH
#define RS_MC_HH

#include "cudd.hh"
#include "rs.hh"
#include "symrs.hh"
#include "formrsctl.hh"
#include "macro.hh"
#include "bdd_macro.hh"
#include "options.hh"
#include "memtime.hh"

using std::cout;
using std::cerr;
using std::endl;
using std::flush;

class ModelChecker
{
    SymRS *srs;
    Options *opts;
    Cudd *cuddMgr;
    BDD *initStates; 
    vector<BDD> *pv;
    vector<BDD> *pv_succ;
    BDD *pv_E;
    BDD *pv_succ_E;
    BDD *pv_act_E;
    BDD *reach;
    vector<BDD> *trp;
    BDD *trm;
    unsigned int trp_size;
    unsigned int totalStateVars;

    BDD zeroFill(const BDD &state);
    BDD getSucc(const BDD &states);
    BDD getPreE(const BDD &states);
    BDD getPreEctx(const BDD &states, const BDD *contexts);
    BDD getStatesRSCTL(const FormRSCTL *form);
    BDD statesEG(const BDD &states);
    BDD statesEU(const BDD &statesA, const BDD &statesB);
    BDD statesEF(const BDD &states);
    BDD statesEGctx(const BDD *contexts, const BDD &states);
    BDD statesEUctx(const BDD *contexts, const BDD &statesA, const BDD &statesB);
    BDD statesEFctx(const BDD *contexts, const BDD &states);
    void cleanup(void);

public:
    ModelChecker(SymRS *srs, Options *opts)
    {
        this->srs = srs;
        this->opts = opts;
        cuddMgr = srs->getCuddMgr();
        initStates = srs->getEncInitStates();
        totalStateVars = srs->getTotalStateVars();
        pv = srs->getEncPV();
        pv_succ = srs->getEncPVsucc();
        pv_E = srs->getEncPV_E();
        pv_succ_E = srs->getEncPVsucc_E();
        pv_act_E = srs->getEncPVact_E();
        trp = srs->getEncPartTrans();
        if (trp == nullptr) trp_size = 0;
        else trp_size = trp->size();
        trm = srs->getEncMonoTrans();
        reach = nullptr;
    }

    void printReach(void);
    void printReachWithSucc(void);
    bool checkReach(const Entities testState);
    bool checkRSCTL(FormRSCTL *form);
    bool checkRSCTLfull(FormRSCTL *form);
    bool checkRSCTLbmc(FormRSCTL *form);
};

#endif
