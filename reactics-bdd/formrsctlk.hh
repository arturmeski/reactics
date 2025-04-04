/*
    Copyright (c) 2012-2015
    Artur Meski <meski@ipipan.waw.pl>
*/

#ifndef RS_FORMRSCTLK_HH
#define RS_FORMRSCTLK_HH

#include <iostream>
#include <string>
#include <cassert>
// #include "rs.hh"
#include "symrs.hh"
#include "cudd.hh"
#include "types.hh"
#include "stateconstr.hh"

#define RSCTLK_PV      0 // propositional variable
#define RSCTLK_AND     1
#define RSCTLK_OR      2
#define RSCTLK_XOR  3
#define RSCTLK_NOT     4
#define RSCTLK_IMPL    5
#define RSCTLK_EG      11 // Existential...
#define RSCTLK_EU      12
#define RSCTLK_EX      13
#define RSCTLK_EF      14
#define RSCTLK_AG      21 // Universal...
#define RSCTLK_AU      22
#define RSCTLK_AX      23
#define RSCTLK_AF      24
#define RSCTLK_EG_ACT  31 // Existential...
#define RSCTLK_EU_ACT  32
#define RSCTLK_EX_ACT  33
#define RSCTLK_EF_ACT  34
#define RSCTLK_AG_ACT  41 // Universal...
#define RSCTLK_AU_ACT  42
#define RSCTLK_AX_ACT  43
#define RSCTLK_AF_ACT  44
#define RSCTLK_TF      50 // true/false

#define RSCTLK_NK      61 // Epistemic operators
#define RSCTLK_NE      62
#define RSCTLK_NC      63
#define RSCTLK_UK      71
#define RSCTLK_UE      72
#define RSCTLK_UC      73

#define RSCTLK_COND_1ARG(a) ((a) == RSCTLK_NOT || (a) == RSCTLK_EG || (a) == RSCTLK_EF || (a) == RSCTLK_EX || (a) == RSCTLK_AG || (a) == RSCTLK_AF || (a) == RSCTLK_AX || (a) == RSCTLK_EG_ACT || (a) == RSCTLK_EF_ACT || (a) == RSCTLK_EX_ACT || (a) == RSCTLK_AG_ACT || (a) == RSCTLK_AF_ACT || (a) == RSCTLK_AX_ACT || (a) == RSCTLK_UK || (a) == RSCTLK_NK || (a) == RSCTLK_UE || (a) == RSCTLK_NE || (a) == RSCTLK_UC || (a) == RSCTLK_NC)
#define RSCTLK_COND_2ARG(a) ((a) == RSCTLK_AND || (a) == RSCTLK_OR || (a) == RSCTLK_XOR || (a) == RSCTLK_IMPL || (a) == RSCTLK_EU || (a) == RSCTLK_AU || (a) == RSCTLK_EU_ACT || (a) == RSCTLK_AU_ACT)
#define RSCTLK_COND_ACT(a) ((a) > 30 && (a) < 45)
#define RSCTLK_IS_VALID(a) (RSCTLK_COND_1ARG(a) || RSCTLK_COND_2ARG(a) || (a) == RSCTLK_PV || (a) == RSCTLK_TF)

#define RSCTLK_COND_IS_UNIVERSAL(a) (((a) > 20 && (a) < 25) || ((a) > 40 && (a) < 45) || ((a) > 70 && (a) < 75))

using std::cout;
using std::endl;

// typedef std::string Entity_f;
// typedef std::set<Entity_f> Action_f;
// typedef vector<Action_f> ActionsVec_f;
typedef std::set<std::string> Agents_f;

class StateConstr;
class RSExporter;

class FormRSCTLK
{
  friend class RSExporter;
  
    Oper oper;
    FormRSCTLK *arg[2];
    std::string entity_name;
    std::string proc_name;
    bool tf;
    BDD *bdd;
    // ActionsVec_f *actions;
    BDD *actions_bdd;
    StateConstr *boolCtx;
    Agents_f agents;
  public:
    /**
     * @brief Constructor for propositional variable.
     *
     * @param   varName variable name used mostly for printing the variable.
     * @param   varBDD  the BDD describing the set where the variable holds.
     */
    FormRSCTLK(std::string procName, std::string varName)
    {
      oper = RSCTLK_PV;
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
    FormRSCTLK(bool val)
    {
      oper = RSCTLK_TF;
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
    FormRSCTLK(Oper op, FormRSCTLK *form1, FormRSCTLK *form2)
    {
      assert(RSCTLK_COND_2ARG(op));
      assert(!RSCTLK_COND_ACT(op));
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
    // FormRSCTLK(Oper op, ActionsVec_f *acts, FormRSCTLK *form1, FormRSCTLK *form2)
    // {
    //   assert(acts != nullptr);
    //   assert(RSCTLK_COND_2ARG(op));
    //   assert(RSCTLK_COND_ACT(op));
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
    FormRSCTLK(Oper op, StateConstr *bctx, FormRSCTLK *form1, FormRSCTLK *form2)
    {
      assert(bctx != nullptr);
      assert(RSCTLK_COND_2ARG(op));
      assert(RSCTLK_COND_ACT(op));
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
    FormRSCTLK(Oper op, FormRSCTLK *form1)
    {
      assert(RSCTLK_COND_1ARG(op));
      assert(!RSCTLK_COND_ACT(op));
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
    // FormRSCTLK(Oper op, ActionsVec_f *acts, FormRSCTLK *form1)
    // {
    //   assert(acts != nullptr);
    //   assert(RSCTLK_COND_1ARG(op));
    //   assert(RSCTLK_COND_ACT(op));
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
    FormRSCTLK(Oper op, StateConstr *bctx, FormRSCTLK *form1)
    {
      assert(bctx != nullptr);
      assert(RSCTLK_COND_1ARG(op));
      assert(RSCTLK_COND_ACT(op));
      oper = op;
      arg[0] = form1;
      arg[1] = nullptr;
      bdd = nullptr;
      // actions = nullptr;
      actions_bdd = nullptr;
      boolCtx = bctx;
    }

    FormRSCTLK(Oper op, Agents_f agents_set, FormRSCTLK *form1)
    {
      assert(RSCTLK_COND_1ARG(op));
      oper = op;
      arg[0] = form1;
      arg[1] = nullptr;
      bdd = nullptr;
      actions_bdd = nullptr;
      agents = agents_set;
    }

    /**
     * @brief Destructor.
     */
    ~FormRSCTLK()
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
      assert(oper == RSCTLK_PV);
      assert(bdd != nullptr);
      return bdd;
    }
    const BDD *getActionsBDD(void) const
    {
      assert(RSCTLK_COND_ACT(oper));
      assert(actions_bdd != nullptr);
      return actions_bdd;
    }
    Oper getOper(void) const
    {
      assert(RSCTLK_IS_VALID(oper));
      return oper;
    }
    FormRSCTLK *getLeftSF(void) const
    {
      assert(arg[0] != nullptr);
      return arg[0];
    }
    FormRSCTLK *getRightSF(void) const
    {
      assert(RSCTLK_COND_2ARG(oper));
      assert(arg[1] != nullptr);
      return arg[1];
    }
    std::string getActionsStr(void) const;
    bool getTF(void) const
    {
      assert(oper == RSCTLK_TF);
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
    bool isERSCTLK(void) const;
    Agents_f getAgents(void) const
    {
      return agents;
    }
    std::string getSingleAgent(void) const
    {
      assert(oper == RSCTLK_NK || oper == RSCTLK_UK);
      return *(agents.begin());
    }
    std::string getAgentsStr(void) const;
    ProcSet getAgentsAsProcSet(RctSys *rs) const;
};

#endif
