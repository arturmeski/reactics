/*
    Copyright (c) 2012-2018
    Artur Meski <meski@ipipan.waw.pl>
*/

#include "symrs.hh"


SymRS::SymRS(RctSys *rs, Options *opts)
{
  this->rs = rs;
  this->opts = opts;

  mapProcEntities();

  totalEntities = rs->getEntitiesSize();

  // TODO: remove
  totalActions = 0;

  totalRctSysStateVars = getTotalProductVariables();
  totalCtxEntities = getTotalCtxEntitiesVariables();

  totalCtxAutStateVars = getCtxAutStateEncodingSize();
  totalStateVars = totalRctSysStateVars + totalCtxAutStateVars;
  numberOfProc = rs->getNumberOfProcesses();

  partTrans = nullptr;
  monoTrans = nullptr;

  pv_ca = nullptr;
  pv_ca_succ = nullptr;
  tr_ca = nullptr;

  encode();
}

void SymRS::encode(void)
{
  VERB("Encoding...");

  if (opts->measure) {
    opts->enc_time = cpuTime();
    opts->enc_mem = memUsed();
  }

  initBDDvars();

  if (usingContextAutomaton()) {
    encodeCtxAutTrans();
  }
  else {
    VERB_LN(3, "Not using context automata, not encoding TR for CA")
  }

  encodeTransitions();
  encodeInitStates();

  if (opts->measure) {
    opts->enc_time = cpuTime() - opts->enc_time;
    opts->enc_mem = memUsed() - opts->enc_mem;
  }

  VERB("Encoding done");
}

LocalIndicesForProcEntities SymRS::buildLocalEntitiesMap(
  const EntitiesForProc &procEnt)
{
  LocalIndicesForProcEntities ent_map;

  for (const auto &proc_ent : procEnt) {
    Process proc_id = proc_ent.first;

    unsigned int cnt = 0;

    for (const auto &e : proc_ent.second) {
      ent_map[proc_id][e] = cnt++;
    }
  }

  return ent_map;
}

void SymRS::initBDDvars(void)
{
  VERB("Initialising CUDD");

  cuddMgr = new Cudd(0, 0);

  VERB("Preparing BDD variables");

  // used for bddVar
  unsigned int bdd_var_idx = 0;

  // used for pv, pv_succ
  unsigned int global_state_idx = 0;

  // ----------------------------------------------------------
  //                        Global state
  // ----------------------------------------------------------
  //
  //  Variables for reaction system with CA (if used)
  //

  pv = new BDDvec(totalStateVars);
  pv_succ = new BDDvec(totalStateVars);
  pv_E = new BDD(BDD_TRUE);
  pv_succ_E = new BDD(BDD_TRUE);

  // ----------------------------------------------------------
  //                       Distributed RS
  // ----------------------------------------------------------

  pv_drs = new vector<BDDvec>(numberOfProc);
  pv_drs_succ = new vector<BDDvec>(numberOfProc);

  pv_drs_flat = new BDDvec(totalRctSysStateVars);
  pv_drs_flat_succ = new BDDvec(totalRctSysStateVars);

  pv_drs_E = new BDDvec(numberOfProc);

  pv_drs_flat_E = new BDD(BDD_TRUE);
  pv_drs_flat_succ_E = new BDD(BDD_TRUE);

  VERB_LN(2, "DRS processing");

  unsigned int drs_flat_index = 0;

  for (const auto &proc_ent : usedProducts) {

    auto proc_id = proc_ent.first;
    auto entities_count = proc_ent.second.size();

    //
    // The order of entities and their correspondence to the
    // correct entities in pv (global) does not matter here.
    //
    // The correspondence is established in the methods
    // returning BDD variables (encoding) of the individual
    // enties.
    //
    // We only need to make sure we have the correct number of
    // variables that are going to be used in the encoding.
    //
    // For efficiency, we do not introduce BDD variables for
    // entites that are never produced in a given local component.
    // Instead, we only select those that are. We apply the same
    // strategy to product entities and context entities.
    //

    // First, we need to adjust the sizes of all the nested vectors
    (*pv_drs)[proc_id].resize(entities_count);
    (*pv_drs_succ)[proc_id].resize(entities_count);

    (*pv_drs_E)[proc_id] = BDD_TRUE;

    for (unsigned int i = 0; i < entities_count; ++i) {

      assert(drs_flat_index < totalRctSysStateVars);
      assert(global_state_idx < totalStateVars);
      assert(proc_id < numberOfProc);
      assert(i < totalEntities);

      // Variables for each individual process/component
      (*pv_drs)[proc_id][i] = cuddMgr->bddVar(bdd_var_idx++);
      (*pv_drs_succ)[proc_id][i] = cuddMgr->bddVar(bdd_var_idx++);

      // Quantification (per proc)
      (*pv_drs_E)[proc_id] *= (*pv_drs)[proc_id][i];

      // The DRS part of the system (flattened): these vars do not include CA
      (*pv_drs_flat)[drs_flat_index] = (*pv_drs)[proc_id][i];
      (*pv_drs_flat_succ)[drs_flat_index] = (*pv_drs_succ)[proc_id][i];

      *pv_drs_flat_E *= (*pv_drs_flat)[drs_flat_index];
      *pv_drs_flat_succ_E *= (*pv_drs_flat_succ)[drs_flat_index];

      // Variables used for the global states
      (*pv)[global_state_idx] = (*pv_drs)[proc_id][i];
      (*pv_succ)[global_state_idx] = (*pv_drs_succ)[proc_id][i];

      *pv_E *= (*pv)[global_state_idx];
      *pv_succ_E *= (*pv_succ)[global_state_idx];

      ++drs_flat_index;
      ++global_state_idx;
    }
  }

  // ----------------------------------------------------------
  //                      Context Automaton
  // ----------------------------------------------------------

  if (usingContextAutomaton()) {
    VERB_LN(2, "Context automaton variables");

    pv_ca = new BDDvec(totalCtxAutStateVars);
    pv_ca_succ = new BDDvec(totalCtxAutStateVars);
    pv_ca_E = new BDD(BDD_TRUE);
    pv_ca_succ_E = new BDD(BDD_TRUE);

    for (unsigned int i = 0; i < totalCtxAutStateVars; ++i) {
      (*pv_ca)[i] = cuddMgr->bddVar(bdd_var_idx++);
      (*pv_ca_succ)[i] = cuddMgr->bddVar(bdd_var_idx++);
      *pv_ca_E *= (*pv_ca)[i];
      *pv_ca_succ_E *= (*pv_ca_succ)[i];

      (*pv)[global_state_idx] = (*pv_ca)[i];
      (*pv_succ)[global_state_idx] = (*pv_ca_succ)[i];
      ++global_state_idx;
    }
  }

  // ----------------------------------------------------------
  //                Enabledness of processes
  // ----------------------------------------------------------
  //
  //  These variables indicate which process is
  //  allowed to perform action
  //
  VERB_LN(2, "Variables for process enabledness/activity");

  pv_proc_enab = new BDDvec(numberOfProc);
  pv_proc_enab_E = new BDD(BDD_TRUE);

  for (unsigned int i = 0; i < numberOfProc; ++i) {
    auto bdd_var = cuddMgr->bddVar(bdd_var_idx++);
    (*pv_proc_enab)[i] = bdd_var;
    *pv_proc_enab_E *= bdd_var;
  }

  // ----------------------------------------------------------
  //                   Context Entities
  // ----------------------------------------------------------

  VERB_LN(2, "Variables for context entities");

  pv_ctx = new BDDvec(totalCtxEntities);
  pv_ctx_E = new BDD(BDD_TRUE);
  pv_proc_ctx = new vector<BDDvec>(numberOfProc);
  pv_proc_ctx_E = new BDDvec(numberOfProc);

  unsigned int flat_ctx_index = 0;

  for (const auto &proc_ent : usedCtxEntities) {

    auto proc_id = proc_ent.first;
    auto entities_count = proc_ent.second.size();

    assert(entities_count < totalEntities);

    // adjust the size of the nested vector before we use an index
    (*pv_proc_ctx)[proc_id].resize(entities_count);

    (*pv_proc_ctx_E)[proc_id] = BDD_TRUE;

    for (unsigned int i = 0; i < entities_count; ++i) {

      assert(flat_ctx_index < totalCtxEntities);
      assert(proc_id < numberOfProc);

      (*pv_proc_ctx)[proc_id][i] = cuddMgr->bddVar(bdd_var_idx++);
      (*pv_proc_ctx_E)[proc_id] *= (*pv_proc_ctx)[proc_id][i];

      (*pv_ctx)[flat_ctx_index] = (*pv_proc_ctx)[proc_id][i];
      *pv_ctx_E *= (*pv_ctx)[flat_ctx_index];

      ++flat_ctx_index;
    }

  }

  if (usingContextAutomaton()) {

    VERB_LN(2, "Updating quantification BDDs with context automaton")

    *pv_E *= *pv_ca_E;
    *pv_succ_E *= *pv_ca_succ_E;
  }

  VERB("All BDD variables ready");
}

size_t SymRS::getTotalProductVariables(void)
{
  size_t total = 0;

  for (const auto &it : usedProducts) {
    total += it.second.size();
  }

  return total;
}

size_t SymRS::getTotalCtxEntitiesVariables(void)
{
  size_t total = 0;

  for (const auto &it : usedCtxEntities) {
    total += it.second.size();
  }

  return total;
}

void SymRS::mapProcEntities(void)
{
  //
  // Reactions
  //
  for (const auto &proc_rcts : rs->proc_reactions) {
    Process proc_id = proc_rcts.first;

    for (const auto &rct : proc_rcts.second) {

      // collect entities that can be produced
      // locally by the process with proc_id

      SET_ADD(usedProducts[proc_id], rct.prod);
    }
  }

  prod_ent_local_idx = buildLocalEntitiesMap(usedProducts);

  //
  // Context automaton
  //
  for (const auto &tr : rs->ctx_aut->transitions) {
    for (const auto &proc_ctx : tr.ctx) {
      Process proc_id = proc_ctx.first;
      SET_ADD(usedCtxEntities[proc_id], proc_ctx.second);
    }
  }

  ctx_ent_local_idx = buildLocalEntitiesMap(usedCtxEntities);

  if (opts->verbose > 9) {
    cout << "Used product entities:" << endl;
    cout << rs->procEntitiesToStr(usedProducts) << endl;

    cout << "Used context entities:" << endl;
    cout << rs->procEntitiesToStr(usedCtxEntities) << endl;
  }
}

unsigned int SymRS::getLocalProductEntityIndex(Process proc_id, Entity entity) const
{
  assert(productEntityExists(proc_id, entity));
  auto idx = prod_ent_local_idx.at(proc_id).at(entity);
  assert(idx < prod_ent_local_idx.at(proc_id).size());
  return idx;
}
unsigned int SymRS::getLocalCtxEntityIndex(Process proc_id, Entity entity) const
{
  assert(ctxEntityExists(proc_id, entity));
  auto idx = ctx_ent_local_idx.at(proc_id).at(entity);
  assert(idx < ctx_ent_local_idx.at(proc_id).size());
  return idx;
}

BDD SymRS::encEntity_raw(Process proc_id, Entity entity, bool succ) const
{
  BDD r;

  assert(proc_id < numberOfProc);
  assert(productEntityExists(proc_id, entity));

  auto local_entity_id = getLocalProductEntityIndex(proc_id, entity);

  if (succ) {
    r = (*pv_drs_succ)[proc_id][local_entity_id];
  }
  else {
    r = (*pv_drs)[proc_id][local_entity_id];
  }

  return r;
}

BDD SymRS::encCtxEntity(Process proc_id, Entity entity) const
{
  assert(entity < totalEntities);
  assert(proc_id < numberOfProc);
  assert(ctxEntityExists(proc_id, entity));

  auto local_entity_id = getLocalCtxEntityIndex(proc_id, entity);

  return (*pv_proc_ctx)[proc_id][local_entity_id];
}

bool SymRS::productEntityExists(Process proc_id, Entity entity) const
{
  if (prod_ent_local_idx.count(proc_id) == 0) {
    return false;
  }
  else {
    if (prod_ent_local_idx.at(proc_id).count(entity) == 1) {
      return true;
    }
  }

  return false;
}

bool SymRS::ctxEntityExists(Process proc_id, Entity entity) const
{
  if (ctx_ent_local_idx.count(proc_id) == 0) {
    return false;
  }
  else {
    if (ctx_ent_local_idx.at(proc_id).count(entity) == 1) {
      return true;
    }
  }

  return false;
}

bool SymRS::processUsesEntity(Process proc_id, Entity entity_id) const
{
  if (productEntityExists(proc_id, entity_id) || ctxEntityExists(proc_id, entity_id)) {
    return true;
  }

  return false;
}

BDD SymRS::encEntitiesConj_raw(Process proc_id, const Entities &entities, bool succ)
{
  BDD r = BDD_TRUE;

  for (const auto &entity : entities) {
    if (succ) {
      r *= encEntitySucc(proc_id, entity);
    }
    else {
      r *= encEntity(proc_id, entity);
    }
  }

  return r;
}

BDD SymRS::encEntitiesDisj_raw(Process proc_id, const Entities &entities, bool succ)
{
  BDD r = BDD_FALSE;

  for (const auto &entity : entities) {
    if (succ) {
      r += encEntitySucc(proc_id, entity);
    }
    else {
      r += encEntity(proc_id, entity);
    }
  }

  return r;
}

BDD SymRS::encEntityCondition(Process proc_id, Entity entity_id)
{
  //
  // Here we encode an entity-based condition which uses
  // the entity appearing as a product or a context entity.
  //
  BDD r = BDD_FALSE;

  if (productEntityExists(proc_id, entity_id)) {
    r += encEntity(proc_id, entity_id);
  }

  if (ctxEntityExists(proc_id, entity_id)) {
    r += encCtxEntity(proc_id, entity_id);
  }

  // pointless call to this function -- we should have prevented it:
  assert(r != BDD_FALSE);

  return r;
}

BDD SymRS::encContext(const EntitiesForProc &proc_entities)
{
  BDD r = BDD_TRUE;

  for (const auto &pe : proc_entities) {
    auto proc_id = pe.first;
    auto entities = pe.second;

    for (const auto &entity : entities) {
      r *= encCtxEntity(proc_id, entity);
    }

    r *= encProcEnabled(proc_id);
  }

  return r;
}

BDD SymRS::compState(const BDD &state) const
{
  assert(0);
  BDD s = state;

  for (unsigned int i = 0; i < totalRctSysStateVars; ++i) {
    if (!(*pv)[i] * state != cuddMgr->bddZero()) {
      s *= !(*pv)[i];
    }
  }

  return s;
}

BDD SymRS::compContext(const BDD &context) const
{
  BDD c = context;

  for (const auto &var : *pv_ctx) {
    if (!var * context != cuddMgr->bddZero()) {
      c *= !var;
    }
  }

  for (const auto &var : *pv_proc_enab) {
    if (!var * context != cuddMgr->bddZero()) {
      c *= !var;
    }
  }

  return c;
}

std::string SymRS::decodedRctSysStateToStr(const BDD &state)
{
  std::string s = "{ ";

  for (const auto &proc_entities : usedProducts) {

    auto proc_id = proc_entities.first;
    auto entities = proc_entities.second;
    s += rs->getProcessName(proc_id) + "={ ";

    for (const auto &entity : entities) {
      if (!(encEntity(proc_id, entity) * state).IsZero()) {
        s += rs->entityToStr(entity) + " ";
      }
    }

    s += "} ";
  }

  s += "}";
  return s;
}

void SymRS::printDecodedRctSysStates(const BDD &states)
{
  BDD unproc = states;

  while (!unproc.IsZero()) {
    BDD t = unproc.PickOneMinterm(*pv_drs_flat);
    cout << decodedRctSysStateToStr(t) << endl;

    if (opts->verbose > 9) {
      BDD_PRINT(t);
      cout << endl;
    }

    unproc -= t;
  }
}

DecompReactions SymRS::getProductionConditions(Process proc_id)
{
  DecompReactions dr;

  for (const auto &rct : rs->proc_reactions[proc_id]) {
    ReactionCond cond;
    cond.rctt = rct.rctt;
    cond.inhib = rct.inhib;

    for (const auto &prod : rct.prod) {
      dr[prod].push_back(cond);
    }
  }

  return dr;
}

BDD SymRS::encEnabledness(Process prod_proc_id, Entity entity_id)
{
  assert(prod_conds.size() > prod_proc_id);

  BDD enab = BDD_FALSE;

  auto production_conditions = prod_conds[prod_proc_id][entity_id];

  VERB_LN(5, "| Produce " << rs->getEntityName(entity_id) << " in " << rs->getProcessName(prod_proc_id) << ":");

  // Iterate through production conditions for the entity (entity_id) that
  // belongs to the process prod_proc_id which contain:
  //  - reactants
  //  - inhibitors
  //
  // Here we are building an alternative for the enab BDD,
  // for all the possible production conditions
  //
  for (const auto &cond : production_conditions) {

    // Take all the reactants... (conjuntion)
    BDD reactants = BDD_TRUE;

    for (const auto &reactant : cond.rctt) {

      // Disjunction for all the processes
      BDD proc_reactants = BDD_FALSE;

      if (ctxEntityExists(prod_proc_id, reactant)) {
        proc_reactants += encCtxEntity(prod_proc_id, reactant);
      }

      for (unsigned int proc_id = 0; proc_id < numberOfProc; ++proc_id) {
        if (productEntityExists(proc_id, reactant)) {

          proc_reactants += encProcEnabled(proc_id) * encEntity(proc_id, reactant);

          VERB_LN(5, "| - if process " << rs->getProcessName(proc_id) << " is enabled and has " << rs->getEntityName(reactant));

        }
      } // END FOR: prod_id

      reactants *= proc_reactants;
    } // END FOR: reactant


    // Take all the inhibitors... (conjunction)
    BDD inhibitors = BDD_TRUE;

    for (const auto &inhibitor : cond.inhib) {

      // Conjunction for all the processes
      BDD proc_inhibitors = BDD_TRUE;

      if (ctxEntityExists(prod_proc_id, inhibitor)) {
        proc_inhibitors *= !encCtxEntity(prod_proc_id, inhibitor);
      }

      for (unsigned int proc_id = 0; proc_id < numberOfProc; ++proc_id) {
        if (productEntityExists(proc_id, inhibitor)) {
          proc_inhibitors *= !encEntity(proc_id, inhibitor) + !encProcEnabled(proc_id);
        }
      }

      inhibitors *= proc_inhibitors;

    }

    enab += reactants * inhibitors;

  } // END FOR: cond

  reorder();

  return enab;
}

// BDD SymRS::encEnabledness(Process prod_proc_id, Entity entity_id)
// {
//   assert(prod_conds.size() > prod_proc_id);

//   BDD enab = BDD_FALSE;

//   auto production_conditions = prod_conds[prod_proc_id][entity_id];

//   VERB_LN(5, "| Produce " << rs->getEntityName(entity_id) << " in " << rs->getProcessName(prod_proc_id) << ":");

//   for (const auto &cond : production_conditions) {

//     BDD reactants = BDD_TRUE;
//     BDD inhibitors = BDD_TRUE;

//     for (const auto &reactant : cond.rctt) {
//       BDD proc_reactants = BDD_FALSE;

//       for (unsigned int proc_id = 0; proc_id < numberOfProc; ++proc_id) {
//         if (processUsesEntity(proc_id, reactant)) {
//           proc_reactants += encProcEnabled(proc_id) * encEntityCondition(proc_id, reactant);

//           VERB_LN(5, "| - if process " << rs->getProcessName(proc_id) << " is enabled and has " << rs->getEntityName(reactant));

//         }
//       } // END FOR: prod_id

//       reactants *= proc_reactants;
//     } // END FOR: reactant

//     // For inhibitors, we take all the processes first and then we iterate over the inhibitors
//     for (unsigned int proc_id = 0; proc_id < numberOfProc; ++proc_id) {
//       BDD proc_inhibitors = BDD_TRUE;

//       for (const auto &inhibitor : cond.inhib) {
//         if (processUsesEntity(proc_id, inhibitor)) {
//           proc_inhibitors *= !encEntityCondition(proc_id, inhibitor);
//         }
//       }

//       if (proc_inhibitors != BDD_TRUE) { // just an optimisation
//         proc_inhibitors += !encProcEnabled(proc_id);
//         inhibitors *= proc_inhibitors;
//       }
//     }

//     enab += reactants * inhibitors;

//   } // END FOR: cond

//   if (opts->reorder_trans) {
//     VERB_L2("Reordering");
//     Cudd_ReduceHeap(cuddMgr->getManager(), CUDD_REORDER_SIFT, 10000);
//   }

//   return enab;
// }


BDD SymRS::encEntitySameSuccessor(Process proc_id, Entity entity_id)
{
  return BDD_IFF(encEntity(proc_id, entity_id), encEntitySucc(proc_id, entity_id));
}

BDD SymRS::encEntityProduction(Process proc_id, Entity entity_id)
{
  BDD enabled = encEnabledness(proc_id, entity_id);

  BDD when_produced = enabled * encEntitySucc(proc_id, entity_id);
  BDD when_not_produced = !enabled * !encEntitySucc(proc_id, entity_id);

  BDD proc_enabled = encProcEnabled(proc_id) * (when_produced + when_not_produced);
  BDD proc_disabled = !encProcEnabled(proc_id) * encEntitySameSuccessor(proc_id, entity_id);

  BDD result = proc_enabled + proc_disabled;

  return result;
}

void SymRS::encodeTransitions(void)
{
  VERB("Decomposing reactions");

  prod_conds.resize(numberOfProc);

  for (auto proc_id = 0; proc_id < numberOfProc; ++proc_id) {
    prod_conds[proc_id] = getProductionConditions(proc_id);
  }

  VERB("Encoding reactions");

  if (opts->part_tr_rel) {
    VERB("Using partitioned transition relation encoding");

    if (usingContextAutomaton()) {
      partTrans = new BDDvec(numberOfProc+1);
    }
    else {
      partTrans = new BDDvec(numberOfProc);
    }

  }
  else {

    VERB("Using monolithic transition relation encoding");
    monoTrans = new BDD(BDD_TRUE);

  }

  VERB_LN(3, "Entity production encoding for all the processes and their products");

  if (opts->part_tr_rel)
  {

    for (const auto &proc_products : usedProducts) {
      auto proc_id = proc_products.first;
      auto products = proc_products.second;

      (*partTrans)[proc_id] = BDD_TRUE;

      for (const auto &prod : products) {
        (*partTrans)[proc_id] *= encEntityProduction(proc_id, prod);
      }
    }


  }
  else {

    for (const auto &proc_products : usedProducts) {
      auto proc_id = proc_products.first;
      auto products = proc_products.second;

      for (const auto &prod : products) {
        *monoTrans *= encEntityProduction(proc_id, prod);
      }
    }

  }

  VERB("Reactions ready");

  if (usingContextAutomaton()) {
    VERB("Augmenting transition relation encoding with the transition relation for context automaton");

    if (opts->part_tr_rel) {  
      auto last_index = numberOfProc;
      (*partTrans)[last_index] = *tr_ca;
    }
    else {
      assert(tr_ca != nullptr);
      *monoTrans *= *tr_ca;
    }
  }
}

void SymRS::encodeInitStates(void)
{
  if (usingContextAutomaton()) {
    VERB("Encoding initial states (using context automaton)");
    encodeInitStatesForCtxAut();
  }
  else {
    FERROR("Context automaton required");
  }

  VERB("Initial states encoded");
}

void SymRS::encodeInitStatesForCtxAut(void)
{
  initStates = new BDD(BDD_TRUE);

  for (unsigned int i = 0; i < totalRctSysStateVars; ++i) {
    *initStates *= !(*pv)[i];
  }

  *initStates *= getEncCtxAutInitState();
}

BDD SymRS::encActStrEntity(std::string proc_name, std::string entity_name) const
{
  auto enc_entity = encCtxEntity(rs->getProcessID(proc_name), rs->getEntityID(entity_name));
  return enc_entity;
}

size_t SymRS::getCtxAutStateEncodingSize(void)
{
  if (!usingContextAutomaton()) {
    return 0;
  }

  assert(rs->ctx_aut != nullptr);

  size_t bitCount = 0;
  size_t bitCountMaxVal = 1;
  size_t numStates = rs->ctx_aut->statesCount();

  while (bitCountMaxVal < numStates) {
    bitCount++;
    bitCountMaxVal *= 2;
  }

  VERB_LN(3, "Bits required for CA: " << bitCount);
  return bitCount;
}

BDD SymRS::encCtxAutState_raw(State state_id, bool succ) const
{
  // select appropriate BDD vector
  BDDvec *enc_vec;

  if (succ) {
    enc_vec = pv_ca_succ;
  }
  else {
    enc_vec = pv_ca;
  }

  assert(enc_vec != nullptr);

  BDD r = BDD_TRUE;
  State val = state_id;

  for (unsigned int i = 0; i < totalCtxAutStateVars; ++i) {
    if (val != 0) {
      if (val % 2 == 1) {
        r *= (*enc_vec)[i];
      }
      else {
        r *= !(*enc_vec)[i];
      }

      val /= 2;
    }
    else {
      r *= !(*enc_vec)[i];
    }
  }

  return r;
}

BDD SymRS::getEncCtxAutInitState(void)
{
  VERB_LN(2, "Encoding context automaton's initial state");

  State state = rs->ctx_aut->getInitState();

  return encCtxAutState(state);
}

void SymRS::encodeCtxAutTrans(void)
{
  VERB_LN(2, "Encoding context automaton's transition relation");

  if (tr_ca != nullptr) {
    VERB_LN(1, "Encoding for context automaton already present, not replacing")
    return;
  }

  tr_ca = new BDD(BDD_FALSE);

  for (auto &t : rs->ctx_aut->transitions) {
    VERB_LN(2, "Encoding CA transition " << rs->ctx_aut->getStateName(t.src_state)
            << " -> " << rs->ctx_aut->getStateName(t.dst_state));
    BDD enc_src = encCtxAutState(t.src_state);
    BDD enc_dst = encCtxAutStateSucc(t.dst_state);
    BDD enc_ctx = compContext(encContext(t.ctx));

    BDD new_trans = enc_src * enc_ctx * enc_dst;

    *tr_ca += new_trans;
  }
}


void SymRS::reorder(void)
{
  if (opts->reorder_trans) {
    VERB_L2("Reordering START");
    // Cudd_ReduceHeap(cuddMgr->getManager(), CUDD_REORDER_SIFT, 10000);
    cuddMgr->ReduceHeap(CUDD_REORDER_GROUP_SIFT);
    VERB_L2("Reordering DONE");
  }
}

/** EOF **/
