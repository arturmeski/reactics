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
  unsigned int cnt = 0;

  for (const auto &proc_ent : procEnt) {
    Process proc_id = proc_ent.first;

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

    for (unsigned int i = 0; i < entities_count; ++i) {

      assert(drs_flat_index < totalRctSysStateVars);
      assert(global_state_idx < totalStateVars);
      assert(proc_id < numberOfProc);
      assert(i < totalEntities);

      // Variables for each individual process/component
      (*pv_drs)[proc_id][i] = cuddMgr->bddVar(bdd_var_idx++);
      (*pv_drs_succ)[proc_id][i] = cuddMgr->bddVar(bdd_var_idx++);

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

  for (unsigned int i = 0; i < numberOfProc; ++i) {
    (*pv_proc_enab)[i] = cuddMgr->bddVar(bdd_var_idx++);
  }

  // ----------------------------------------------------------
  //                   Context Entities
  // ----------------------------------------------------------

  // // Actions/Contexts
  // pv_act = new BDDvec(totalActions);
  // pv_act_E = new BDD(BDD_TRUE);
  //
  // // TODO
  // // Actions need also per-process PV and flattened PV
  //
  // for (unsigned int i = 0; i < totalActions; ++i) {
  //   (*pv_act)[i] = cuddMgr->bddVar(bdd_var_idx++);
  //   *pv_act_E *= (*pv_act)[i];
  // }

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

BDD SymRS::encEntity_raw(Process proc_id, Entity entity, bool succ) const
{
  BDD r;

  assert(proc_id < numberOfProc);

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

  auto local_entity_id = getLocalCtxEntityIndex(proc_id, entity);

  return (*pv_proc_ctx)[proc_id][local_entity_id];
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

BDD SymRS::encStateActEntitiesConj(const Entities &entities)
{
  assert(0);
  BDD r = BDD_TRUE;
  /*
  for (const auto &entity : entities) {
    BDD state_act = encEntity(entity);
    int actEntity;

    // if entity is also an action entity, we include it in the encoding
    if ((actEntity = getMappedStateToActID(entity)) >= 0) {
      state_act += encActEntity(actEntity);
    }

    r *= state_act;
  }
  */

  return r;
}

BDD SymRS::encStateActEntitiesDisj(const Entities &entities)
{
  assert(0);
  BDD r = BDD_FALSE;
  /*
  for (const auto &entity : entities) {
    BDD state_act = encEntity(entity);
    int actEntity;

    // if entity is also an aciton entity, we include it in the encoding
    if ((actEntity = getMappedStateToActID(entity)) >= 0) {
      state_act += encActEntity(actEntity);
    }

    r += state_act;
  }
  */
  return r;
}

BDD SymRS::encActEntitiesConj(const Entities &entities)
{
  assert(0);
  BDD r = BDD_TRUE;
  /*
  for (const auto &entity : entities) {
    Entity actEntity = getMappedStateToActID(entity);
    r *= encActEntity(actEntity);
  }
  */
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
  assert(0);
  BDD c = context;

  for (unsigned int i = 0; i < totalActions; ++i) {
    if (!(*pv_act)[i] * context != cuddMgr->bddZero()) {
      c *= !(*pv_act)[i];
    }
  }

  return c;
}

std::string SymRS::decodedRctSysStateToStr(const BDD &state)
{
  assert(0);
  std::string s = "{ ";
  /*
  for (unsigned int i = 0; i < totalRctSysStateVars; ++i) {
    if (!(encEntity(i) * state).IsZero()) {
      s += rs->entityToStr(i) + " ";
    }
  }
  */
  s += "}";
  return s;
}

void SymRS::printDecodedRctSysStates(const BDD &states)
{
  assert(0);
  BDD unproc = states;

  while (!unproc.IsZero()) {
    BDD t = unproc.PickOneMinterm(*pv_rs);
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

void SymRS::encodeTransitions(void)
{
  VERB("Decomposing reactions");

  vector<DecompReactions> prod_conds(numberOfProc);

  for (auto proc_id = 0; proc_id < numberOfProc; ++proc_id) {
    prod_conds[proc_id] = getProductionConditions(proc_id);
  }

  VERB("Encoding reactions");

  if (opts->part_tr_rel) {
    VERB("Using partitioned transition relation encoding");
    FERROR("Partitioned transition relation is currently not supported");
  }
  else {
    VERB("Using monolithic transition relation encoding");
    monoTrans = new BDD(BDD_TRUE);
  }

  FERROR("WORK IN PROGRESS");
}

BDD SymRS::encNoContext(void)
{
  assert(0);
  return BDD_FALSE;
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

BDD SymRS::encActStrEntity(std::string name) const
{
  /*
  int id = getMappedStateToActID(rs->getEntityID(name));

  if (id < 0) {
    FERROR("Entity \"" << name << "\" not defined as context entity");
    return BDD_FALSE;
  }
  else {
    return encActEntity(getMappedStateToActID(rs->getEntityID(name)));
  }
  */
  return BDD_FALSE;
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

  while (bitCountMaxVal <= numStates) {
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
    // assert(0); // enc_ctx
    BDD enc_ctx = BDD_FALSE; //compContext(encActEntitiesConj(t.ctx));

    *tr_ca += enc_src * enc_ctx * enc_dst;
  }
}

/** EOF **/
