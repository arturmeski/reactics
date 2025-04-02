
#include "export.hh"


RSExporter::RSExporter(RctSys *rs, rsin_driver *drv, std::ostream & outStream): 
        rs(rs), drv(drv), output(outStream) {

    // Store all possible inputs (reactants and inhibitors) and outputs (products) for each process

    for (Process proc=0; proc<rs->getNumberOfProcesses(); ++proc) {
        for (const auto & rr : rs->proc_reactions[proc]) {
            for (const auto & e : rr.rctt)
                procInputs[proc].insert(e);
        
            for (const auto & e : rr.inhib)
                procInputs[proc].insert(e);
        
            for (const auto & e : rr.prod)
                procOutputs[proc].insert(e);            
        }
    }

    // Add possible inputs from context automaton

    for (const auto & trans : rs->ctx_aut->transitions) {
        for (const auto & procCtx : trans.ctx) {
            for (const auto & e : procCtx.second) {
                procInputs[procCtx.first].insert(e);
            }
        }
    }
}


void RSExporter::exportToISPL() {
    exportEnvironment();

    for (Process proc=0; proc<rs->getNumberOfProcesses(); ++proc)
        exportAgent(proc);

    parseFormulas();
    exportEvaluation();
    exportInitStates();
    exportFormulae();
}


void RSExporter::exportEnvironment() {
    output << "Agent Environment\n\n";

    exportEnvironmentVars();
    exportEnvironmentActions();
    exportEnvironmentProtocol();
    exportEnvironmentEvolution();

    output << "\nend Agent\n" << endl;
}


void RSExporter::exportEnvironmentVars() {
    output << "Obsvars:\n"
           << indent << "mode: {init, clear, select_active_agents, activate_agents,\n" 
           << indent << indent << "distribute_local, add_context, distribute_global, produce,\n";

    for (Process proc=0; proc<rs->getNumberOfProcesses(); ++proc) {
        for (const Entity & e : procOutputs[proc]) {
            output << indent << indent << "collect_" << rs->processes_ids[proc] 
                   << "_" << rs->entities_ids[e] << ",\n";
        }
    }

    output << indent << indent << "finalize\n" << indent << "};\n\n";

    output << indent << "-- Boolean variables denoting entities available for each agent --\n\n";

    for (Process proc=0; proc<rs->getNumberOfProcesses(); ++proc) {
        for (const Entity & e : procInputs[proc]) {
            output << indent << rs->processes_ids[proc] 
                   << "_" << rs->entities_ids[e] << ": 0..1;\n";
        }

        output << "\n";
    }

    output << indent << "-- Boolean variables denoting which agents are active --\n\n";

    for (const string & procName : rs->processes_ids)
        output << indent << "Active_" << procName << ": 0..1;\n";

    output << "end Obsvars\n\n"
           << "Vars:\n\n";
           
    output << indent << "-- Context automaton details --\n\n";

    output << indent << "state: {";

    for (size_t i=0; i<rs->ctx_aut->statesCount(); ++i) {
        string stName = rs->ctx_aut->getStateName(i);

        // Skip the dummy state used for closure
        if (stName == "T")
            continue;

        if (i) output << ", ";
    
        output << stName;
    }

    output << "};\n";

    // Add dummy transition leading to the initial state (no agent is active)
    output << indent << "transition: {"
           << "\n" << indent << indent << "init_0";

    int trId {1};

    for (const CtxAutTransition & trans : rs->ctx_aut->transitions) {
        string dstName = rs->ctx_aut->getStateName(trans.dst_state);

        if (dstName == "T")
            continue;

        output << ",";
        output << "\n" << indent << indent << rs->ctx_aut->getStateName(trans.src_state) 
               << "_" << dstName << "_" << trId;
        ++trId;
    }

    output << indent << "\n};\n\n";

    output << indent << "-- Boolean variables denoting existence of entities in the environment.\n\n";
    
    for (const string & entityName : rs->entities_ids) 
        output << indent << entityName << " : 0..1;\n";
    
    output << "end Vars" << endl;
}


void RSExporter::exportEnvironmentActions() {
    output << "\nActions = {\n"
           << indent << "init, clear, select_active_agents, activate_agents,\n"
           << indent << "distribute_local, add_context, distribute_global, produce,\n";

    for (Process proc=0; proc<rs->getNumberOfProcesses(); ++proc) {
        for (const Entity & e : procOutputs[proc]) {
            output << indent << "collect_" << rs->processes_ids[proc] 
                   << "_" << rs->entities_ids[e] << ",\n";
        }
    }

    output << indent << "finalize, sleep\n};\n";
}


void RSExporter::exportEnvironmentProtocol() {
    output << "\nProtocol:\n" 
           << indent << "mode=clear : {clear};\n"
           << indent << "mode=select_active_agents : {select_active_agents};\n"
           << indent << "mode=activate_agents : {activate_agents};\n\n";

    for (Process proc=0; proc<rs->getNumberOfProcesses(); ++proc) {
        for (const Entity & e : procOutputs[proc]) {
            output << indent << "mode=collect_" << rs->processes_ids[proc] 
                   << "_" << rs->entities_ids[e] 
                   << ": {collect_" << rs->processes_ids[proc] 
                   << "_" << rs->entities_ids[e] << "};\n";
        }

        output << "\n";
    }

    output << indent << "mode=distribute_local : {distribute_local};\n"
           << indent << "mode=add_context : {add_context};\n"
           << indent << "mode=distribute_global : {distribute_global};\n"
           << indent << "mode=produce : {produce};\n"
           << indent << "mode=finalize : {finalize};\n\n"
           << indent << "Other : {sleep};\n"
           << "end Protocol\n";
}


void RSExporter::exportEnvironmentEvolution() {
    output << "\nEvolution:\n\n";

    //--------------------------------------------------------------------------------
    // Reset the environment state after the previous computation step.
    // (reset agent activity status, availability of entities, etc.)
    //--------------------------------------------------------------------------------

    output << indent <<"--------------------------------------------------------------------------------\n"
           << indent <<"-- Reset the environment state after the previous computation step.\n"
           << indent <<"-- (reset agent activity status, availability of entities, etc.)\n"
           << indent <<"--------------------------------------------------------------------------------\n\n"
           << indent;

    for (const string & procName : rs->processes_ids)
        output << "Active_" << procName << "=0 and ";
    
    output << "\n" << indent << indent;
    
    for (const string & entityName : rs->entities_ids) 
        output << entityName << "=0 and ";

    output << "\n" << indent << indent << "mode=select_active_agents\n"
           << indent << indent << indent << "if mode=clear;\n\n";

    //--------------------------------------------------------------------------------
    // Active agents are selected based on the current context automaton transition.
    //--------------------------------------------------------------------------------

    output << indent <<"--------------------------------------------------------------------------------\n"
           << indent <<"-- Active agents are selected based on the current context automaton transition.\n"
           << indent <<"--------------------------------------------------------------------------------\n\n"
           << indent;

    // For the dummy initial transition leading to the initial state no agent is active
    for (Process proc=0; proc<rs->getNumberOfProcesses(); ++proc)
        output << "Active_" << rs->getProcessName(proc) << "=0 and ";

    output << "mode=activate_agents\n"
           << indent << indent << "if mode=select_active_agents and transition=init_0;\n\n" << indent;

    unsigned transNo = 1;

    for (const CtxAutTransition & trans : rs->ctx_aut->transitions) {
        vector<bool> isActive(rs->getNumberOfProcesses(), false);

        string dstName = rs->ctx_aut->getStateName(trans.dst_state);

        if (dstName == "T")
            continue;

        for (const auto & entry : trans.ctx)
            isActive[entry.first] = true;

        for (Process proc=0; proc<rs->getNumberOfProcesses(); ++proc)
            output << "Active_" << rs->getProcessName(proc) << "="
                   << (isActive[proc] ? "1" : "0")
                   << " and ";

        output << "mode=activate_agents\n"
               << indent << indent << "if mode=select_active_agents and transition="
               << rs->ctx_aut->getStateName(trans.src_state) << "_" 
               << rs->ctx_aut->getStateName(trans.dst_state) << "_" 
               << to_string(transNo) << ";\n\n" << indent;

        ++transNo;
    }

    //--------------------------------------------------------------------------------
    // Conduct a series of queries to active agents regarding products
    // that may have been produced in the last step when they were active.
    //--------------------------------------------------------------------------------

    output << "--------------------------------------------------------------------------------\n"
           << indent << "-- Conduct a series of queries to active agents regarding products\n"
           << indent << "-- that may have been produced in the last step when they were active.\n"
           << indent << "--------------------------------------------------------------------------------\n\n";

    vector<pair<Process, Entity>> procProducts;

    for (Process proc=0; proc < rs->getNumberOfProcesses(); ++proc)
        for (const Entity & e : procOutputs[proc])
            procProducts.push_back(make_pair(proc, e));
    
    output << indent << "mode=collect_"
           << rs->getProcessName(procProducts[0].first) << "_"
           << rs->getEntityName(procProducts[0].second) << "\n"
           << indent << indent << "if mode=activate_agents;\n\n";

    for (unsigned pairIdx=1; pairIdx < procProducts.size(); ++pairIdx) {
        output << indent << rs->getEntityName(procProducts[pairIdx-1].second) 
               << "=1 and mode=collect_"
               << rs->getProcessName(procProducts[pairIdx].first) << "_"
               << rs->getEntityName(procProducts[pairIdx].second) << "\n"
               << indent << indent << "if mode=collect_"
               << rs->getProcessName(procProducts[pairIdx-1].first) << "_"
               << rs->getEntityName(procProducts[pairIdx-1].second) 
               << " and " << rs->getProcessName(procProducts[pairIdx-1].first) 
               << ".Action=produce_" 
               << rs->getEntityName(procProducts[pairIdx-1].second)
               << ";\n";
               
        output << indent << "mode=collect_"
               << rs->getProcessName(procProducts[pairIdx].first) << "_"
               << rs->getEntityName(procProducts[pairIdx].second) << "\n"
               << indent << indent << "if mode=collect_"
               << rs->getProcessName(procProducts[pairIdx-1].first) << "_"
               << rs->getEntityName(procProducts[pairIdx-1].second) 
               << " and (" << rs->getProcessName(procProducts[pairIdx-1].first) 
               << ".Action=not_produce_" 
               << rs->getEntityName(procProducts[pairIdx-1].second)
               << " or " << rs->getProcessName(procProducts[pairIdx-1].first) 
               << ".Action=sleep);\n\n";
    }

    output << indent << rs->getEntityName(procProducts.rbegin()->second) 
            << "=1 and mode=distribute_local\n"
            << indent << indent << "if mode=collect_"
            << rs->getProcessName(procProducts.rbegin()->first) << "_"
            << rs->getEntityName(procProducts.rbegin()->second) 
            << " and " << rs->getProcessName(procProducts.rbegin()->first) 
            << ".Action=produce_" 
            << rs->getEntityName(procProducts.rbegin()->second)
            << ";\n";
            
    output << indent << "mode=distribute_local\n"
            << indent << indent << "if mode=collect_"
            << rs->getProcessName(procProducts.rbegin()->first) << "_"
            << rs->getEntityName(procProducts.rbegin()->second) 
            << " and (" << rs->getProcessName(procProducts.rbegin()->first) 
            << ".Action=not_produce_" 
            << rs->getEntityName(procProducts.rbegin()->second)
            << " or " << rs->getProcessName(procProducts.rbegin()->first) 
            << ".Action=sleep);\n\n";

    //--------------------------------------------------------------------------------
    // The entities available in the environment are distributed between the agents.
    //--------------------------------------------------------------------------------

    output << indent <<"--------------------------------------------------------------------------------\n"
           << indent <<"-- The entities available in the environment are distributed between the agents. \n"
           << indent <<"--------------------------------------------------------------------------------\n\n"
           << indent;

    bool first = true;

    for (Process proc=0; proc<rs->getNumberOfProcesses(); ++proc) {
        for (const Entity & e : procInputs[proc]) {
            if (!first)
                output << " and ";
            else
                first = false;

            output << rs->getProcessName(proc) << "_" << rs->getEntityName(e) << "=" << rs->getEntityName(e);
        }

        output << "\n" << indent; 
    }

    output << "and mode=add_context\n" << indent << indent 
           << "if mode=distribute_local;\n\n";

    //--------------------------------------------------------------------------------
    // A set of additional entities, if any, is provided for each active agent 
    // following the context automaton transition description.
    //--------------------------------------------------------------------------------

    output << indent <<"--------------------------------------------------------------------------------\n"
           << indent <<"-- A set of additional entities, if any, is provided for each active agent\n"
           << indent <<"-- following the context automaton transition description.\n"
           << indent <<"--------------------------------------------------------------------------------\n\n"
           << indent;

    transNo = 1;
    vector<tuple<State, State, unsigned>> noCtxTrans;

    for (const CtxAutTransition & trans : rs->ctx_aut->transitions) {
        if (rs->ctx_aut->getStateName(trans.dst_state) == "T")
            continue;

        string ctxStr {""};
        string separator {""};
        first = true;

        for (const auto & procCtx : trans.ctx) {
            for (auto ent : procCtx.second) {
                if (first) {
                    first = false;
                    separator = "";
                }
                else
                    separator = "and ";
            
                ctxStr += separator + rs->getProcessName(procCtx.first) + "_" + rs->getEntityName(ent) + "=1 ";
            }
        }

        if (ctxStr.length() > 0) 
            output << indent << ctxStr 
                   << "and mode=distribute_global\n" << indent << indent 
                   << "if mode=add_context and transition="
                   << rs->ctx_aut->getStateName(trans.src_state) << "_" << rs->ctx_aut->getStateName(trans.dst_state) << "_" << transNo
                   << ";\n\n";
        else
            noCtxTrans.push_back({trans.src_state, trans.dst_state, transNo});
        
        ++transNo;
    }

    //--------------------------------------------------------------------------------
    // Mode change for transitions having no additional entities in the context
    //--------------------------------------------------------------------------------

    if (noCtxTrans.size() > 0) {
        output << indent << "mode=distribute_global if mode=add_context and\n" 
               << indent << indent << " (transition=init_0";

        for (const auto & trans : noCtxTrans) {
            output << " or transition=" << rs->ctx_aut->getStateName(get<0>(trans)) 
                   << "_" << rs->ctx_aut->getStateName(get<1>(trans))
                   << "_" << get<2>(trans);
        }

        output << ");\n\n";
    }
    
    //--------------------------------------------------------------------------------
    // Notify active agents to execute all possible reactions.
    //--------------------------------------------------------------------------------

    output << indent <<  "--------------------------------------------------------------------------------\n"
           << indent <<"-- Notify active agents to execute all possible reactions.\n"
           << indent <<"--------------------------------------------------------------------------------\n\n"
           << indent;

    output << "mode=produce if mode=distribute_global;\n\n";

    output << indent << "mode=finalize\n"
            << indent << indent << "if mode=produce;\n\n";

    //--------------------------------------------------------------------------------
    // Select next computation step (choose context automaton transition).
    //--------------------------------------------------------------------------------

    output << indent <<"--------------------------------------------------------------------------------\n"
           << indent <<"-- Select next computation step (choose context automaton transition).\n"
           << indent <<"--------------------------------------------------------------------------------\n\n"
           << indent;

    transNo = 1;
    
    for (const CtxAutTransition & trans : rs->ctx_aut->transitions) {
        if (rs->ctx_aut->getStateName(trans.dst_state) == "T")
            continue;     

        output << indent << "mode=clear and state=" 
               << rs->ctx_aut->getStateName(trans.dst_state)
               << " and transition="
               << rs->ctx_aut->getStateName(trans.src_state) << "_"
               << rs->ctx_aut->getStateName(trans.dst_state) << "_"
               << transNo << "\n" << indent << indent;

        output << "\n" << indent << indent << "if mode=finalize and state="
               << rs->ctx_aut->getStateName(trans.src_state);
        
        if (trans.state_constr) 
            output << " and " << stateConstrToStr(trans.state_constr);
        
        output << ";\n\n";

        ++transNo;
    }

    output << "end Evolution\n";
}


void RSExporter::exportEnvironmentInitState() {
    output << indent << "Environment.mode=clear\n\n";

    for (const string & procName : rs->processes_ids)
        output << indent << indent << "and Environment.Active_" << procName << "=0\n";
    
    output << "\n";

    for (const string & entName : rs->entities_ids)
        output << indent << indent << "and Environment." << entName << "=0\n";
    
    output << "\n";

    for (Process proc=0; proc<rs->getNumberOfProcesses(); ++proc) {
        for (const Entity & e : procInputs[proc])
            output << indent << indent << "and Environment." << rs->getProcessName(proc) << "_" 
                   << rs->entities_ids[e] << "=0\n";

        output << "\n";
    }

    State initState = rs->ctx_aut->getInitState();
    output << indent << indent
           << "and Environment.state="
           << rs->ctx_aut->getStateName(initState) << "\n"
           << indent << indent << "and Environment.transition=init_0";
}


void RSExporter::exportAgent(const Process & proc) {
    output << "\nAgent " << rs->processes_ids[proc] << "\n\n";
    
    exportAgentVars(proc);
    exportAgentProtocol(proc);
    exportAgentEvolution(proc);
    
    output  << "end Agent\n" << endl;
}


void RSExporter::exportAgentVars(const Process & proc) {
    output << "Vars:\n"
           << indent << "isActive: 0..1;\n";

    for (const Entity & e : procInputs[proc]) {
        output << indent << rs->entities_ids[e] << "_in: 0..1;\n";
    }

    for (const Entity & e : procOutputs[proc]) {
        output << indent << rs->entities_ids[e] << "_out: 0..1;\n";
    }

    output << "end Vars\n\n";

    output << "Actions = {\n";

    for (const Entity & e : procOutputs[proc]) {
        output << indent << "produce_" << rs->entities_ids[e] 
               << ", not_produce_" << rs->entities_ids[e] << ",\n";
    }

    output << indent << "sleep\n};\n\n";
}


void RSExporter::exportAgentProtocol(const Process & proc) {
    string procName = rs->processes_ids[proc];

    output << "Protocol:\n";

    for (const Entity & e : procOutputs[proc]) {
        string entityName = rs->entities_ids[e];

        output << indent << entityName << "_out=1 and (Environment.mode=collect_" << procName << "_" << entityName
               << " and isActive=1): {produce_" << entityName << "};\n"
               << indent << entityName << "_out=0 and (Environment.mode=collect_" << procName << "_" << entityName
               << " and isActive=1): {not_produce_" << entityName << "};\n\n";
    }

    output << indent << "Other: {sleep};\n"
           << "end Protocol\n\n";
}


void RSExporter::exportAgentEvolution(const Process & proc) {
    string procName = rs->processes_ids[proc];

    output << "Evolution:\n\n";
    
    //--------------------------------------------------------------------------------
    // Set the agent's activity status.
    //--------------------------------------------------------------------------------

    output << indent <<"--------------------------------------------------------------------------------\n"
           << indent <<"-- Set the agent's activity status.\n"
           << indent <<"--------------------------------------------------------------------------------\n\n";

    output << indent << "isActive=Environment.Active_" << procName << " ";

    for (const Entity & e : procInputs[proc])
        output << "and " << rs->entities_ids[e] << "_in=0 ";
    
    output << "\n" << indent << indent << "if Environment.Action=activate_agents;\n\n";

    bool first {true};

    //--------------------------------------------------------------------------------
    // Synchronise with the environment state.
    //--------------------------------------------------------------------------------

    output << indent << "--------------------------------------------------------------------------------\n"
           << indent <<"-- Synchronise with the environment state.\n"
           << indent <<"--------------------------------------------------------------------------------\n\n";
    
    for (const Entity & e : procInputs[proc]) {
        string entityName = rs->entities_ids[e];

        if (first) {
            first = false;
            output << indent;
        }
        else {
            output << "and ";
        }

        output << entityName << "_in=Environment." << procName << "_" << entityName << " ";
    }

    output << "\n" << indent << indent << "if isActive=1 and Environment.Action=distribute_global;\n\n";

    exportAgentReactions(proc);

    output << "end Evolution\n\n";
}


void RSExporter::exportAgentReactions(const Process & proc) {
    output << indent <<"--------------------------------------------------------------------------------\n"
           << indent <<"-- Agent's reactions.\n"
           << indent <<"--------------------------------------------------------------------------------\n\n";
    
    // For each entity produced accumulate all the ways it may be produced

    map<string, string> sources;
    
    for (const auto & reaction : rs->proc_reactions[proc]) {
            string rctCond = reactionCondToStr(reaction);

        for (const Entity & e : reaction.prod) {
            string rctProduct = rs->getEntityName(e);

            if (sources.count(rctProduct))
                sources[rctProduct] = appendCondition(sources[rctProduct], rctCond);
            else
                sources[rctProduct] = rctCond;
        }
    }

    // Output a single formula combining all the agent's reactions

    bool moreReactions {false};

    for (const auto & entry : sources) {
        if (moreReactions)
            output << indent << indent << "and\n";
        else
            moreReactions = true;
        
        output << indent << entry.first << "_out = " << entry.second << "\n";
    }

    output << indent << indent << "if isActive=1 and Environment.Action=produce;\n\n";
}


void RSExporter::exportAgentInitState(const Process & proc) {
    string procName = rs->processes_ids[proc];

    output << "\n\n" << indent << indent << "and " << procName << ".isActive=0";

    for (const Entity & e : procInputs[proc]) {
        output << "\n" << indent << indent << "and " << procName << "." << rs->entities_ids[e] << "_in=0";
    }

    for (const Entity & e : procOutputs[proc]) {
        output << "\n" << indent << indent << "and " << procName << "." << rs->entities_ids[e] << "_out=0";
    }
}


void RSExporter::parseFormulas() {
    for (const auto & prop : drv->properties) {
        formulas.push_back(formulaToStr(prop.second));
    }
}


void RSExporter::exportEvaluation() {
    output << "\nEvaluation\n";

    for (const auto & a : atoms)
        output << indent << a.second << " if " << a.first << ";\n";

    output << "end Evaluation" << endl;
}


void RSExporter::exportInitStates() {
    output << "\nInitStates\n";
    
    exportEnvironmentInitState();

    for (Process proc=0; proc<rs->getNumberOfProcesses(); ++proc)
        exportAgentInitState(proc);
    
    output << ";\n"
           << "end InitStates" << endl;
}


void RSExporter::exportFormulae() {
    output << "\nFormulae\n";

    for (const string & fStr : formulas) 
        output << indent << fStr << ";\n";

    output << "end Formulae" << endl;
}


/* State constraints are required to be in conjunctive normal form. */
string RSExporter::stateConstrToStr(const StateConstr * guard) {
    string expr;

    switch (guard->oper) {
        case STC_PV: 
            return guard->proc_name + "_" + guard->entity_name + "=1";
        
        case STC_TF:
            return guard->tf ? "true" : "false";
        
        case STC_AND:
            return "(" + stateConstrToStr(guard->arg[0]) + " and " + stateConstrToStr(guard->arg[1]) + ")";

        case STC_OR:
            return "(" + stateConstrToStr(guard->arg[0]) + " or " + stateConstrToStr(guard->arg[1]) + ")";
    
        case STC_NOT:
            expr = stateConstrToStr(guard->arg[0]);
            return  expr.substr(0, expr.length()-1) + "0";

        default:
            return "??";
            assert(0);
    }   
}


string RSExporter::reactionCondToStr(const Reaction & reaction) {
    string cond;

    bool moreRctts {false};

    for (const Entity & e : reaction.rctt) {
        if (moreRctts)
            cond += "*";
        else
            moreRctts = true;
        
        cond += rs->getEntityName(e) + "_in";
    }

    for (const Entity & e : reaction.inhib) 
        cond += "*(1-" + rs->getEntityName(e) + "_in)";

    return cond;
}


string RSExporter::appendCondition(string & oldCond, string & newCond) {
    return "(" + oldCond + ") + " + newCond + " - (" + oldCond + ") * " + newCond;
}


string RSExporter::formulaToStr(const FormRSCTLK * form) {
    string varStr;
    string labelStr;

    switch (form->oper) {

        case RSCTLK_PV: // propositional variable
            varStr = form->proc_name + "." + form->entity_name + "_out=1";
            
            if (atoms.find(varStr) == atoms.end()) {
                labelStr =  "atomic_" + to_string(atoms.size());
                atoms[varStr] = labelStr;
            }
            else {
                labelStr = atoms[varStr];
            }
            
            return labelStr;
            
        case RSCTLK_AND:
            return "(" + formulaToStr(form->arg[0]) + " and " + formulaToStr(form->arg[1]) + ")";
        
        case RSCTLK_OR:
            return "(" + formulaToStr(form->arg[0]) + " or " + formulaToStr(form->arg[1]) + ")";
            
        case RSCTLK_XOR:
            return "((" + formulaToStr(form->arg[0]) + " or " + formulaToStr(form->arg[1]) + ") and !(" + 
                      formulaToStr(form->arg[0]) + " and " + formulaToStr(form->arg[1]) + "))";

        case RSCTLK_NOT:
            return "!(" + formulaToStr(form->arg[0]) +")";

        case RSCTLK_IMPL:
            return "(" + formulaToStr(form->arg[0]) + " -> " + formulaToStr(form->arg[1]) + ")";

        case  RSCTLK_EG:  // Existential...
            return "EG(" + formulaToStr(form->arg[0]) + ")";

        case  RSCTLK_EU:
            return "E(" + formulaToStr(form->arg[0]) + " U " + formulaToStr(form->arg[1]) + ")";

        case  RSCTLK_EX:
            return "EX(" + formulaToStr(form->arg[0]) + ")";

        case  RSCTLK_EF:
            return "EF(" + formulaToStr(form->arg[0]) + ")";

        case  RSCTLK_AG: // Universal...
            return "AG(" + formulaToStr(form->arg[0]) + ")";

        case  RSCTLK_AU:
            return "A(" + formulaToStr(form->arg[0]) + " U " + formulaToStr(form->arg[1]) + ")";

        case  RSCTLK_AX:
            return "AX(" + formulaToStr(form->arg[0]) + ")";

        case  RSCTLK_AF:
            return "AF(" + formulaToStr(form->arg[0]) + ")";

        case  RSCTLK_UK: // Epistemic operators
            return "K(" + form->getSingleAgent() + ", " + formulaToStr(form->arg[0]) + ")";

        default:
            assert(0);
            return "??";
    }
}
