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

  public:
    SymRS(RctSys *rs, Options *opts);

    BDDvec *getEncPV(void)
    {
      return pv;
    }
    BDDvec *getEncPVsucc(void)
    {
      return pv_succ;
    }
    BDD *getEncPV_E(void)
    {
      return pv_E;
    }
    BDD *getEncPVsucc_E(void)
    {
      return pv_succ_E;
    }
    BDD *getEncPVact_E(void)
    {
      return pv_act_E;
    }
    BDDvec *getEncPartTrans(void)
    {
      return partTrans;
    }
    BDD *getEncMonoTrans(void)
    {
      return monoTrans;
    }
    BDD *getEncInitStates(void)
    {
      return initStates;
    }
    Cudd *getCuddMgr(void)
    {
      return cuddMgr;
    }
    unsigned int getTotalStateVars(void)
    {
      return totalStateVars;
    }
    unsigned int getTotalRctSysStateVars(void)
    {
      return totalRctSysStateVars;
    }
    BDD encEntity(std::string proc_name, std::string entity_name) const
    {
      return encEntity(rs->getProcessID(proc_name), rs->getEntityID(entity_name));
    }
    BDD encActStrEntity(std::string name) const;
    BDD getBDDtrue(void) const
    {
      return BDD_TRUE;
    }
    BDD getBDDfalse(void) const
    {
      return BDD_FALSE;
    }

    /**
     * @brief Checks if context automaton is used
     *
     * @return True if CA is used
     */
    bool usingContextAutomaton(void)
    {
      return rs->ctx_aut != nullptr;
    }

    /**
     * @brief Encodes a context automaton's state
     *
     * @return Returns the encoded state
     */
    BDD encCtxAutState_raw(State state_id, bool succ) const;

    /**
     * @brief Encodes a context automaton's state (as predecessor/non-primed)
     *
     * @return Returns the encoded state
     */
    BDD encCtxAutState(State state_id) const
    {
      return encCtxAutState_raw(state_id, false);
    }

    /**
     * @brief Encodes a context automaton's state (as successor/primed)
     *
     * @return Returns the encoded state
     */
    BDD encCtxAutStateSucc(State state_id) const
    {
      return encCtxAutState_raw(state_id, true);
    }

    /**
     * @brief Encodes the initial state of context automaton
     *
     * @return Returns the encoded state(s)
     */
    BDD getEncCtxAutInitState(void);

    /**
     * @brief Getter for context automaton's state variables (predecessor/non-primed)
     *
     * @return Returns a vector of BDDs
     */
    BDDvec *getEncCtxAutPV(void)
    {
      return pv_ca;
    }

    /**
     * @brief Getter for context automaton's successor (primed) state variables
     *
     * @return Returns a vector of BDDs
     */
    BDDvec *getEncCtxAutPVsucc(void)
    {
      return pv_ca_succ;
    }

    /**
     * @brief Getter for context automaton's quantification BDD (for non-primed vars)
     *
     * @return Returns a BDD for quantification
     */
    BDD *getEncCtxAutPV_E(void)
    {
      return pv_ca_E;
    }

    /**
     * @brief Getter for context automaton's quantification BDD (for primed vars)
     *
     * @return Returns a BDD for quantification
     */
    BDD *getEncCtxAutPVsucc_E(void)
    {
      return pv_ca_succ_E;
    }

    /**
     * @brief Encodes the monolithic transition relation
     */
    void encodeCtxAutTrans(void);

    /**
     * @brief Getter for context automaton's transition relation
     *
     * @return Returns a BDD encoding the transition relation
     */
    BDD *getEncCtxAutTrans(void)
    {
      return tr_ca;
    }

  private:

    RctSys *rs;
    Cudd *cuddMgr;
    Options *opts;

    BDD *initStates;              /*!< BDD with initial states encoded */

    BDDvec *pv;                   /*!< PVs for the global state (all the variables, flat) */
    BDDvec *pv_succ;
    BDD *pv_E;
    BDD *pv_succ_E;

    BDDvec *pv_proc_enab;         /*!< Variables indicating if a process is enabled */

    BDDvec *pv_rs; // remove
    BDDvec *pv_rs_succ; // remove

    BDD *pv_rs_E; // remove
    BDD *pv_rs_succ_E; // remove

    vector<BDDvec> *pv_drs;       /*!< PVs for the product part of state
                                       (per DRS process) */
    vector<BDDvec> *pv_drs_succ;  /*!< PVs for the product (successor)
                                       part of state (per DRS process) */

    BDDvec *pv_drs_flat;          /*!< PVs for the DRS product part of state (flat) */
    BDDvec *pv_drs_flat_succ;     /*!< PVs for the DRS product (successor) part of state (flat) */

    BDD *pv_drs_flat_E;
    BDD *pv_drs_flat_succ_E;

    vector<DecompReactions> prod_conds; /*!< Production conditions (per process and per entity) */

    BDDvec *partTrans;
    BDD *monoTrans;

    // Context automaton
    BDDvec *pv_ca;
    BDDvec *pv_ca_succ;
    BDD *pv_ca_E;
    BDD *pv_ca_succ_E;
    BDD *tr_ca;

    BDDvec *pv_ctx;               /*!< Flat */
    BDD *pv_ctx_E;
    vector<BDDvec> *pv_proc_ctx;
    BDDvec *pv_proc_ctx_E;

    // TODO: remove
    BDDvec *pv_act;
    BDD *pv_act_E;

    unsigned int totalEntities;
    unsigned int numberOfProc;         /*!< The number of DRS processes */
    unsigned int totalStateVars;
    unsigned int totalRctSysStateVars; /*!< Total number of different entities produced by reactions */
    unsigned int totalCtxEntities;     /*!< Total number of different (process,context) entities used */
    unsigned int totalActions;
    unsigned int totalCtxAutStateVars;

    EntitiesForProc usedProducts;     /*!< Entities used in products (per process) */
    EntitiesForProc usedCtxEntities;  /*!< Entities used in context sets (per process) */

    LocalIndicesForProcEntities prod_ent_local_idx; /*!< Local indices for each entity (per process): product entities */
    LocalIndicesForProcEntities ctx_ent_local_idx;  /*!< Local indices for each entity (per process): context entities */

    size_t getTotalProductVariables(void);
    size_t getTotalCtxEntitiesVariables(void);

    unsigned int getLocalProductEntityIndex(Process proc_id, Entity entity) const;
    unsigned int getLocalCtxEntityIndex(Process proc_id, Entity entity) const;

    BDD encEntity_raw(Process proc_id, Entity entity, bool succ) const;
    BDD encEntity(Process proc_id, Entity entity) const
    {
      return encEntity_raw(proc_id, entity, false);
    }
    BDD encEntitySucc(Process proc_id, Entity entity) const
    {
      return encEntity_raw(proc_id, entity, true);
    }

    BDD encCtxEntity(Process proc_id, Entity entity) const;

    bool productEntityExists(Process proc_id, Entity entity) const;
    bool ctxEntityExists(Process proc_id, Entity entity) const;

    BDD encProcEnabled(Process proc_id) const
    {
      return (*pv_proc_enab)[proc_id];
    }

    BDD encEntitiesConj_raw(Process proc_id, const Entities &entities, bool succ);
    BDD encEntitiesConj(Process proc_id, const Entities &entities)
    {
      return encEntitiesConj_raw(proc_id, entities, false);
    }
    BDD encEntitiesConjSucc(Process proc_id, const Entities &entities)
    {
      return encEntitiesConj_raw(proc_id, entities, true);
    }

    // ---- TODO below:

    BDD encEntitiesDisj_raw(Process proc_id, const Entities &entities, bool succ);
    BDD encEntitiesDisj(Process proc_id, const Entities &entities)
    {
      return encEntitiesDisj_raw(proc_id, entities, false);
    }
    BDD encEntitiesDisjSucc(Process proc_id, const Entities &entities)
    {
      return encEntitiesDisj_raw(proc_id, entities, true);
    }

    BDD encEntityCondition(Process proc_id, Entity entity_id);

    BDD encContext(const EntitiesForProc &proc_entities);

    /**
     * @brief Complements an encoding of a given state by negating all the variables that are not set to true
     *
     * @return Returns the encoded state
     */
    BDD compState(const BDD &state) const;

    BDD compContext(const BDD &context) const;

    std::string decodedRctSysStateToStr(const BDD &state);
    void printDecodedRctSysStates(const BDD &states);

    BDD encNoContext(void);

    DecompReactions getProductionConditions(Process proc_id);

    void initBDDvars(void);

    BDD encEnabledness(Process proc_id, Entity entity_id);
    BDD encEntitySameSuccessor(Process proc_id, Entity entity_id);
    BDD encEntityProduction(Process proc_id, Entity entity_id);

    void encodeTransitions(void);
    void encodeInitStates(void);
    void encodeInitStatesForCtxAut(void);
    LocalIndicesForProcEntities buildLocalEntitiesMap(const EntitiesForProc &procEnt);
    void mapProcEntities(void);
    void encode(void);

    size_t getCtxAutStateEncodingSize(void);

};

#endif

/** EOF **/
