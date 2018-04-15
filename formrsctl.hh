/*
    Copyright (c) 2012-2015
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#ifndef RS_FORMRSCTL_HH
#define RS_FORMRSCTL_HH

#include <iostream>
#include <string>
#include <cassert>
#include "rs.hh"
#include "symrs.hh"
#include "cudd.hh"

#define RSCTL_PV      0 // propositional variable
#define RSCTL_AND     1
#define RSCTL_OR      2
#define RSCTL_XOR  3
#define RSCTL_NOT     4
#define RSCTL_IMPL    5
#define RSCTL_EG      11 // Existential...
#define RSCTL_EU      12
#define RSCTL_EX      13
#define RSCTL_EF      14
#define RSCTL_AG      21 // Universal...
#define RSCTL_AU      22
#define RSCTL_AX      23
#define RSCTL_AF      24
#define RSCTL_EG_ACT  31 // Existential...
#define RSCTL_EU_ACT  32
#define RSCTL_EX_ACT  33
#define RSCTL_EF_ACT  34
#define RSCTL_AG_ACT  41 // Universal...
#define RSCTL_AU_ACT  42
#define RSCTL_AX_ACT  43
#define RSCTL_AF_ACT  44
#define RSCTL_TF      50 // true/false

/* For Boolean contexts: */
#define BCTX_PV   60
#define BCTX_AND  61
#define BCTX_OR   62
#define BCTX_XOR  63
#define BCTX_NOT  64
#define BCTX_TF   70


#define RSCTL_COND_1ARG(a) ((a) == RSCTL_NOT || (a) == RSCTL_EG || (a) == RSCTL_EF || (a) == RSCTL_EX || (a) == RSCTL_AG || (a) == RSCTL_AF || (a) == RSCTL_AX || (a) == RSCTL_EG_ACT || (a) == RSCTL_EF_ACT || (a) == RSCTL_EX_ACT || (a) == RSCTL_AG_ACT || (a) == RSCTL_AF_ACT || (a) == RSCTL_AX_ACT)
#define RSCTL_COND_2ARG(a) ((a) == RSCTL_AND || (a) == RSCTL_OR || (a) == RSCTL_XOR || (a) == RSCTL_IMPL || (a) == RSCTL_EU || (a) == RSCTL_AU || (a) == RSCTL_EU_ACT || (a) == RSCTL_AU_ACT)
#define RSCTL_COND_ACT(a) ((a) > 30 && (a) < 45)
#define RSCTL_IS_VALID(a) (RSCTL_COND_1ARG(a) || RSCTL_COND_2ARG(a) || (a) == RSCTL_PV || (a) == RSCTL_TF)

#define RSCTL_COND_IS_UNIVERSAL(a) (((a) > 20 && (a) < 25) || ((a) > 40 && (a) < 45))

#define BCTX_COND_1ARG(a) ((a) == BCTX_NOT)
#define BCTX_COND_2ARG(a) ((a) == BCTX_AND || (a) == BCTX_OR || (a) == BCTX_XOR)
#define BCTX_IS_VALID(a) (BCTX_COND_1ARG(a) || BCTX_COND_2ARG(a) || (a) == BCTX_PV || (a) == BCTX_TF)

using std::cout;
using std::endl;

typedef unsigned char Oper;

// typedef std::string Entity_f;
// typedef std::set<Entity_f> Action_f;
// typedef vector<Action_f> ActionsVec_f;

class BoolContexts
{
    Oper oper;
    BoolContexts *arg[2];
    std::string name;
    std::string proc_name;
    bool tf;

  public:

    BoolContexts(std::string procName, std::string varName)
    {
      oper = BCTX_PV;
      name = varName;
      proc_name = procName;
      arg[0] = nullptr;
      arg[1] = nullptr;
    }

    /**
     * @brief Constructor for true/false.
     *
     * @param   val value of the logical constant
     */
    BoolContexts(bool val)
    {
      oper = BCTX_TF;
      tf = val;
      arg[0] = nullptr;
      arg[1] = nullptr;
    }

    /**
     * @brief Constructor for one-argument formula.
     */
    BoolContexts(Oper op, BoolContexts *form1)
    {
      assert(op == BCTX_NOT);
      oper = op;
      arg[0] = form1;
      arg[1] = nullptr;
    }

    /**
     * @brief Constructor for two-argument formula.
     */
    BoolContexts(Oper op, BoolContexts *form1, BoolContexts *form2)
    {
      assert(BCTX_COND_2ARG(op));
      oper = op;
      arg[0] = form1;
      arg[1] = form2;
    }

    ~BoolContexts()
    {
      delete arg[0];
      delete arg[1];
    }

    std::string toStr(void) const;

    BDD getBDD(const SymRS *srs) const;

    Oper getOper(void) const
    {
      assert(BCTX_IS_VALID(oper));
      return oper;
    }
    BoolContexts *getLeftSF(void) const
    {
      assert(arg[0] != nullptr);
      return arg[0];
    }
    BoolContexts *getRightSF(void) const
    {
      assert(BCTX_COND_2ARG(oper));
      assert(arg[1] != nullptr);
      return arg[1];
    }
};

class FormRSCTL
{
    Oper oper;
    FormRSCTL *arg[2];
    std::string entity_name;
    std::string proc_name;
    bool tf;
    BDD *bdd;
    // ActionsVec_f *actions;
    BDD *actions_bdd;
    BoolContexts *boolCtx;
  public:
    /**
     * @brief Constructor for propositional variable.
     *
     * @param   varName variable name used mostly for printing the variable.
     * @param   varBDD  the BDD describing the set where the variable holds.
     */
    FormRSCTL(std::string procName, std::string varName)
    {
      oper = RSCTL_PV;
      proc_name = procName;
      entity_name = varName;
      arg[0] = nullptr;
      arg[1] = nullptr;
      bdd = nullptr;
      // actions = nullptr;
      actions_bdd = nullptr;
      boolCtx = nullptr;
    }

    /**
     * @brief Constructor for true/false.
     *
     * @param   val value of the logical constant
     */
    FormRSCTL(bool val)
    {
      oper = RSCTL_TF;
      tf = val;
      arg[0] = nullptr;
      arg[1] = nullptr;
      bdd = nullptr;
      // actions = nullptr;
      actions_bdd = nullptr;
      boolCtx = nullptr;
    }

    /**
     * @brief Constructor for two-argument formula.
     */
    FormRSCTL(Oper op, FormRSCTL *form1, FormRSCTL *form2)
    {
      assert(RSCTL_COND_2ARG(op));
      assert(!RSCTL_COND_ACT(op));
      oper = op;
      arg[0] = form1;
      arg[1] = form2;
      bdd = nullptr;
      // actions = nullptr;
      actions_bdd = nullptr;
      boolCtx = nullptr;
    }

    /**
     * @brief Constructor for two-argument formula with action restrictions.
     */
    // FormRSCTL(Oper op, ActionsVec_f *acts, FormRSCTL *form1, FormRSCTL *form2)
    // {
    //   assert(acts != nullptr);
    //   assert(RSCTL_COND_2ARG(op));
    //   assert(RSCTL_COND_ACT(op));
    //   oper = op;
    //   arg[0] = form1;
    //   arg[1] = form2;
    //   bdd = nullptr;
    //   actions = acts;
    //   actions_bdd = nullptr;
    //   boolCtx = nullptr;
    // }

    /**
     * @brief Constructor for two-argument formula with Boolean context restrictions.
     */
    FormRSCTL(Oper op, BoolContexts *bctx, FormRSCTL *form1, FormRSCTL *form2)
    {
      assert(bctx != nullptr);
      assert(RSCTL_COND_2ARG(op));
      assert(RSCTL_COND_ACT(op));
      oper = op;
      arg[0] = form1;
      arg[1] = form2;
      bdd = nullptr;
      // actions = nullptr;
      actions_bdd = nullptr;
      boolCtx = bctx;
    }

    /**
     * @brief Constructor for one-argument formula.
     */
    FormRSCTL(Oper op, FormRSCTL *form1)
    {
      assert(RSCTL_COND_1ARG(op));
      assert(!RSCTL_COND_ACT(op));
      oper = op;
      arg[0] = form1;
      arg[1] = nullptr;
      bdd = nullptr;
      // actions = nullptr;
      actions_bdd = nullptr;
      boolCtx = nullptr;
    }

    /**
     * @brief Constructor for one-argument formula with action restrictions.
     */
    // FormRSCTL(Oper op, ActionsVec_f *acts, FormRSCTL *form1)
    // {
    //   assert(acts != nullptr);
    //   assert(RSCTL_COND_1ARG(op));
    //   assert(RSCTL_COND_ACT(op));
    //   oper = op;
    //   arg[0] = form1;
    //   arg[1] = nullptr;
    //   bdd = nullptr;
    //   // actions = acts;
    //   actions_bdd = nullptr;
    //   boolCtx = nullptr;
    // }

    /**
     * @brief Constructor for one-argument formula with Boolean context restrictions.
     */
    FormRSCTL(Oper op, BoolContexts *bctx, FormRSCTL *form1)
    {
      assert(bctx != nullptr);
      assert(RSCTL_COND_1ARG(op));
      assert(RSCTL_COND_ACT(op));
      oper = op;
      arg[0] = form1;
      arg[1] = nullptr;
      bdd = nullptr;
      // actions = nullptr;
      actions_bdd = nullptr;
      boolCtx = bctx;
    }

    /**
     * @brief Destructor.
     */
    ~FormRSCTL()
    {
      delete arg[0];
      delete arg[1];
      delete bdd;
      // delete actions;
      delete actions_bdd;
      delete boolCtx;
    }
    std::string toStr(void) const;
    bool hasOper(Oper op) const;
    const BDD *getBDD(void) const
    {
      assert(oper == RSCTL_PV);
      assert(bdd != nullptr);
      return bdd;
    }
    const BDD *getActionsBDD(void) const
    {
      assert(RSCTL_COND_ACT(oper));
      assert(actions_bdd != nullptr);
      return actions_bdd;
    }
    Oper getOper(void) const
    {
      assert(RSCTL_IS_VALID(oper));
      return oper;
    }
    FormRSCTL *getLeftSF(void) const
    {
      assert(arg[0] != nullptr);
      return arg[0];
    }
    FormRSCTL *getRightSF(void) const
    {
      assert(RSCTL_COND_2ARG(oper));
      assert(arg[1] != nullptr);
      return arg[1];
    }
    std::string getActionsStr(void) const;
    bool getTF(void) const
    {
      assert(oper == RSCTL_TF);
      return tf;
    }
    void encodeEntities(const SymRS *srs);
    void encodeActions(const SymRS *srs);
    void forgetActionsBDD(void)
    {
      if (actions_bdd != nullptr) {
        delete actions_bdd;
      }
    }
    bool isERSCTL(void) const;
};

#endif
