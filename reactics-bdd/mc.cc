#include "mc.hh"

ModelChecker::ModelChecker(SymRS *srs, Options *opts)
  : using_ctx_aut(false)
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
  pv_ctx_E = srs->getEncPVctx_E();
  pv_proc_enab_E = srs->getEncPVproc_enab_E();
  pv_drs_E = srs->getEncPVdrs_E();

  assert(pv != nullptr);
  assert(pv_succ != nullptr);
  assert(pv_E != nullptr);
  assert(pv_succ_E != nullptr);
  assert(pv_ctx_E != nullptr);
  assert(pv_proc_enab_E != nullptr);
  assert(pv_drs_E != nullptr);

  //
  // Transition relations
  //
  //  trp -- partitioned TR
  //  trm -- monolithic TR
  //
  // If we use trp, then trm is nullptr (same for trm)
  //
  trp = srs->getEncPartTrans();

  if (trp == nullptr) {
    trp_size = 0;
  }
  else {
    trp_size = trp->size();
  }

  trm = srs->getEncMonoTrans();

  if (srs->usingContextAutomaton()) {
    using_ctx_aut = true;
    pv_ca = srs->getEncCtxAutPV();
    pv_ca_succ = srs->getEncCtxAutPVsucc();
    pv_ca_E = srs->getEncCtxAutPV_E();
    pv_ca_succ_E = srs->getEncCtxAutPVsucc_E();
  }
  else {
    using_ctx_aut = false;
    pv_ca = nullptr;
    pv_ca_succ = nullptr;
    pv_ca_E = nullptr;
    pv_ca_succ_E = nullptr;
  }

  // Initialise the set of reachable states
  reach = nullptr;
}

inline BDD ModelChecker::getSucc(const BDD &states)
{
  BDD q = BDD_TRUE;

  VERB_L2("Computing successors");

  if (opts->part_tr_rel) {
    for (const auto &trans : *trp) {
      q *= states * trans;
      reorder();
    }
  }
  else {
    q *= states * *trm;
  }

  q = (q.ExistAbstract(*pv_E)).SwapVariables(*pv_succ, *pv);

  // we should have one BDD for cleaning up
  // it should be calculated at the very beginning

  q = q.ExistAbstract(*pv_ctx_E);
  q = q.ExistAbstract(*pv_proc_enab_E);

  return q;
}

inline BDD ModelChecker::getPreE(const BDD &states)
{
  BDD q = BDD_TRUE;
  VERB_L2("Computing preE");
  BDD x = states.SwapVariables(*pv, *pv_succ);

  if (opts->part_tr_rel) {
    for (const auto &trans : *trp) {
      q *= x * trans;
      reorder();
    }
  }
  else {
    q *= x * *trm;
  }

  q = q.ExistAbstract(*pv_succ_E);
  q = q.ExistAbstract(*pv_ctx_E);
  q = q.ExistAbstract(*pv_proc_enab_E);

  return q;
}

inline BDD ModelChecker::getPreEctx(const BDD &states, const BDD *contexts)
{
  BDD q = BDD_TRUE;
  VERB_L2("Computing (context-restricted) preE");
  BDD x = states.SwapVariables(*pv, *pv_succ);

  if (opts->part_tr_rel) {
    for (const auto &trans : *trp) {
      q *= x * trans;
      reorder();
    }

    q *= *contexts;
  }
  else {
    q *= x * *trm * *contexts;
  }

  q = q.ExistAbstract(*pv_succ_E);
  q = q.ExistAbstract(*pv_ctx_E);
  q = q.ExistAbstract(*pv_proc_enab_E);
  return q;
}

void ModelChecker::dropCtxAutStatePart(BDD &states)
{
  states = states.ExistAbstract(*pv_ca_E);
}

void ModelChecker::printReach(void)
{
  VERB_LN(2, "Printing/generating reachable states");

  if (opts->measure) {
    opts->ver_time = cpuTime();
  }

  assert(initStates != nullptr);

  BDD *reach = new BDD(*initStates);
  BDD reach_p = BDD_FALSE;

  unsigned int k = 0;

  while (*reach != reach_p) {
    if (opts->show_progress) {
      cout << "\rIteration " << ++k << flush;
    }

    reach_p = *reach;
    *reach += getSucc(*reach);
  }

  dropCtxAutStatePart(*reach);
  srs->printDecodedRctSysStates(*reach);
  cleanup();

  if (opts->measure) {
    opts->ver_time = cpuTime() - opts->ver_time;
    opts->ver_mem = memUsed();
  }
}

void ModelChecker::printReachWithSucc(void)
{
  VERB_LN(2, "Printing/generating reachable states (with successors)");

  BDD *reach = new BDD(*initStates);
  BDD reach_p = cuddMgr->bddZero();

  while (*reach != reach_p) {
    reach_p = *reach;
    BDD newStates = getSucc(*reach) - *reach;
    *reach += newStates;

  }

  BDD unproc = *reach;

  while (!unproc.IsZero()) {
    BDD t;
    t = unproc.PickOneMinterm(*pv);
    if (opts->backend_mode)
    {
        cout << "G " << srs->decodedRctSysStateWithCtxAutToStr(t) << endl;
    }
    else
    {
        cout << "Successors of " << srs->decodedRctSysStateWithCtxAutToStr(t) << ":" << endl;
    }
    srs->printDecodedRctSysWithCtxAutStates(getSucc(t));
    unproc -= t;
  }

  cleanup();
}

bool ModelChecker::checkReach(const Entities testState)
{
  if (opts->measure) {
    opts->ver_time = cpuTime();
  }

  // BDD st = srs->getEncState(testState);
  BDD st = BDD_FALSE;
  assert(0);

  BDD reach = *initStates;
  BDD reach_p = cuddMgr->bddZero();

  while (reach != reach_p) {
    if (reach * st != cuddMgr->bddZero()) {
      cleanup();
      return true;
    }

    reach_p = reach;
    reach += getSucc(reach);
  }

  cleanup();

  if (opts->measure) {
    opts->ver_time = cpuTime() - opts->ver_time;
    opts->ver_mem = memUsed();
  }

  return false;
}

BDD ModelChecker::getStatesRSCTLK(const FormRSCTLK *form)
{
  assert(reach != nullptr);
  Oper oper = form->getOper();

  if (oper == RSCTLK_PV) {
    return *form->getBDD() * *reach;
  }
  else if (oper == RSCTLK_TF) {
    if (form->getTF() == true) {
      return *reach;
    }
    else {
      return cuddMgr->bddZero();
    }
  }
  else if (oper == RSCTLK_AND) {
    return getStatesRSCTLK(form->getLeftSF()) * getStatesRSCTLK(form->getRightSF());
  }
  else if (oper == RSCTLK_OR) {
    return getStatesRSCTLK(form->getLeftSF()) + getStatesRSCTLK(form->getRightSF());
  }
  else if (oper == RSCTLK_XOR) {
    return getStatesRSCTLK(form->getLeftSF()) ^ getStatesRSCTLK(form->getRightSF());
  }
  else if (oper == RSCTLK_IMPL) {
    return (!getStatesRSCTLK(form->getLeftSF()) * *reach) + getStatesRSCTLK(
             form->getRightSF());
  }
  else if (oper == RSCTLK_NOT) {
    return !getStatesRSCTLK(form->getLeftSF()) * *reach;
  }
  else if (oper == RSCTLK_EX) {
    return getPreE(getStatesRSCTLK(form->getLeftSF())) * *reach;
  }
  else if (oper == RSCTLK_EG) {
    return statesEG(getStatesRSCTLK(form->getLeftSF()));
  }
  else if (oper == RSCTLK_EU) {
    return statesEU(
             getStatesRSCTLK(form->getLeftSF()),
             getStatesRSCTLK(form->getRightSF())
           );
  }
  else if (oper == RSCTLK_EF) {
    return statesEF(getStatesRSCTLK(form->getLeftSF()));
  }
  else if (oper == RSCTLK_AX) {
    return !getPreE(!getStatesRSCTLK(form->getLeftSF()) * *reach) * *reach;
  }
  else if (oper == RSCTLK_AG) {
    return !statesEF(
             !getStatesRSCTLK(form->getLeftSF()) * *reach) * *reach;
  }
  else if (oper == RSCTLK_AU) {
    BDD ng = !getStatesRSCTLK(form->getRightSF()) * *reach;
    BDD nf = !getStatesRSCTLK(form->getLeftSF()) * *reach;

    BDD x = !statesEU(ng, ng * nf) * *reach;

    if (!x.IsZero()) {
      x = x * !statesEG(ng) * *reach;
    }

    return x;
  }
  else if (oper == RSCTLK_AF) {
    return !statesEG(
             !getStatesRSCTLK(form->getLeftSF()) * *reach) * *reach;
  }
  /***** CONTEXT RESTRICTIONS: ******/
  else if (oper == RSCTLK_EX_ACT) {
    return getPreEctx(getStatesRSCTLK(form->getLeftSF()),
                      form->getActionsBDD()) * *reach;
  }
  else if (oper == RSCTLK_EG_ACT) {
    return statesEGctx(form->getActionsBDD(),
                       getStatesRSCTLK(form->getLeftSF())); /***** EG? *****/
  }
  else if (oper == RSCTLK_EU_ACT) {
    return statesEUctx(
             form->getActionsBDD(),
             getStatesRSCTLK(form->getLeftSF()),
             getStatesRSCTLK(form->getRightSF())
           );
  }
  else if (oper == RSCTLK_EF_ACT) {
    return statesEFctx(form->getActionsBDD(), getStatesRSCTLK(form->getLeftSF()));
  }
  else if (oper == RSCTLK_AX_ACT) {
    return !getPreEctx(!getStatesRSCTLK(form->getLeftSF()) * *reach,
                       form->getActionsBDD()) * *reach;
  }
  else if (oper == RSCTLK_AG_ACT) {
    return !statesEFctx(form->getActionsBDD(),
                        !getStatesRSCTLK(form->getLeftSF()) * *reach) * *reach;
  }
  else if (oper == RSCTLK_AU_ACT) {
    BDD ng = !getStatesRSCTLK(form->getRightSF()) * *reach;
    BDD nf = !getStatesRSCTLK(form->getLeftSF()) * *reach;

    BDD x = !statesEUctx(form->getActionsBDD(), ng, ng * nf) * *reach;

    if (!x.IsZero()) {
      x = x * !statesEGctx(form->getActionsBDD(), ng) * *reach;
    }

    return x;
  }
  else if (oper == RSCTLK_AF_ACT) {
    return !statesEGctx(form->getActionsBDD(),
                        !getStatesRSCTLK(form->getLeftSF()) * *reach) * *reach;
  }
  else if (oper == RSCTLK_NK) {
    auto proc_id = srs->rs->getProcessID(form->getSingleAgent());
    return statesNK(getStatesRSCTLK(form->getLeftSF()) * *reach, proc_id) * *reach;
  }
  else if (oper == RSCTLK_UK) {
    auto proc_id = srs->rs->getProcessID(form->getSingleAgent());
    return *reach - (statesNK(*reach - getStatesRSCTLK(form->getLeftSF()), proc_id) * *reach);
  }
  else if (oper == RSCTLK_NE) {
    auto proc_set = form->getAgentsAsProcSet(srs->rs);
    return statesNE(getStatesRSCTLK(form->getLeftSF()) * *reach, proc_set) * *reach;
  }
  else if (oper == RSCTLK_UE) {
    auto proc_set = form->getAgentsAsProcSet(srs->rs);
    return *reach - (statesNE(*reach - getStatesRSCTLK(form->getLeftSF()), proc_set) * *reach);
  }
  else if (oper == RSCTLK_NC) {
    auto proc_set = form->getAgentsAsProcSet(srs->rs);
    return statesNC(getStatesRSCTLK(form->getLeftSF()) * *reach, proc_set) * *reach;
  }
  else if (oper == RSCTLK_UC) {
    auto proc_set = form->getAgentsAsProcSet(srs->rs);
    return *reach - (statesNC(*reach - getStatesRSCTLK(form->getLeftSF()), proc_set) * *reach);
  }

  assert(0); // Should never happen
  return BDD_FALSE;
}

BDD ModelChecker::statesEG(const BDD &states)
{
  BDD x = states;
  BDD x_p = cuddMgr->bddZero();

  while (x != x_p) {
    x_p = x;
    x = x * getPreE(x);
  }

  return x;
}

BDD ModelChecker::statesEU(const BDD &statesA, const BDD &statesB)
{
  BDD x = statesA;
  BDD x_p = *reach;

  while (x != x_p) {
    x_p = x;
    x = x + (statesA * getPreE(x));
  }

  return x;
}

BDD ModelChecker::statesEF(const BDD &states)
{
  BDD x = states;
  BDD x_p = *reach;

  while (x != x_p) {
    x_p = x;
    x = x + (*reach * getPreE(x));
  }

  return x;
}

BDD ModelChecker::statesEGctx(const BDD *contexts, const BDD &states)
{
  BDD x = states;
  BDD x_p = cuddMgr->bddZero();

  while (x != x_p) {
    x_p = x;
    x = x * getPreEctx(x, contexts);
  }

  return x;
}

BDD ModelChecker::statesEUctx(const BDD *contexts, const BDD &statesA,
                              const BDD &statesB)
{
  BDD x = statesA;
  BDD x_p = *reach;

  while (x != x_p) {
    x_p = x;
    x = x + (statesA * getPreEctx(x, contexts));
  }

  return x;
}

BDD ModelChecker::statesEFctx(const BDD *contexts, const BDD &states)
{
  BDD x = states;
  BDD x_p = *reach;

  while (x != x_p) {
    x_p = x;
    x = x + (*reach * getPreEctx(x, contexts));
  }

  return x;
}

BDD ModelChecker::statesNK(const BDD &states, Process proc_id)
{
  // bdd = new BDD((arg[0]->satStates(reach) * reach).ExistAbstract(bddOnlyIth(getAgent())) * reach);
  BDD x = states;

  x = x.ExistAbstract(getIthOnly(proc_id));

  return x;
}

BDD ModelChecker::statesNE(const BDD &states, ProcSet processes)
{
  BDD x = BDD_FALSE;

  for (auto const &proc_id : processes) {
    x += states.ExistAbstract(getIthOnly(proc_id));
  }

  return x;
}

BDD ModelChecker::statesNC(const BDD &states, ProcSet processes)
{
  BDD x = BDD_FALSE;
  BDD x_p = *reach;

  while (x != x_p) {
    x_p = x;
    BDD t = BDD_FALSE;

    for (auto const &proc_id : processes) {
      t += x.ExistAbstract(getIthOnly(proc_id));
    }

    x = t;
  }

  return x;
}

BDD ModelChecker::getIthOnly(Process proc_id)
{
  /* if possible, we return the BDD from cache */
  if (ith_only_E.count(proc_id) == 1) {
    return ith_only_E[proc_id];
  }

  /* nothing has been found in the cache */
  BDD bdd = BDD_TRUE;

  for (auto i = 0; i < pv_drs_E->size(); ++i) {

    if (i == proc_id) {
      continue;
    }

    bdd *= (*pv_drs_E)[i];
  }

  ith_only_E[proc_id] = bdd;

  return bdd;
}

bool ModelChecker::checkRSCTLK(FormRSCTLK *form)
{
  if (form->isERSCTLK()) {
    return checkRSCTLKbmc(form);
  }
  else {
    return checkRSCTLKfull(form);
  }
}

bool ModelChecker::checkRSCTLKfull(FormRSCTLK *form)
{
  if (opts->measure) {
    opts->ver_time = cpuTime();
  }

  assert(form != nullptr);

  bool result = false;

  VERB("Model checking for RSCTLK formula: " << form->toStr());

  VERB("Processing the formula: encoding entities");
  form->encodeEntities(srs);
  VERB("Entities encoded");

  VERB("Processing the formula: encoding actions/contexts");
  form->encodeActions(srs);
  VERB("Contexts encoded");

  assert(reach == nullptr);

  reach = new BDD(*initStates);
  BDD reach_p = cuddMgr->bddZero();

  VERB("Generating state space");

  unsigned int k = 0;

  while (*reach != reach_p) {

    if (opts->show_progress) {
      cout << "\rIteration " << ++k << flush;
    }

    if (opts->reorder_reach) {
      VERB_L2("Reordering")
      Cudd_ReduceHeap(cuddMgr->getManager(), CUDD_REORDER_SIFT, 10000);
    }

    reach_p = *reach;
    *reach += getSucc(*reach);
  }

  if (opts->show_progress) {
    cout << endl;
  }

  VERB("Checking the formula");

  //if (*initStates * getStatesRSCTLK(form) != cuddMgr->bddZero())
  if (*initStates * getStatesRSCTLK(form) == *initStates) {
    result = true;
  }
  else {
    result = false;
  }

  cleanup();

  if (opts->backend_mode) {
      cout << "Result:" << result << endl;
  } else {
      cout << "Formula " << form->toStr() << (result ? " holds" : " does not hold")
           << endl;
  }

  if (opts->measure) {
    opts->ver_time = cpuTime() - opts->ver_time;
    opts->ver_mem = memUsed();
  }

  return result;
}

bool ModelChecker::checkRSCTLKbmc(FormRSCTLK *form)
{
  if (opts->measure) {
    opts->ver_time = cpuTime();
  }

  assert(form != nullptr);

  if (!form->isERSCTLK()) {
    FERROR("Formula " << form->toStr() <<
           " is not syntactically an ERSCTLK formula");
  }

  bool result = false;

  VERB("Bounded model checking for RSCTLK formula: " << form->toStr());

  VERB("Processing the formula: encoding entities");
  form->encodeEntities(srs);
  VERB("Entities encoded");

  VERB("Processing the formula: encoding actions/contexts");
  form->encodeActions(srs);
  VERB("Contexts encoded");

  assert(reach == nullptr);

  reach = new BDD(*initStates);
  BDD reach_p = cuddMgr->bddZero();

  unsigned int k = 0;

  while (*reach != reach_p) {
    if (opts->show_progress) {
      cout << "\rIteration " << ++k << flush;
    }

    //if (*initStates * getStatesRSCTLK(form) != cuddMgr->bddZero())
    if (*initStates * getStatesRSCTLK(form) == *initStates) {
      result = true;
      break;
    }

    reach_p = *reach;
    *reach += getSucc(*reach);
  }

  if (opts->show_progress) {
    cout << endl;
  }

  cleanup();

  if (opts->backend_mode) {
      cout << "result:" << result << endl;
  } else {
      cout << "Formula " << form->toStr() << " " << (result ? "holds" :
           "does not hold") << endl;
  }

  if (opts->measure) {
    opts->ver_time = cpuTime() - opts->ver_time;
    opts->ver_mem = memUsed();
  }

  return result;
}

void ModelChecker::reorder(void)
{
  if (opts->reorder_trans) {
    VERB_L2("Reordering START");
    // Cudd_ReduceHeap(cuddMgr->getManager(), CUDD_REORDER_SIFT, 100000);
    cuddMgr->ReduceHeap(CUDD_REORDER_GROUP_SIFT);
    VERB_L2("Reordering DONE");
  }
}

void ModelChecker::cleanup(void)
{
  delete reach;
  reach = nullptr;
}

/** EOF **/
