#include "mc.hh"

ModelChecker::ModelChecker(SymRS *srs, Options *opts)
{
    this->srs = srs;
    this->opts = opts;
    
	cuddMgr = srs->getCuddMgr();
	
	initStates = srs->getEncInitStates();
	
    totalStateVars = srs->getTotalStateVars();
    
	pv = srs->getEncPV();
    pv_succ = srs->getEncPVsucc();
    pv_E = srs->getEncPV_E();
    pv_succ_E = srs->getEncPVsucc_E();
    pv_act_E = srs->getEncPVact_E();

    //
	// Transition relations
	//
	//	trp -- partitioned TR
	//	trm -- monolithic TR
	//
	// If we use trp, then trm is nullptr (same for trm)
	//
	trp = srs->getEncPartTrans();
    if (trp == nullptr) 
		trp_size = 0;
    else 
		trp_size = trp->size();	
    trm = srs->getEncMonoTrans();
    
	if (srs->usingContextAutomaton())
	{
		// ca_init_state = srs->getEncCtxAutInitState();
		pv_ca = srs->getEncCtxAutPV();
		pv_ca_succ = srs->getEncCtxAutPVsucc();
		ca_tr = srs->getEncCtxAutTrans();
	}
	
	// Initialise the set of reachable states
	reach = nullptr;
}

inline BDD ModelChecker::getSucc(const BDD &states)
{
    BDD q = BDD_TRUE;

    VERB_L2("Computing successors");
    if (opts->part_tr_rel)
    {
        for (unsigned int i = 0; i < trp_size; ++i)
        {
            q *= states * (*trp)[i];
        }
    }
    else
    {
        q *= states * *trm;
    }
    q = (q.ExistAbstract(*pv_E)).SwapVariables(*pv_succ, *pv);
    q = q.ExistAbstract(*pv_act_E);

    return q;
}

inline BDD ModelChecker::getPreE(const BDD &states)
{
    BDD q = BDD_TRUE;
    VERB_L2("Computing preE");
    BDD x = states.SwapVariables(*pv, *pv_succ);
    if (opts->part_tr_rel)
    {
        for (unsigned int i = 0; i < trp_size; ++i)
            q *= x * (*trp)[i];
    }
    else
    {
        q *= x * *trm;
    }
    q = q.ExistAbstract(*pv_succ_E);
    q = q.ExistAbstract(*pv_act_E);
    return q;
}

inline BDD ModelChecker::getPreEctx(const BDD &states, const BDD *contexts)
{
    BDD q = BDD_TRUE;
    VERB_L2("Computing (context-restricted) preE");
    BDD x = states.SwapVariables(*pv, *pv_succ);
    if (opts->part_tr_rel)
    {
        for (unsigned int i = 0; i < trp_size; ++i)
            q *= x * (*trp)[i] * *contexts;
    }
    else
    {
        q *= x * *trm * *contexts;
    }
    q = q.ExistAbstract(*pv_succ_E);
    q = q.ExistAbstract(*pv_act_E);
    return q;
}

void ModelChecker::printReach(void)
{
	VERB_LN(2, "Printing/generating reachable states");
	
    if (opts->measure)
        opts->ver_time = cpuTime();

	assert(initStates != nullptr);
	
    BDD *reach = new BDD(*initStates);
    BDD reach_p = BDD_FALSE;

    unsigned int k = 0;

    while (*reach != reach_p)
    {
        if (opts->show_progress)
        {
            cout << "\rIteration " << ++k << flush;
        }
        reach_p = *reach;
        *reach += getSucc(*reach);
    }

    srs->printDecodedStates(*reach);

    cleanup();

    if (opts->measure)
    {
        opts->ver_time = cpuTime() - opts->ver_time;
        opts->ver_mem = memUsed();
    }
}

void ModelChecker::printReachWithSucc(void)
{
	VERB_LN(2, "Printing/generating reachable states (with successors)");
	
    BDD *reach = new BDD(*initStates);
    BDD reach_p = cuddMgr->bddZero();

    while (*reach != reach_p)
    {
        reach_p = *reach;
        BDD newStates = getSucc(*reach) - *reach;
        *reach += newStates;

    }

    BDD unproc = *reach;
    while (!unproc.IsZero())
    {
        BDD t;
        t = unproc.PickOneMinterm(*pv);
        cout << "Successors of " << srs->decodedStateToStr(t) << ":" << endl;
        srs->printDecodedStates(getSucc(t));
        unproc -= t;
    }
    cleanup();
}

bool ModelChecker::checkReach(const Entities testState)
{
    if (opts->measure)
        opts->ver_time = cpuTime();

    BDD st = srs->getEncState(testState);

    BDD reach = *initStates;
    BDD reach_p = cuddMgr->bddZero();

    while (reach != reach_p)
    {
        if (reach * st != cuddMgr->bddZero())
        {
            cleanup();
            return true;
        }
        reach_p = reach;
        reach += getSucc(reach);
    }

    cleanup();

    if (opts->measure)
    {
        opts->ver_time = cpuTime() - opts->ver_time;
        opts->ver_mem = memUsed();
    }

    return false;
}

BDD ModelChecker::getStatesRSCTL(const FormRSCTL *form)
{
    assert(reach != nullptr);
    Oper oper = form->getOper();
    if (oper == RSCTL_PV)
    {
        return *form->getBDD() * *reach;
    }
    else if (oper == RSCTL_TF)
    {
        if (form->getTF() == true)
            return *reach;
        else
            return cuddMgr->bddZero();
    }
    else if (oper == RSCTL_AND)
    {
        return getStatesRSCTL(form->getLeftSF()) * getStatesRSCTL(form->getRightSF());
    }
    else if (oper == RSCTL_OR)
    {
        return getStatesRSCTL(form->getLeftSF()) + getStatesRSCTL(form->getRightSF());
    }
    else if (oper == RSCTL_XOR)
    {
        return getStatesRSCTL(form->getLeftSF()) ^ getStatesRSCTL(form->getRightSF());
    }
    else if (oper == RSCTL_IMPL)
    {
        return (!getStatesRSCTL(form->getLeftSF()) * *reach) + getStatesRSCTL(form->getRightSF());
    }
    else if (oper == RSCTL_NOT)
    {
        return !getStatesRSCTL(form->getLeftSF()) * *reach;
    }
    else if (oper == RSCTL_EX)
    {
        return getPreE(getStatesRSCTL(form->getLeftSF())) * *reach;
    }
    else if (oper == RSCTL_EG)
    {
        return statesEG(getStatesRSCTL(form->getLeftSF()));
    }
    else if (oper == RSCTL_EU)
    {
        return statesEU(
                getStatesRSCTL(form->getLeftSF()),
                getStatesRSCTL(form->getRightSF())
                );
    }
    else if (oper == RSCTL_EF)
    {
        return statesEF(getStatesRSCTL(form->getLeftSF()));
    }
    else if (oper == RSCTL_AX)
    {
        return !getPreE(!getStatesRSCTL(form->getLeftSF()) * *reach) * *reach;
    }
    else if (oper == RSCTL_AG)
    {
        return !statesEF(
                !getStatesRSCTL(form->getLeftSF()) * *reach) * *reach;
    }
    else if (oper == RSCTL_AU)
    {
        BDD ng = !getStatesRSCTL(form->getRightSF()) * *reach;
        BDD nf = !getStatesRSCTL(form->getLeftSF()) * *reach;

        BDD x = !statesEU(ng, ng * nf) * *reach;
        if (!x.IsZero()) 
            x = x * !statesEG(ng) * *reach;

        return x; 
    }
    else if (oper == RSCTL_AF)
    {
        return !statesEG(
                !getStatesRSCTL(form->getLeftSF()) * *reach) * *reach;
    }
    /***** CONTEXT RESTRICTIONS: ******/
    else if (oper == RSCTL_EX_ACT) 
    {
        return getPreEctx(getStatesRSCTL(form->getLeftSF()), form->getActionsBDD()) * *reach;
    }
    else if (oper == RSCTL_EG_ACT)
    {
        return statesEGctx(form->getActionsBDD(), getStatesRSCTL(form->getLeftSF())); /***** EG? *****/
    }
    else if (oper == RSCTL_EU_ACT)
    {
        return statesEUctx(
                    form->getActionsBDD(),
                    getStatesRSCTL(form->getLeftSF()),
                    getStatesRSCTL(form->getRightSF())
                );
    }
    else if (oper == RSCTL_EF_ACT)
    {
        return statesEFctx(form->getActionsBDD(), getStatesRSCTL(form->getLeftSF()));
    }
    else if (oper == RSCTL_AX_ACT)
    {
        return !getPreEctx(!getStatesRSCTL(form->getLeftSF()) * *reach, form->getActionsBDD()) * *reach;
    }
    else if (oper == RSCTL_AG_ACT)
    {
        return !statesEFctx(form->getActionsBDD(),
                !getStatesRSCTL(form->getLeftSF()) * *reach) * *reach;
    }
    else if (oper == RSCTL_AU_ACT)
    {
        BDD ng = !getStatesRSCTL(form->getRightSF()) * *reach;
        BDD nf = !getStatesRSCTL(form->getLeftSF()) * *reach;

        BDD x = !statesEUctx(form->getActionsBDD(), ng, ng * nf) * *reach; 
        if (!x.IsZero()) 
            x = x * !statesEGctx(form->getActionsBDD(), ng) * *reach;

        return x; 
    }
    else if (oper == RSCTL_AF_ACT)
    {
        return !statesEGctx(form->getActionsBDD(),
               !getStatesRSCTL(form->getLeftSF()) * *reach) * *reach;
    }

    assert(0); // Should never happen
    return BDD_FALSE;
}

BDD ModelChecker::statesEG(const BDD &states)
{
    BDD x = states;
    BDD x_p = cuddMgr->bddZero();
    while (x != x_p)
    {
        x_p = x;
        x = x * getPreE(x);
    }
    return x;
}

BDD ModelChecker::statesEU(const BDD &statesA, const BDD &statesB)
{
    BDD x = statesA;
    BDD x_p = *reach;
    while (x != x_p)
    {
        x_p = x;
        x = x + (statesA * getPreE(x));
    }
    return x;
}

BDD ModelChecker::statesEF(const BDD &states)
{
    BDD x = states;
    BDD x_p = *reach;
    while (x != x_p)
    {
        x_p = x;
        x = x + (*reach * getPreE(x));
    }
    return x;
}

BDD ModelChecker::statesEGctx(const BDD *contexts, const BDD &states)
{
    BDD x = states;
    BDD x_p = cuddMgr->bddZero();
    while (x != x_p)
    {
        x_p = x;
        x = x * getPreEctx(x, contexts);
    }
    return x;
}

BDD ModelChecker::statesEUctx(const BDD *contexts, const BDD &statesA, const BDD &statesB)
{
    BDD x = statesA;
    BDD x_p = *reach;
    while (x != x_p)
    {
        x_p = x;
        x = x + (statesA * getPreEctx(x, contexts));
    }
    return x;
}

BDD ModelChecker::statesEFctx(const BDD *contexts, const BDD &states)
{
    BDD x = states;
    BDD x_p = *reach;
    while (x != x_p)
    {
        x_p = x;
        x = x + (*reach * getPreEctx(x, contexts));
    }
    return x;
}

bool ModelChecker::checkRSCTL(FormRSCTL *form)
{
    if (form->isERSCTL())
        return checkRSCTLbmc(form);
    else
        return checkRSCTLfull(form);
}

bool ModelChecker::checkRSCTLfull(FormRSCTL *form)
{
    if (opts->measure)
        opts->ver_time = cpuTime();

    assert(form != nullptr);

    bool result = false;

    VERB("Model checking for RSCTL formula: " << form->toStr());

    VERB("Processing the formula: encoding entities");
    form->encodeEntities(srs);
    VERB("Entities encoded");

    VERB("Processing the formula: encoding actions/contexts");
    form->encodeActions(srs);
    VERB("Contexts encoded");

    assert(reach == nullptr);

    reach = new BDD(*initStates);
    BDD reach_p = cuddMgr->bddZero();

    VERB("Generating state space");

    unsigned int k = 0;

    while (*reach != reach_p)
    {

        if (opts->show_progress)
        {
            cout << "\rIteration " << ++k << flush;
        }

        if (opts->reorder_reach)
        {
            VERB_L2("Reordering")
            Cudd_ReduceHeap(cuddMgr->getManager(), CUDD_REORDER_SIFT, 10000);
        }

        reach_p = *reach;
        *reach += getSucc(*reach);
    }

    if (opts->show_progress) cout << endl;

    VERB("Checking the formula");

    //if (*initStates * getStatesRSCTL(form) != cuddMgr->bddZero())
	if (*initStates * getStatesRSCTL(form) == *initStates)
    {
        result = true;
    }
    else
    {
        result = false;
    }

    cleanup(); 

    cout << "Formula " << form->toStr() << (result ? " holds" : " does not hold") << endl;

    if (opts->measure)
    {
        opts->ver_time = cpuTime() - opts->ver_time;
        opts->ver_mem = memUsed();
    }

    return result;
}

bool ModelChecker::checkRSCTLbmc(FormRSCTL *form)
{
    if (opts->measure)
        opts->ver_time = cpuTime();

    assert(form != nullptr);

    if (!form->isERSCTL())
    {
        FERROR("Formula " << form->toStr() << " is not syntactically an ERSCTL formula");
    }

    bool result = false;

    VERB("Bounded model checking for RSCTL formula: " << form->toStr());

    VERB("Processing the formula: encoding entities");
    form->encodeEntities(srs);
    VERB("Entities encoded");

    VERB("Processing the formula: encoding actions/contexts");
    form->encodeActions(srs);
    VERB("Contexts encoded");

    assert(reach == nullptr);

    reach = new BDD(*initStates);
    BDD reach_p = cuddMgr->bddZero();

    unsigned int k = 0;

    while (*reach != reach_p)
    {
        if (opts->show_progress)
        {
            cout << "\rIteration " << ++k << flush;
        }

        //if (*initStates * getStatesRSCTL(form) != cuddMgr->bddZero())
	    if (*initStates * getStatesRSCTL(form) == *initStates)
        {
            result = true;
            break;
        }

        reach_p = *reach;
        *reach += getSucc(*reach);
    }

    if (opts->show_progress) cout << endl;

    cleanup(); 

    cout << "Formula " << form->toStr() << " " << (result ? "holds" : "does not hold") << endl;

    if (opts->measure)
    {
        opts->ver_time = cpuTime() - opts->ver_time;
        opts->ver_mem = memUsed();
    }

    return result;
}

void ModelChecker::cleanup(void)
{
    delete reach;
    reach = nullptr;
}

/** EOF **/