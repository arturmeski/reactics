/*
    Copyright (c) 2018
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#ifndef STATECONSTR_HH
#define STATECONSTR_HH

#include "types.hh"

#include <cassert>

/* For state constraints: */
#define STC_PV   80
#define STC_AND  81
#define STC_OR   82
#define STC_XOR  83
#define STC_NOT  84
#define STC_TF   90

#define STC_COND_1ARG(a) ((a) == STC_NOT)
#define STC_COND_2ARG(a) ((a) == STC_AND || (a) == STC_OR || (a) == STC_XOR)
#define STC_IS_VALID(a) (STC_COND_1ARG(a) || STC_COND_2ARG(a) || (a) == STC_PV || (a) == STC_TF)

class SymRS;

class StateConstr
{
    Oper oper;
    StateConstr *arg[2];
    std::string entity_name;
    std::string proc_name;
    bool tf;

  public:

    StateConstr(std::string procName, std::string varName)
    {
      oper = STC_PV;
      entity_name = varName;
      proc_name = procName;
      arg[0] = nullptr;
      arg[1] = nullptr;
    }

    /**
     * @brief Constructor for true/false.
     *
     * @param   val value of the logical constant
     */
    StateConstr(bool val)
    {
      oper = STC_TF;
      tf = val;
      arg[0] = nullptr;
      arg[1] = nullptr;
    }

    /**
     * @brief Constructor for one-argument formula.
     */
    StateConstr(Oper op, StateConstr *form1)
    {
      assert(op == STC_NOT);
      oper = op;
      arg[0] = form1;
      arg[1] = nullptr;
    }

    /**
     * @brief Constructor for two-argument formula.
     */
    StateConstr(Oper op, StateConstr *form1, StateConstr *form2)
    {
      assert(STC_COND_2ARG(op));
      oper = op;
      arg[0] = form1;
      arg[1] = form2;
    }

    ~StateConstr()
    {
      delete arg[0];
      delete arg[1];
    }

    std::string toStr(void) const;

    BDD getBDD(const SymRS *srs, bool encode_context) const;
    BDD getBDDforContext(const SymRS *srs) const;
    BDD getBDDforState(const SymRS *srs) const;

    Oper getOper(void) const
    {
      assert(STC_IS_VALID(oper));
      return oper;
    }
    StateConstr *getLeftSF(void) const
    {
      assert(arg[0] != nullptr);
      return arg[0];
    }
    StateConstr *getRightSF(void) const
    {
      assert(STC_COND_2ARG(oper));
      assert(arg[1] != nullptr);
      return arg[1];
    }

    bool isFalse(void) const;
    bool isTrue(void) const;
};

#endif
