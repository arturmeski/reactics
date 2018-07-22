#ifndef RS_MC_HH
#define RS_MC_HH

#include "cudd.hh"
#include "rs.hh"
#include "symrs.hh"
#include "formrsctlk.hh"
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
    BDD *pv_ctx_E;
    BDDvec *pv_drs_E;
    BDD *reach;
    vector<BDD> *trp;
    BDD *trm;

    std::map<Process, BDD> ith_only_E;

    // Context Automaton
    bool using_ctx_aut;
    vector<BDD> *pv_ca;
    vector<BDD> *pv_ca_succ;
    BDD *pv_ca_E;
    BDD *pv_ca_succ_E;

    BDD *pv_proc_enab_E;

    unsigned int trp_size;
    unsigned int totalStateVars;

    /**
     * @brief Abstracts away (in-place!) the context automaton states
     */
    void dropCtxAutStatePart(BDD &states);

    BDD getSucc(const BDD &states);
    BDD getPreE(const BDD &states);
    BDD getPreEctx(const BDD &states, const BDD *contexts);
    BDD getStatesRSCTLK(const FormRSCTLK *form);
    BDD statesEG(const BDD &states);
    BDD statesEU(const BDD &statesA, const BDD &statesB);
    BDD statesEF(const BDD &states);
    BDD statesEGctx(const BDD *contexts, const BDD &states);
    BDD statesEUctx(const BDD *contexts, const BDD &statesA, const BDD &statesB);
    BDD statesEFctx(const BDD *contexts, const BDD &states);
    BDD statesNK(const BDD &states, Process proc_id);

    BDD getIthOnly(Process proc_id);

    void cleanup(void);

    void reorder(void);
    
  public:
    ModelChecker(SymRS *srs, Options *opts);

    void printReach(void);
    void printReachWithSucc(void);
    bool checkReach(const Entities testState);
    bool checkRSCTLK(FormRSCTLK *form);
    bool checkRSCTLKfull(FormRSCTLK *form);
    bool checkRSCTLKbmc(FormRSCTLK *form);
};

#endif
