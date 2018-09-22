/*
    Copyright (c) 2018
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#include "stateconstr.hh"
#include "types.hh"
#include "cudd.hh"
#include "bdd_macro.hh"
#include "symrs.hh"

std::string StateConstr::toStr(void) const
{
  if (oper == STC_PV) {
    return proc_name + "." + entity_name;
  }
  else if (oper == STC_TF) {
    if (tf) {
      return "true";
    }
    else {
      return "false";
    }
  }
  else if (oper == STC_AND) {
    return "(" + arg[0]->toStr() + " AND " + arg[1]->toStr() + ")";
  }
  else if (oper == STC_OR) {
    return "(" + arg[0]->toStr() + " OR " + arg[1]->toStr() + ")";
  }
  else if (oper == STC_XOR) {
    return "(" + arg[0]->toStr() + " XOR " + arg[1]->toStr() + ")";
  }
  else if (oper == STC_NOT) {
    return "~" + arg[0]->toStr();
  }

  else {
    return "??";
    assert(0);
  }
}

BDD StateConstr::getBDDforState(const SymRS *srs) const
{
  assert(0);
  // return BDD_FALSE;
}

BDD StateConstr::getBDDforContext(const SymRS *srs) const
{
  if (oper == STC_PV) {
    return srs->encActStrEntity(proc_name, entity_name);
  }
  else if (oper == STC_TF) {
    if (tf) {
      return srs->getBDDtrue();
    }
    else {
      return srs->getBDDfalse();
    }
  }
  else if (oper == STC_AND) {
    return arg[0]->getBDD(srs) * arg[1]->getBDD(srs);
  }
  else if (oper == STC_OR) {
    return arg[0]->getBDD(srs) + arg[1]->getBDD(srs);
  }
  else if (oper == STC_XOR) {
    return arg[0]->getBDD(srs) ^ arg[1]->getBDD(srs);
  }
  else if (oper == STC_NOT) {
    return !arg[0]->getBDD(srs);
  }
  else {
    assert(0);
    FERROR("Undefined operator used in Boolean context definition. This should not happen.");
    return srs->getBDDfalse();
  }
}
