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
  return getBDD(srs, false);
}

BDD StateConstr::getBDDforContext(const SymRS *srs) const
{
  return getBDD(srs, true);
}

BDD StateConstr::getBDD(const SymRS *srs, bool encode_context) const
{
  if (oper == STC_PV) {
    if (encode_context)
      return srs->encActStrEntity(proc_name, entity_name);
    else
      return srs->encEntity(proc_name, entity_name);
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
    return arg[0]->getBDD(srs, encode_context) * arg[1]->getBDD(srs, encode_context);
  }
  else if (oper == STC_OR) {
    return arg[0]->getBDD(srs, encode_context) + arg[1]->getBDD(srs, encode_context);
  }
  else if (oper == STC_XOR) {
    return arg[0]->getBDD(srs, encode_context) ^ arg[1]->getBDD(srs, encode_context);
  }
  else if (oper == STC_NOT) {
    return !arg[0]->getBDD(srs, encode_context);
  }
  else {
    assert(0);
    FERROR("Undefined operator used in Boolean state/context definition. This should not happen.");
    return srs->getBDDfalse();
  }
}

bool StateConstr::isFalse(void) const
{
  if (oper == STC_TF && tf == false)
    return true;

  if (oper == STC_NOT && arg[0]->isTrue())
    return true;

  return false;
}

bool StateConstr::isTrue(void) const
{
  if (oper == STC_TF && tf == true)
    return true;

  if (oper == STC_NOT && arg[0]->isFalse())
    return true;

  return false;
}
