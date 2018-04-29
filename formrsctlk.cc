/*
    Copyright (c) 2012, 2013
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#include "formrsctlk.hh"


std::string BoolContexts::toStr(void) const
{
  if (oper == BCTX_PV) {
    return proc_name + "." + entity_name;
  }
  else if (oper == BCTX_TF) {
    if (tf) {
      return "true";
    }
    else {
      return "false";
    }
  }
  else if (oper == BCTX_AND) {
    return "(" + arg[0]->toStr() + " AND " + arg[1]->toStr() + ")";
  }
  else if (oper == BCTX_OR) {
    return "(" + arg[0]->toStr() + " OR " + arg[1]->toStr() + ")";
  }
  else if (oper == BCTX_XOR) {
    return "(" + arg[0]->toStr() + " XOR " + arg[1]->toStr() + ")";
  }
  else if (oper == BCTX_NOT) {
    return "~" + arg[0]->toStr();
  }

  else {
    return "??";
    assert(0);
  }
}

BDD BoolContexts::getBDD(const SymRS *srs) const
{
  if (oper == BCTX_PV) {
    return srs->encActStrEntity(proc_name, entity_name);
  }
  else if (oper == BCTX_TF) {
    if (tf) {
      return srs->getBDDtrue();
    }
    else {
      return srs->getBDDfalse();
    }
  }
  else if (oper == BCTX_AND) {
    return arg[0]->getBDD(srs) * arg[1]->getBDD(srs);
  }
  else if (oper == BCTX_OR) {
    return arg[0]->getBDD(srs) + arg[1]->getBDD(srs);
  }
  else if (oper == BCTX_XOR) {
    return arg[0]->getBDD(srs) ^ arg[1]->getBDD(srs);
  }
  else if (oper == BCTX_NOT) {
    return !arg[0]->getBDD(srs);
  }
  else {
    assert(0);
    FERROR("Undefined operator used in Boolean context definition. This should not happen.");
    return srs->getBDDfalse();
  }
}

std::string FormRSCTLK::toStr(void) const
{
  if (oper == RSCTLK_PV) {
    return proc_name + "." + entity_name;
  }
  else if (oper == RSCTLK_TF) {
    if (tf) {
      return "true";
    }
    else {
      return "false";
    }
  }
  else if (oper == RSCTLK_AND) {
    return "(" + arg[0]->toStr() + " AND " + arg[1]->toStr() + ")";
  }
  else if (oper == RSCTLK_OR) {
    return "(" + arg[0]->toStr() + " OR " + arg[1]->toStr() + ")";
  }
  else if (oper == RSCTLK_XOR) {
    return "(" + arg[0]->toStr() + " XOR " + arg[1]->toStr() + ")";
  }
  else if (oper == RSCTLK_IMPL) {
    return "(" + arg[0]->toStr() + " IMPLIES " + arg[1]->toStr() + ")";
  }
  else if (oper == RSCTLK_NOT) {
    return "~" + arg[0]->toStr();
  }
  else if (oper == RSCTLK_EX) {
    return "EX(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_EG) {
    return "EG(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_EU) {
    return "EU(" + arg[0]->toStr() + "," + arg[1]->toStr() + ")";
  }
  else if (oper == RSCTLK_EF) {
    return "EF(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_AX) {
    return "AX(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_AG) {
    return "AG(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_AU) {
    return "AU(" + arg[0]->toStr() + "," + arg[1]->toStr() + ")";
  }
  else if (oper == RSCTLK_AF) {
    return "AF(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_EX_ACT) {
    return "E" + getActionsStr() + "X(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_EG_ACT) {
    return "E" + getActionsStr() + "G(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_EU_ACT) {
    return "E" + getActionsStr() + "U(" + arg[0]->toStr() + "," + arg[1]->toStr()
           + ")";
  }
  else if (oper == RSCTLK_EF_ACT) {
    return "E" + getActionsStr() + "F(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_AX_ACT) {
    return "A" + getActionsStr() + "X(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_AG_ACT) {
    return "A" + getActionsStr() + "G(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_AU_ACT) {
    return "A" + getActionsStr() + "U(" + arg[0]->toStr() + "," + arg[1]->toStr()
           + ")";
  }
  else if (oper == RSCTLK_AF_ACT) {
    return "A" + getActionsStr() + "F(" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_NK) {
    return "NK[" + getSingleAgent() + "](" + arg[0]->toStr() + ")";
  }
  else if (oper == RSCTLK_UK) {
    return "K[" + getSingleAgent() + "](" + arg[0]->toStr() + ")";
  }

  else {
    return "??";
    assert(0);
  }
}

bool FormRSCTLK::hasOper(Oper op) const
{
  if (oper == op) {
    return true;
  }
  else {
    bool result = false;

    if (arg[0] != nullptr) {
      result = arg[0]->hasOper(op);
    }

    if (!result && arg[1] != nullptr) {
      result = arg[1]->hasOper(op);
    }

    return result;
  }
}

void FormRSCTLK::encodeEntities(const SymRS *srs)
{
  if (RSCTLK_COND_1ARG(oper)) {
    arg[0]->encodeEntities(srs);
  }
  else if (RSCTLK_COND_2ARG(oper)) {
    arg[0]->encodeEntities(srs);
    arg[1]->encodeEntities(srs);
  }
  else if (oper == RSCTLK_PV) {
    bdd = new BDD(srs->encEntity(proc_name, entity_name));
  }
}

bool FormRSCTLK::isERSCTLK(void) const
{
  if (oper == RSCTLK_PV) {
    return true;
  }

  if (oper == RSCTLK_NOT) {
    if (arg[0]->getOper() == RSCTLK_PV || arg[0]->getOper() == RSCTLK_TF) {
      return true;
    }
    else {
      return false;
    }
  }

  if (RSCTLK_COND_IS_UNIVERSAL(oper)) {
    return false;
  }

  if (RSCTLK_COND_1ARG(oper)) {
    return arg[0]->isERSCTLK();
  }

  if (RSCTLK_COND_2ARG(oper)) {
    return arg[0]->isERSCTLK() && arg[1]->isERSCTLK();
  }

  assert(0);

  return false;
}

std::string FormRSCTLK::getActionsStr(void) const
{
  // if (actions != nullptr) {
  //   std::string r = "[ ";
  //   bool firstact = true;
  //
  //   for (ActionsVec_f::iterator act = actions->begin(); act != actions->end();
  //        ++act) {
  //     if (!firstact) {
  //       r += ",";
  //     }
  //     else {
  //       firstact = false;
  //     }
  //
  //     r += "{";
  //     bool firstent = true;
  //
  //     for (Action_f::iterator ent = act->begin(); ent != act->end(); ++ent) {
  //       if (!firstent) {
  //         r += ",";
  //       }
  //       else {
  //         firstent = false;
  //       }
  //
  //       r += *ent;
  //     }
  //
  //     r += "}";
  //   }
  //
  //   r += " ]";
  //   return r;
  // }
  if (boolCtx != nullptr) {
    return "< " + boolCtx->toStr() + " >";
  }
  else {
    FERROR("Context not specified. This should not happen.");
  }
}

void FormRSCTLK::encodeActions(const SymRS *srs)
{
  if (RSCTLK_COND_ACT(oper)) {
    if (actions_bdd != nullptr) {
      forgetActionsBDD();
    }

    actions_bdd = new BDD(srs->getBDDfalse());
    assert(boolCtx != nullptr);
    // assert(actions != nullptr || boolCtx != nullptr);
    // assert(!(actions != nullptr && boolCtx != nullptr));

    // if (actions != nullptr) {
    //   for (ActionsVec_f::iterator act = actions->begin(); act != actions->end();
    //        ++act) {
    //     BDD single_action = srs->getBDDtrue();
    //
    //     for (Action_f::iterator ent = act->begin(); ent != act->end(); ++ent) {
    //       single_action *= srs->encActStrEntity(*ent);
    //     }
    //
    //     single_action = srs->compContext(single_action);
    //     *actions_bdd += single_action;
    //   }
    // }
    if (boolCtx != nullptr) {
      *actions_bdd = boolCtx->getBDD(srs);
    }
    else {
      assert(0);
    }
  }

  if (RSCTLK_COND_1ARG(oper)) {
    arg[0]->encodeActions(srs);
  }

  if (RSCTLK_COND_2ARG(oper)) {
    arg[0]->encodeActions(srs);
    arg[1]->encodeActions(srs);
  }
}
