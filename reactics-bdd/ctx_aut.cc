
#include "ctx_aut.hh"
#include "macro.hh"
#include "rs.hh"
#include "stateconstr.hh"

CtxAut::CtxAut(Options *opts, RctSys *parent_rctsys)
{
  setOptions(opts);
  this->parent_rctsys = parent_rctsys;
  made_progressive = false;
}

bool CtxAut::hasState(std::string name)
{
  if (states_names.find(name) == states_names.end()) {
    return false;
  }
  else {
    return true;
  }
}

State CtxAut::getStateID(std::string name)
{
  if (!hasState(name)) {
    FERROR("No such state: " << name);
  }

  return states_names[name];
}

std::string CtxAut::getStateName(State state_id)
{
  assert(state_id < states_ids.size());
  return states_ids[state_id];
}

void CtxAut::addState(std::string name)
{
  if (!hasState(name)) {
    State new_state_id = states_ids.size();

    VERB_L2("Adding state: " << name << " index=" << new_state_id);

    states_ids.push_back(name);
    states_names[name] = new_state_id;

    if (!init_state_defined) {
      setInitState(name);
    }
  }
}

void CtxAut::setInitState(std::string name)
{
  VERB_L2("Setting initial CA state: " << name);
  State state_id = getStateID(name);
  VERB_L2("Got initial CA state ID: index=" << state_id);
  init_state_id = state_id;
  init_state_defined = true;
}

State CtxAut::getInitState(void)
{
  assert(init_state_defined);
  return init_state_id;
}

void CtxAut::printAutomaton(void)
{
  showStates();
  showTransitions();
}

void CtxAut::showStates(void)
{
  if (states_ids.size() > 0) {
    cout << "# Context Automaton States:" << endl;
    cout << " = Init state: " << getStateName(init_state_id) << endl;

    for (const auto &s : states_ids) {
      cout << " * " << s << endl;
    }
  }
}

void CtxAut::pushContextEntity(Entity entity_id)
{
  tmpEntities.insert(entity_id);
}

void CtxAut::saveCurrentContextSet(Process proc_id)
{
  if (!parent_rctsys->hasProcess(proc_id)) {
    FERROR("No such process: ID=" << proc_id);
  }

  tmpProcEntities[proc_id] = tmpEntities;
  tmpEntities.clear();
}

void CtxAut::addTransition(std::string srcStateName, std::string dstStateName,
                           StateConstr *stateConstr)
{
  VERB_L3("Saving transition");

  CtxAutTransition new_transition;

  new_transition.src_state = getStateID(srcStateName);
  new_transition.ctx = tmpProcEntities;
  // tmpEntities.clear();
  tmpProcEntities.clear();
  new_transition.state_constr = stateConstr;
  new_transition.dst_state = getStateID(dstStateName);
  transitions.push_back(new_transition);
}

void CtxAut::showTransitions(void)
{
  if (transitions.size() == 0) {
    cout << "Empty context automaton" << endl;
    return;
  }

  cout << "# Context Automaton Transitions:" << endl;

  for (const auto &t : transitions) {
    cout << " * [" << getStateName(t.src_state) << " -> "
         << getStateName(t.dst_state) << "]: { "
         << parent_rctsys->procEntitiesToStr(t.ctx) << "}";

    if (t.state_constr != nullptr) {
      cout << " " << t.state_constr->toStr();
    }

    cout << endl;
  }
}

void CtxAut::makeProgressive(void)
{
  VERB_LN(2, "Calculating progressive closure of CA");
  assert(!made_progressive);

  std::string special_loc = "T";

  while (hasState(special_loc)) {
    special_loc += "T";
  }

  addState(special_loc);
  State special_loc_id = getLastStateID();

  std::map<State, StateConstr *> constrs;

  for (State s = 0; s < states_ids.size(); ++s) {
    if (s == special_loc_id) {
      continue;
    }

    if (constrs.count(s) == 0) {
      constrs[s] = new StateConstr(true);
    }
  }

  constrs[special_loc_id] = new StateConstr(true);

  for (const auto &t : transitions) {
    State curr_st = t.src_state;

    if (t.state_constr != nullptr) {
      constrs[curr_st] =
        new StateConstr(STC_OR, constrs[curr_st], t.state_constr);
    }
  }

  for (const auto &s : states_ids) {
    StateConstr *state_constr = nullptr;

    if (!constrs[getStateID(s)]->isTrue()) {
      state_constr = new StateConstr(STC_NOT, constrs[getStateID(s)]);
      addTransition(s, special_loc, state_constr);
    }
  }

  addTransition(special_loc, special_loc, nullptr);

  made_progressive = true;
}

/** EOF **/
