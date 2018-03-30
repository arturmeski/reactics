/*
    Copyright (c) 2012-2018
    Artur Meski <meski@ipipan.waw.pl>
*/

#include "symrs.hh"


SymRS::SymRS(RctSys *rs, Options *opts)
{
  this->rs = rs;
  this->opts = opts;
  totalRctSysStateVars = rs->getEntitiesSize();
  totalReactions = rs->getReactionsSize();
  totalActions = rs->getActionsSize();

  totalCtxAutStateVars = getCtxAutStateEncodingSize();

  totalStateVars = totalRctSysStateVars + totalCtxAutStateVars;

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

  mapStateToAct();

  mapProcEntities();

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
  // cout << rs->procEntitiesToStr(usedCtxEntities) << endl;
}

BDD SymRS::encEntity_raw(Entity entity, bool succ) const
{
  BDD r;

  if (succ) {
    r = (*pv_succ)[entity];
  }
  else {
    r = (*pv)[entity];
  }

  return r;
}

BDD SymRS::encEntitiesConj_raw(const Entities &entities, bool succ)
{
  BDD r = BDD_TRUE;

  for (const auto &entity : entities) {
    if (succ) {
      r *= encEntitySucc(entity);
    }
    else {
      r *= encEntity(entity);
    }
  }

  return r;
}

BDD SymRS::encEntitiesDisj_raw(const Entities &entities, bool succ)
{
  BDD r = BDD_FALSE;

  for (const auto &entity : entities) {
    if (succ) {
      r += encEntitySucc(entity);
    }
    else {
      r += encEntity(entity);
    }
  }

  return r;
}

BDD SymRS::encStateActEntitiesConj(const Entities &entities)
{
  BDD r = BDD_TRUE;

  for (const auto &entity : entities) {
    BDD state_act = encEntity(entity);
    int actEntity;

    // if entity is also an action entity, we include it in the encoding
    if ((actEntity = getMappedStateToActID(entity)) >= 0) {
      state_act += encActEntity(actEntity);
    }

    r *= state_act;
  }

  return r;
}

BDD SymRS::encStateActEntitiesDisj(const Entities &entities)
{
  BDD r = BDD_FALSE;

  for (const auto &entity : entities) {
    BDD state_act = encEntity(entity);
    int actEntity;

    // if entity is also an aciton entity, we include it in the encoding
    if ((actEntity = getMappedStateToActID(entity)) >= 0) {
      state_act += encActEntity(actEntity);
    }

    r += state_act;
  }

  return r;
}

BDD SymRS::encActEntitiesConj(const Entities &entities)
{
  BDD r = BDD_TRUE;

  for (const auto &entity : entities) {
    Entity actEntity = getMappedStateToActID(entity);
    r *= encActEntity(actEntity);
  }

  return r;
}

BDD SymRS::compState(const BDD &state) const
{
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

  for (unsigned int i = 0; i < totalActions; ++i) {
    if (!(*pv_act)[i] * context != cuddMgr->bddZero()) {
      c *= !(*pv_act)[i];
    }
  }

  return c;
}

std::string SymRS::decodedRctSysStateToStr(const BDD &state)
{
  std::string s = "{ ";

  for (unsigned int i = 0; i < totalRctSysStateVars; ++i) {
    if (!(encEntity(i) * state).IsZero()) {
      s += rs->entityToStr(i) + " ";
    }
  }

  s += "}";
  return s;
}

void SymRS::printDecodedRctSysStates(const BDD &states)
{
  BDD unproc = states;

  while (!unproc.IsZero()) {
    BDD t = unproc.PickOneMinterm(*pv_rs);
    cout << decodedRctSysStateToStr(t) << endl;

    if (opts->verbose > 9) {
      t.PrintMinterm();
      cout << endl;
    }

    unproc -= t;
  }
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

  // Variables for reaction system with CA (if used)
  pv = new vector<BDD>(totalStateVars);
  pv_succ = new vector<BDD>(totalStateVars);
  pv_E = new BDD(BDD_TRUE);
  pv_succ_E = new BDD(BDD_TRUE);

  // Reaction system (no actions, no CA)
  pv_rs = new vector<BDD>(totalRctSysStateVars);
  pv_rs_succ = new vector<BDD>(totalRctSysStateVars);
  pv_rs_E = new BDD(BDD_TRUE);
  pv_rs_succ_E = new BDD(BDD_TRUE);

  for (unsigned int i = 0; i < totalRctSysStateVars; ++i) {
    (*pv_rs)[i] = cuddMgr->bddVar(bdd_var_idx++);
    (*pv_rs_succ)[i] = cuddMgr->bddVar(bdd_var_idx++);
    *pv_rs_E *= (*pv_rs)[i];
    *pv_rs_succ_E *= (*pv_rs_succ)[i];

    (*pv)[global_state_idx] = (*pv_rs)[i];
    (*pv_succ)[global_state_idx] = (*pv_rs_succ)[i];
    ++global_state_idx;
  }

  // CA
  if (usingContextAutomaton()) {
    VERB("Context automaton variables");

    pv_ca = new vector<BDD>(totalCtxAutStateVars);
    pv_ca_succ = new vector<BDD>(totalCtxAutStateVars);
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

  // Actions/Contexts
  pv_act = new vector<BDD>(totalActions);
  pv_act_E = new BDD(BDD_TRUE);

  for (unsigned int i = 0; i < totalActions; ++i) {
    (*pv_act)[i] = cuddMgr->bddVar(bdd_var_idx++);
    *pv_act_E *= (*pv_act)[i];
  }

  // Quantification BDDs

  *pv_E = *pv_rs_E;
  *pv_succ_E = *pv_rs_succ_E;

  if (usingContextAutomaton()) {
    *pv_E *= *pv_ca_E;
    *pv_succ_E *= *pv_ca_succ_E;
  }

  VERB("All BDD variables ready");
}

void SymRS::encodeTransitions(void)
{
  DecompReactions dr;

  VERB("Decomposing reactions");

  for (unsigned int i = 0; i < totalReactions; ++i) {
    ReactionCond cond;
    cond.rctt = rs->reactions[i].rctt;
    cond.inhib = rs->reactions[i].inhib;

    for (Entities::iterator p = rs->reactions[i].prod.begin();
         p != rs->reactions[i].prod.end(); ++p) {
      dr[*p].push_back(cond);
    }
  }

  VERB("Encoding reactions");

  if (opts->part_tr_rel) {
    VERB("Using partitioned transition relation encoding");
    partTrans = new vector<BDD>(totalRctSysStateVars);
  }
  else {
    VERB("Using monolithic transition relation encoding");
    monoTrans = new BDD(BDD_TRUE);
  }

  for (unsigned int p = 0; p < totalRctSysStateVars; ++p) {
    VERB_L3("Encoding for successor " << p);

    DecompReactions::iterator di;

    if ((di = dr.find(p)) == dr.end()) {
      // there is no reaction producing p:
      if (opts->part_tr_rel) {
        (*partTrans)[p] = !encEntitySucc(p);
      }
      else {
        *monoTrans *= !encEntitySucc(p);
      }
    }
    else {
      // di - reactions producing p

      BDD conditions = BDD_FALSE;

      assert(di->second.size() > 0);

      for (unsigned int j = 0; j < di->second.size(); ++j) {
        conditions += encStateActEntitiesConj(di->second[j].rctt) *
                      !encStateActEntitiesDisj(di->second[j].inhib);
      }

      if (opts->part_tr_rel) {
        (*partTrans)[p] = conditions * encEntitySucc(p);
        (*partTrans)[p] += !conditions * !encEntitySucc(p);
      }
      else {
        *monoTrans *= (conditions * encEntitySucc(p)) + (!conditions * !encEntitySucc(
                        p));
      }
    }

    if (opts->reorder_trans) {
      VERB_L2("Reordering");
      Cudd_ReduceHeap(cuddMgr->getManager(), CUDD_REORDER_SIFT, 10000);
    }

  }

  VERB("Reactions ready");

  if (usingContextAutomaton()) {
    VERB("Augmenting transition relation encoding with the transition relation for context automaton");

    if (opts->part_tr_rel) {
      assert(0);
    }
    else {
      assert(tr_ca != nullptr);
      *monoTrans *= *tr_ca;
    }
  }

  VERB("Transition relation encoded")
}

BDD SymRS::getEncState(const Entities &entities)
{
  assert(0);
  //BDD state = compState(encEntitiesConj(rs->initState));
  //for (RctSys::Entities::iterator at = rs->actionEntities.begin(); at != rs->actionEntities.end(); ++at)
  //{
  //    state = state.ExistAbstract(encEntity(*at));
  //}
  return BDD_FALSE;
}

BDD SymRS::encNoContext(void)
{
  BDD noContextBDD = BDD_TRUE;

  for (unsigned int i = 0; i < totalActions; ++i) {
    noContextBDD *= !(*pv_act)[i];
  }

  return noContextBDD;
}

void SymRS::encodeInitStates(void)
{
  if (usingContextAutomaton()) {
    VERB("Encoding initial states (using context automaton)");
    encodeInitStatesForCtxAut();
  }
  else {
    VERB("Encoding initial states (for the action entities method -- no CA)");
    encodeInitStatesNoCtxAut();
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

void SymRS::encodeInitStatesNoCtxAut(void)
{
#ifndef NDEBUG

  if (opts->part_tr_rel) {
    assert(partTrans != nullptr);
  }

#endif

  initStates = new BDD(BDD_FALSE);

  for (auto state = rs->initStates.begin();
       state != rs->initStates.end();
       ++state) {
    VERB("Encoding a single inital state");
    BDD newInitState = compState(encEntitiesConj(*state));
    BDD q = BDD_TRUE;

    if (opts->part_tr_rel) {
      for (unsigned int i = 0; i < partTrans->size(); ++i) {
        q *= newInitState * (*partTrans)[i] * encNoContext();
      }
    }
    else {
      q *= newInitState * *monoTrans * encNoContext();
    }

    q = (q.ExistAbstract(*pv_E)).SwapVariables(*pv_succ, *pv);
    q = q.ExistAbstract(*pv_act_E);

    *initStates += q;
  }
}

void SymRS::mapStateToAct(void)
{
  VERB("Mapping state variables to action variables");
  unsigned int j = 0;

  for (unsigned int i = 0; i < totalRctSysStateVars; ++i) {
    if (rs->isActionEntity(i)) {
      stateToAct.push_back(j++);
    }
    else {
      stateToAct.push_back(-1);
    }
  }

  const unsigned int verbosity_level = 9;

  if (opts->verbose > verbosity_level) {
    for (unsigned int i = 0; i < stateToAct.size(); ++i) {
      cout << "ii VERBOSE(" << verbosity_level << "): stateToAct[" << i << "] = " <<
           stateToAct[i] << endl;
    }
  }
}

BDD SymRS::encActStrEntity(std::string name) const
{
  int id = getMappedStateToActID(rs->getEntityID(name));

  if (id < 0) {
    FERROR("Entity \"" << name << "\" not defined as context entity");
    return BDD_FALSE;
  }
  else {
    return encActEntity(getMappedStateToActID(rs->getEntityID(name)));
  }
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
  vector<BDD> *enc_vec;

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
    assert(0); // enc_ctx
    BDD enc_ctx = BDD_FALSE; //compContext(encActEntitiesConj(t.ctx));

    *tr_ca += enc_src * enc_ctx * enc_dst;
  }
}

/** EOF **/
