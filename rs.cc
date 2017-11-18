/*
    Copyright (c) 2012-2014
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#include "rs.hh"

bool RctSys::hasAtom(std::string name)
{
    if (atoms_names.find(name) == atoms_names.end())
        return false;
    else
        return true;
}

void RctSys::addAtom(std::string name)
{
    if (!hasAtom(name))
    {
        Atom new_atom_id = atoms_ids.size();

        VERB_L2("Adding atom: " << name << " index=" << new_atom_id);

        atoms_ids.push_back(name);
        atoms_names[name] = new_atom_id;
    }
}

std::string RctSys::getAtomName(Atom atomID)
{
    if (atomID < atoms_ids.size())
        return atoms_ids[atomID];
    else
    {
        FERROR("No such atom ID: " << atomID);
        return "??";
    }
}

RctSys::Atom RctSys::getAtomID(std::string name)
{
    if (!hasAtom(name))
    {
        FERROR("No such atom: " << name);
    }
    return atoms_names[name];
}

void RctSys::pushReactant(std::string atomName)
{
    if (!hasAtom(atomName))
        addAtom(atomName);
    tmpReactants.insert(getAtomID(atomName));
}
void RctSys::pushInhibitor(std::string atomName)
{
    if (!hasAtom(atomName))
        addAtom(atomName);
    tmpInhibitors.insert(getAtomID(atomName));
}
void RctSys::pushProduct(std::string atomName)
{
    if (!hasAtom(atomName))
        addAtom(atomName);
    tmpProducts.insert(getAtomID(atomName));
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

std::string RctSys::atomsToStr(const Atoms &atoms)
{
    std::string s = " ";
    for (auto a = atoms.begin(); a != atoms.end(); ++a)
    {
        s += atomToStr(*a) + " ";
    }
    return s;
}

void RctSys::showReactions(void)
{
    cout << "# Reactions:" << endl;
    for (auto r = reactions.begin(); r != reactions.end(); ++r)
    {
        cout << " * (R={" << atomsToStr(r->rctt) << "},"
             << "I={" << atomsToStr(r->inhib) << "}," 
             << "P={" << atomsToStr(r->prod) << "})" << endl;
    } 
}

void RctSys::pushStateAtom(std::string atomName)
{
    if (!hasAtom(atomName))
    {
        FERROR("No such entity: " << atomName);
    }
    tmpState.insert(getAtomID(atomName)); 
}

void RctSys::commitInitState(void)
{
    initStates.insert(tmpState); 
    tmpState.clear();
}


void RctSys::addActionAtom(std::string atomName)
{
    if (!hasAtom(atomName))
        addAtom(atomName);
    actionAtoms.insert(getAtomID(atomName));
}

bool RctSys::isActionAtom(Atom atom)
{
    if (actionAtoms.count(atom) > 0)
        return true;
    else
        return false;
}

void RctSys::showActionAtoms(void)
{
    cout << "# Context entities:";
    for (auto a = actionAtoms.begin(); a != actionAtoms.end(); ++a)
    {
        cout << " " << getAtomName(*a);
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
            cout << " " << getAtomName(*a);
        }
        cout << endl;
    }
}

void RctSys::printSystem(void)
{
    showInitialStates();
    showActionAtoms();
    showReactions();

}
