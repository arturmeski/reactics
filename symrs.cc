/*
    Copyright (c) 2012-2018
    Artur Meski <meski@ipipan.waw.pl>
*/

#include "symrs.hh"

BDD SymRS::encEntity_raw(Entity entity, bool succ) const
{
    BDD r;

    if (succ)
        r = (*pv_succ)[entity];
    else
        r = (*pv)[entity];

    return r;
}

BDD SymRS::encEntitiesConj_raw(const Entities &entities, bool succ)
{
    BDD r = BDD_TRUE;

    for (auto entity = entities.begin(); entity != entities.end(); ++entity)
    {
        if (succ) r *= encEntitySucc(*entity);
        else r *= encEntity(*entity);
    }

    return r;
}

BDD SymRS::encEntitiesDisj_raw(const Entities &entities, bool succ)
{
    BDD r = BDD_FALSE;

    for (auto entity = entities.begin(); entity != entities.end(); ++entity)
    {
        if (succ) r += encEntitySucc(*entity);
        else r += encEntity(*entity);
    }

    return r;
}

BDD SymRS::encStateActEntitiesConj(const Entities &entities)
{
    BDD r = BDD_TRUE;

    for (auto entity = entities.begin(); entity != entities.end(); ++entity)
    {
        BDD state_act = encEntity(*entity);
        int actEntity;
		
		// if entity is also an aciton entity, we include it in the encoding
        if ((actEntity = getMappedStateToActID(*entity)) >= 0)
            state_act += encActEntity(actEntity);
        
		r *= state_act;
    }

    return r;
}

BDD SymRS::encStateActEntitiesDisj(const Entities &entities)
{
    BDD r = BDD_FALSE;

    for (auto entity = entities.begin(); entity != entities.end(); ++entity)
    {
        BDD state_act = encEntity(*entity);
        int actEntity;

		// if entity is also an aciton entity, we include it in the encoding
        if ((actEntity = getMappedStateToActID(*entity)) >= 0)
            state_act += encActEntity(actEntity);
		
        r += state_act;
    }

    return r;
}

BDD SymRS::compState(const BDD &state) const
{
    BDD s = state;

    for (unsigned int i = 0; i < totalStateVars; ++i)
    {
        if (!(*pv)[i] * state != cuddMgr->bddZero())
            s *= !(*pv)[i];
    }

    return s;
}

BDD SymRS::compContext(const BDD &context) const
{
    BDD c = context;

    for (unsigned int i = 0; i < totalActions; ++i)
    {
        if (!(*pv_act)[i] * context != cuddMgr->bddZero())
            c *= !(*pv_act)[i];
    }

    return c;
}

std::string SymRS::decodedStateToStr(const BDD &state)
{
    std::string s = "{ ";
    for (unsigned int i = 0; i < totalStateVars; ++i)
    {
        if (!(encEntity(i) * state).IsZero())
        {
            s += rs->entityToStr(i) + " ";
        }
    }
    s += "}";
    return s;
}

void SymRS::printDecodedStates(const BDD &states)
{
    BDD unproc = states;
    while (!unproc.IsZero())
    {
        BDD t = unproc.PickOneMinterm(*pv);
        cout << decodedStateToStr(t) << endl;
        if (opts->verbose > 9) {
            t.PrintMinterm();
            cout << endl;
        }
        unproc -= t;
    }
}

void SymRS::initBDDvars(void)
{
	VERB("Initialising CUDD");
	
    cuddMgr = new Cudd(0,0);

    VERB("Preparing BDD variables");
	
    pv = new vector<BDD>(totalStateVars);
    pv_succ = new vector<BDD>(totalStateVars);
    pv_act = new vector<BDD>(totalActions);
    pv_E = new BDD(BDD_TRUE);
    pv_succ_E = new BDD(BDD_TRUE);
    pv_act_E = new BDD(BDD_TRUE);

    for (unsigned int i = 0; i < totalStateVars; ++i)
    {
        (*pv)[i] = cuddMgr->bddVar(i*2);
        (*pv_succ)[i] = cuddMgr->bddVar((i*2)+1);

        *pv_E *= (*pv)[i];
        *pv_succ_E *= (*pv_succ)[i];
    }

    unsigned int offset = totalStateVars * 2;
	
    for (unsigned int i = 0; i < totalActions; ++i)
    {
        (*pv_act)[i] = cuddMgr->bddVar(offset+i);
        *pv_act_E *= (*pv_act)[i];
    }

	offset += totalActions;

	VERB("Context automaton variables");

	pv_ca = new vector<BDD>(totalCtxAutStateVars);
	pv_ca_succ = new vector<BDD>(totalCtxAutStateVars);
	pv_ca_E = new BDD(BDD_TRUE);
	pv_ca_succ_E = new BDD(BDD_TRUE);
	
	//
	// BDD variables for encoding local states of context automaton
	//
	unsigned int base_index = offset;
	for (unsigned int i = 0; i < totalCtxAutStateVars; ++i)
	{
		(*pv_ca)[i] = cuddMgr->bddVar(base_index);
		(*pv_ca_succ)[i] = cuddMgr->bddVar(base_index+1);
		
		*pv_ca_E *= (*pv_ca)[i];
		*pv_ca_succ_E *= (*pv_ca_succ)[i];
	
		base_index += 2;
	}

    VERB("All BDD variables ready");
}

void SymRS::encodeTransitions(void)
{
    DecompReactions dr;

    VERB("Decomposing reactions");
    for (unsigned int i = 0; i < totalReactions; ++i)
    {
        ReactionCond cond;
        cond.rctt = rs->reactions[i].rctt;
        cond.inhib = rs->reactions[i].inhib;
    
        for (Entities::iterator p = rs->reactions[i].prod.begin();
                p != rs->reactions[i].prod.end(); ++p)
        {
            dr[*p].push_back(cond);
        }
    }

    VERB("Encoding reactions");

    if (opts->part_tr_rel)
    {
        VERB("Using partitioned transition relation encoding");
        partTrans = new vector<BDD>(totalStateVars);
    }
    else
    {
        VERB("Using monolithic transition relation encoding");
        monoTrans = new BDD(BDD_TRUE);
    }

    for (unsigned int p = 0; p < totalStateVars; ++p)
    {
        VERB_L3("Encoding for successor " << p);

        DecompReactions::iterator di;

        if ((di = dr.find(p)) == dr.end())
        {
            // there is no reaction producing p:
            if (opts->part_tr_rel)
                (*partTrans)[p] = !encEntitySucc(p);
            else
            {
                *monoTrans *= !encEntitySucc(p);
            }
        }
        else
        {
            // di - reactions producing p
            
            BDD conditions = BDD_FALSE;

            assert(di->second.size() > 0);

            for (unsigned int j = 0; j < di->second.size(); ++j)
            {
                conditions += encStateActEntitiesConj(di->second[j].rctt) * !encStateActEntitiesDisj(di->second[j].inhib);
            }

            if (opts->part_tr_rel)
            {
                (*partTrans)[p] = conditions * encEntitySucc(p);
                (*partTrans)[p] += !conditions * !encEntitySucc(p);
            }
            else
            {
                *monoTrans *= (conditions * encEntitySucc(p)) + (!conditions * !encEntitySucc(p));
            }
        }
        if (opts->reorder_trans)
        {
            VERB_L2("Reordering");
            Cudd_ReduceHeap(cuddMgr->getManager(), CUDD_REORDER_SIFT, 10000);
        }

    }

    VERB("Reactions ready");
}

BDD SymRS::getEncState(const Entities &entities)
{
    assert(0);
    //BDD state = compState(encEntitiesConj(rs->initState));
    //for (RctSys::Entities::iterator at = rs->actionEntities.begin(); at != rs->actionEntities.end(); ++at)
    //{
    //    state = state.ExistAbstract(encEntity(*at));
    //}
    return BDD_FALSE;
}

BDD SymRS::encNoContext(void)
{
	BDD noContextBDD = BDD_TRUE;

    for (unsigned int i = 0; i < totalActions; ++i)
    {
        noContextBDD *= !(*pv_act)[i];
    }

	return noContextBDD;
}

void SymRS::encodeInitStates(void)
{
    VERB("Encoding initial states");

#ifndef NDEBUG
    if (opts->part_tr_rel)
        assert(partTrans != nullptr);
#endif

    initStates = new BDD(BDD_FALSE);
		
    for (auto state = rs->initStates.begin();
            state != rs->initStates.end();
            ++state)
    {
        VERB("Encoding a single inital state");
        BDD newInitState = compState(encEntitiesConj(*state)); 
        BDD q = BDD_TRUE;
        if (opts->part_tr_rel)
        {
            for (unsigned int i = 0; i < partTrans->size(); ++i)
            {
                q *= newInitState * (*partTrans)[i] * encNoContext();
            }
        }
        else
        {
            q *= newInitState * *monoTrans * encNoContext();
        }
		
        q = (q.ExistAbstract(*pv_E)).SwapVariables(*pv_succ, *pv);
        q = q.ExistAbstract(*pv_act_E);

        *initStates += q;
    }

    VERB("Initial states encoded");
}

void SymRS::mapStateToAct(void)
{
    VERB("Mapping state variables to action variables");
    unsigned int j = 0;
    for (unsigned int i = 0; i < totalStateVars; ++i)
    {
        if (rs->isActionEntity(i)) {
            stateToAct.push_back(j++);
        }
        else
        {
            stateToAct.push_back(-1);
        }
    }
	const unsigned int verbosity_level = 9;
    if (opts->verbose > verbosity_level)
    {
        for (unsigned int i = 0; i < stateToAct.size(); ++i)
        {
            cout << "ii VERBOSE(" << verbosity_level << "): stateToAct[" << i << "] = " << stateToAct[i] << endl;
        }
    }
}

void SymRS::encode(void)
{
    VERB("Encoding...");

    if (opts->measure)
    {
        opts->enc_time = cpuTime();
        opts->enc_mem = memUsed();
    }

    mapStateToAct();

    initBDDvars();
    encodeTransitions();
    encodeInitStates();

    if (opts->measure)
    {
        opts->enc_time = cpuTime() - opts->enc_time;
        opts->enc_mem = memUsed() - opts->enc_mem;
    }

    VERB("Encoding done");
}

BDD SymRS::encActStrEntity(std::string name) const 
{
    int id = getMappedStateToActID(rs->getEntityID(name));
	if (id < 0) 
	{
		FERROR("Entity \"" << name << "\" not defined as context entity");
		return BDD_FALSE;
	} else {
		return encActEntity(getMappedStateToActID(rs->getEntityID(name)));
	}
}

size_t SymRS::getCtxAutStateEncodingSize(void)
{
    size_t bitCount = 0;
    size_t bitCountMaxVal = 1;
    size_t numStates = rs->ctx_aut->statesCount();
    while (bitCountMaxVal <= numStates)
    {
        bitCount++;
        bitCountMaxVal *= 2;
    }
    return bitCount;
}

BDD SymRS::encCtxAutState_raw(State state_id, bool succ) const
{
	// select appropriate BDD vector
	vector<BDD> *enc_vec;
    if (succ)
        enc_vec = pv_ca_succ;
    else
        enc_vec = pv_ca;

    BDD r;
	State val = state_id;

	for (unsigned int i = 0; i < totalCtxAutStateVars; ++i)
	{
		if (val != 0)
		{
			if (val % 2 == 1)
				r *= (*enc_vec)[i];
			else
				r *= !(*enc_vec)[i];
			val /= 2;
		}
		else
			r *= !(*enc_vec)[i];
	}

    return r;
}

BDD *SymRS::getEncCtxAutInitState(void)
{
	return new BDD(BDD_TRUE);
}

vector<BDD> *SymRS::getEncCtxAutPV(void)
{
	return new vector<BDD>();
}

vector<BDD> *SymRS::getEncCtxAutPVsucc(void)
{
	return new vector<BDD>();
}

BDD *SymRS::getEncCtxAutTrans(void)
{
	return new BDD(BDD_TRUE);
}

/** EOF **/
