/*
    Copyright (c) 2012-2018
    Artur Meski <meski@ipipan.waw.pl>
*/

#include "rs.hh"

RctSys::RctSys(void)
  : current_process_defined(false)
{
  ctx_aut = nullptr;
}

bool RctSys::hasEntity(std::string name)
{
  if (entities_names.find(name) == entities_names.end()) {
    return false;
  }
  else {
    return true;
  }
}

void RctSys::addEntity(std::string name)
{
  if (!hasEntity(name)) {
    Entity new_entity_id = entities_ids.size();

    VERB_L2("Adding entity: " << name << " index=" << new_entity_id);

    entities_ids.push_back(name);
    entities_names[name] = new_entity_id;
  }
}

std::string RctSys::getEntityName(Entity entityID)
{
  if (entityID < entities_ids.size()) {
    return entities_ids[entityID];
  }
  else {
    FERROR("No such entity ID: " << entityID);
    return "??";
  }
}

Entity RctSys::getEntityID(std::string name)
{
  if (!hasEntity(name)) {
    FERROR("No such entity: " << name);
  }

  return entities_names[name];
}

void RctSys::setCurrentProcess(std::string processName)
{
  VERB_LN(2, "Current Process: " << processName);

  if (!hasProcess(processName)) {
    addProcess(processName);
  }

  current_proc_id = getProcessID(processName);
  current_process_defined = true;
}

void RctSys::addProcess(std::string processName)
{
  if (!hasProcess(processName)) {
    Process new_proc_id = processes_ids.size();

    VERB_L2("Adding process: " << processName << " index=" << new_proc_id);

    processes_ids.push_back(processName);
    processes_names[processName] = new_proc_id;

    // reactions for the new process
    proc_reactions[new_proc_id] = Reactions();
    assert(proc_reactions.size() == new_proc_id + 1);
  }
}

bool RctSys::hasProcess(std::string processName)
{
  if (processes_names.find(processName) == processes_names.end()) {
    return false;
  }
  else {
    return true;
  }
}

bool RctSys::hasProcess(Process processID)
{
  if (processID >= processes_ids.size()) {
    return false;
  }

  return true;
}

Process RctSys::getProcessID(std::string processName)
{
  if (!hasProcess(processName)) {
    FERROR("No such process: " << processName);
  }

  return processes_names[processName];
}

std::string RctSys::getProcessName(Process processID)
{
  if (hasProcess(processID)) {
    return processes_ids[processID];
  }
  else {
    FERROR("No such process ID: " << processID);
  }
}

void RctSys::pushReactant(std::string entityName)
{
  if (!hasEntity(entityName)) {
    addEntity(entityName);
  }

  tmpReactants.insert(getEntityID(entityName));
}
void RctSys::pushInhibitor(std::string entityName)
{
  if (!hasEntity(entityName)) {
    addEntity(entityName);
  }

  tmpInhibitors.insert(getEntityID(entityName));
}
void RctSys::pushProduct(std::string entityName)
{
  if (!hasEntity(entityName)) {
    addEntity(entityName);
  }

  tmpProducts.insert(getEntityID(entityName));
}

void RctSys::addReactionForCurrentProcess(Reaction reaction)
{
  if (!current_process_defined) {
    FERROR("Internal error. Current process is not set!");
  }

  proc_reactions[current_proc_id].push_back(reaction);
}

void RctSys::commitReaction(void)
{
  VERB_L3("Saving reaction");

  Reaction r;

  r.rctt = tmpReactants;
  r.inhib = tmpInhibitors;
  r.prod = tmpProducts;

  addReactionForCurrentProcess(r);

  tmpReactants.clear();
  tmpInhibitors.clear();
  tmpProducts.clear();
}

std::string RctSys::entitiesToStr(const Entities &entities)
{
  std::string s = " ";

  for (auto a = entities.begin(); a != entities.end(); ++a) {
    s += entityToStr(*a) + " ";
  }

  return s;
}

std::string RctSys::procEntitiesToStr(const EntitiesForProc &procEntities)
{
  std::string s = "";

  for (auto const &p : procEntities) {
    s += getProcessName(p.first) + "={" + entitiesToStr(p.second) + "} ";
  }

  return s;
}

void RctSys::showReactions(void)
{
  cout << "# Reactions:" << endl;

  for (unsigned int proc_id = 0; proc_id < processes_ids.size(); ++proc_id) {
    cout << endl;
    cout << "  . proc = \"" << getProcessName(proc_id) << "\":" << endl;

    for (const auto &r : proc_reactions[proc_id]) {
      cout << "     * (R={" << entitiesToStr(r.rctt) << "},"
           << "I={" << entitiesToStr(r.inhib) << "},"
           << "P={" << entitiesToStr(r.prod) << "})" << endl;
    }
  }

  cout << endl;
}

void RctSys::pushStateEntity(std::string entityName)
{
  if (!hasEntity(entityName)) {
    FERROR("No such entity: " << entityName);
  }

  tmpState.insert(getEntityID(entityName));
}

void RctSys::commitInitState(void)
{
  if (ctx_aut != nullptr) {
    FERROR("Initial RS states must not be used with context automaton");
  }

  initStates.insert(tmpState);
  tmpState.clear();
}

void RctSys::addActionEntity(std::string entityName)
{
  if (!hasEntity(entityName)) {
    addEntity(entityName);
  }

  actionEntities.insert(getEntityID(entityName));
}

void RctSys::addActionEntity(Entity entity)
{
  if (!isActionEntity(entity)) {
    actionEntities.insert(entity);
  }
}

bool RctSys::isActionEntity(Entity entity)
{
  if (actionEntities.count(entity) > 0) {
    return true;
  }
  else {
    return false;
  }
}

void RctSys::showActionEntities(void)
{
  cout << "# Context entities:";

  for (auto a = actionEntities.begin(); a != actionEntities.end(); ++a) {
    cout << " " << getEntityName(*a);
  }

  cout << endl;
}

void RctSys::showInitialStates(void)
{
  cout << "# Initial states:" << endl;

  for (auto s = initStates.begin(); s != initStates.end(); ++s) {
    cout << " *";

    for (auto a = s->begin(); a != s->end(); ++a) {
      cout << " " << getEntityName(*a);
    }

    cout << endl;
  }
}

void RctSys::printSystem(void)
{
  if (!usingContextAutomaton()) {
    showInitialStates();
  }

  showActionEntities();
  showReactions();

  if (ctx_aut != nullptr) {
    ctx_aut->printAutomaton();
  }
}

void RctSys::ctxAutEnable(void)
{
  assert(ctx_aut == nullptr);

  if (initStatesDefined()) {
    FERROR("Initial states must not be defined if using context automaton");
  }

  ctx_aut = new CtxAut(opts, this);
}

void RctSys::ctxAutAddState(std::string stateName)
{
  assert(ctx_aut != nullptr);
  ctx_aut->addState(stateName);
}

void RctSys::ctxAutSetInitState(std::string stateName)
{
  assert(ctx_aut != nullptr);
  ctx_aut->setInitState(stateName);
}

void RctSys::ctxAutAddTransition(std::string srcStateName,
                                 std::string dstStateName)
{
  assert(ctx_aut != nullptr);
  ctx_aut->addTransition(srcStateName, dstStateName);
}

void RctSys::ctxAutPushNamedContextEntity(std::string entityName)
{
  assert(ctx_aut != nullptr);

  Entity entity_id = getEntityID(entityName);

  //
  // We mark the entity as an action entity
  //
  //  This step is required to ensure the minimal number of
  //  BDD variables used in the encoding of the context sets
  //
  addActionEntity(entity_id);

  ctx_aut->pushContextEntity(entity_id);
}

void RctSys::ctxAutSaveCurrentContextSet(std::string processName)
{
  Process processID = getProcessID(processName);
  ctx_aut->saveCurrentContextSet(processID);
}

/** EOF **/
