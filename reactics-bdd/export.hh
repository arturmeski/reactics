
#ifndef EXPORT_HH
#define EXPORT_HH

#include <iostream>
#include "types.hh"
#include "mc.hh"
#include "rs.hh"
#include "rsin_driver.hh"


class RSExporter {
public:
    RSExporter(RctSys *rs, rsin_driver *drv, std::ostream & outStream = std::cout);

    void exportToISPL();
private:
    RctSys *rs;
    rsin_driver *drv;
    string indent {"  "};
    std::ostream &output;

    void exportEnvironment();
    void exportAgent(const Process & proc);

    void exportEnvironmentVars();
    void exportEnvironmentActions();
    void exportEnvironmentProtocol();
    void exportEnvironmentEvolution();
    void exportEnvironmentInitState();

    void exportAgentVars(const Process & proc);
    void exportAgentProtocol(const Process & proc);
    void exportAgentEvolution(const Process & proc);
    void exportAgentReactions(const Process & proc);
    void exportAgentInitState(const Process & proc);

    void parseFormulas();
    void exportEvaluation();
    void exportInitStates();
    void exportFormulae();

    std::string stateConstrToStr(const StateConstr * guard);
    std::string reactionCondToStr(const Reaction & reaction);
    std::string appendCondition(std::string & oldCond, std::string & newCond);
    std::string formulaToStr(const FormRSCTLK * form);

    EntitiesForProc procInputs;
    EntitiesForProc procOutputs;
    
    std::map<std::string, std::string> atoms;
    std::vector<std::string> formulas;
};

#endif