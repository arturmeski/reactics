/*
    Copyright (c) 2012-2014
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#include "rs.hh"

bool RctSys::hasEntity(std::string name)
{
    if (entities_names.find(name) == entities_names.end())
        return false;
    else
        return true;
}

void RctSys::addEntity(std::string name)
{
    if (!hasEntity(name))
    {
        Entity new_entity_id = entities_ids.size();

        VERB_L2("Adding entity: " << name << " index=" << new_entity_id);

        entities_ids.push_back(name);		
        entities_names[name] = new_entity_id;
    }
}

std::string RctSys::getEntityName(Entity entityID)
{
    if (entityID < entities_ids.size())
        return entities_ids[entityID];
    else
    {
        FERROR("No such entity ID: " << entityID);
        return "??";
    }
}

RctSys::Entity RctSys::getEntityID(std::string name)
{
    if (!hasEntity(name))
    {
        FERROR("No such entity: " << name);
    }
    return entities_names[name];
}

void RctSys::pushReactant(std::string entityName)
{
    if (!hasEntity(entityName))
        addEntity(entityName);
    tmpReactants.insert(getEntityID(entityName));
}
void RctSys::pushInhibitor(std::string entityName)
{
    if (!hasEntity(entityName))
        addEntity(entityName);
    tmpInhibitors.insert(getEntityID(entityName));
}
void RctSys::pushProduct(std::string entityName)
{
    if (!hasEntity(entityName))
        addEntity(entityName);
    tmpProducts.insert(getEntityID(entityName));
}

void RctSys::commitReaction(void)
{
    VERB_L3("Saving reaction");

    Reaction r;

    r.rctt = tmpReactants;
    r.inhib = tmpInhibitors;
    r.prod = tmpProducts;

    reactions.push_back(r);

    tmpReactants.clear();
    tmpInhibitors.clear();
    tmpProducts.clear();
}

std::string RctSys::entitiesToStr(const Entities &entities)
{
    std::string s = " ";
    for (auto a = entities.begin(); a != entities.end(); ++a)
    {
        s += entityToStr(*a) + " ";
    }
    return s;
}

void RctSys::showReactions(void)
{
    cout << "# Reactions:" << endl;
    for (auto r = reactions.begin(); r != reactions.end(); ++r)
    {
        cout << " * (R={" << entitiesToStr(r->rctt) << "},"
             << "I={" << entitiesToStr(r->inhib) << "}," 
             << "P={" << entitiesToStr(r->prod) << "})" << endl;
    } 
}

void RctSys::pushStateEntity(std::string entityName)
{
    if (!hasEntity(entityName))
    {
        FERROR("No such entity: " << entityName);
    }
    tmpState.insert(getEntityID(entityName)); 
}

void RctSys::commitInitState(void)
{
    initStates.insert(tmpState); 
    tmpState.clear();
}


void RctSys::addActionEntity(std::string entityName)
{
    if (!hasEntity(entityName))
        addEntity(entityName);
    actionEntities.insert(getEntityID(entityName));
}

bool RctSys::isActionEntity(Entity entity)
{
    if (actionEntities.count(entity) > 0)
        return true;
    else
        return false;
}

void RctSys::showActionEntities(void)
{
    cout << "# Context entities:";
    for (auto a = actionEntities.begin(); a != actionEntities.end(); ++a)
    {
        cout << " " << getEntityName(*a);
    }
    cout << endl;
}

void RctSys::showInitialStates(void)
{
    cout << "# Initial states:" << endl;
    for (auto s = initStates.begin(); s != initStates.end(); ++s)
    {
        cout << " *";
        for (auto a = s->begin(); a != s->end(); ++a)
        {
            cout << " " << getEntityName(*a);
        }
        cout << endl;
    }
}

void RctSys::printSystem(void)
{
    showInitialStates();
    showActionEntities();
    showReactions();
}

bool CtxAut::hasState(std::string name)
{
    if (states_names.find(name) == states_names.end())
        return false;
    else
        return true;
}

CtxAut::State CtxAut::getStateID(std::string name)
{
    if (!hasState(name))
    {
        FERROR("No such state: " << name);
    }
    return states_names[name];
}

void CtxAut::addState(std::string name)
{
    if (!hasState(name))
    {
        State new_state_id = states_ids.size();

        VERB_L2("Adding state: " << name << " index=" << new_state_id);

        states_ids.push_back(name);
        states_names[name] = new_state_id;
    }
}

void CtxAut::pushContextEntity(RctSys::Entity entity_id) 
{
	tmpEntities.insert(entity_id);
}

void CtxAut::addTransition(std::string srcStateName, std::string dstStateName) 
{
    VERB_L3("Saving transition");
	
	Transition new_transition;
	
	new_transition.src_state = getStateID(srcStateName);
	new_transition.ctx = tmpEntities; 
	tmpEntities.clear();
	new_transition.dst_state = getStateID(dstStateName);
}

