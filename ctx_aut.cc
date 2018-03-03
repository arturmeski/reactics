
#include "ctx_aut.hh"

bool CtxAut::hasState(std::string name)
{
    if (states_names.find(name) == states_names.end())
        return false;
    else
        return true;
}

State CtxAut::getStateID(std::string name)
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

void CtxAut::printAutomaton(void)
{
	showStates();
}

void CtxAut::showStates(void)
{
	cout << "# Context Automaton States:" << endl;
	for (const auto &s : states_ids)
		cout << " * " << s << endl;
}

void CtxAut::pushContextEntity(Entity entity_id) 
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

/** EOF **/
