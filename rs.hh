/*
    Copyright (c) 2012-2014
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#ifndef RS_RS_HH
#define RS_RS_HH

#include <iostream>
#include <set>
#include <map>
#include <vector>
#include <string>
#include <cstdlib>
#include "macro.hh"
#include "options.hh"
#include "memtime.hh"

using std::cout;
using std::endl;

class RctSys
{
    friend class SymRS;
    friend class SymRSstate;
public:
    typedef unsigned int Atom;
    typedef std::set<Atom> Atoms;
    struct Reaction {
        Atoms rctt;
        Atoms inhib;
        Atoms prod;
    };
    typedef std::vector<Reaction> Reactions;
    typedef std::vector<std::string> AtomsByIds;
    typedef std::map<std::string, Atom> AtomsByName;
    typedef std::set<Atoms> AtomsSets;
private:
    Reactions reactions;
    AtomsSets initStates;

    Atoms actionAtoms;

    AtomsByIds atoms_ids;
    AtomsByName atoms_names;

    Atoms tmpReactants;
    Atoms tmpInhibitors;
    Atoms tmpProducts;

    Atoms tmpState;

    Atom getAtomID(std::string atomName);

    Options *opts;

public:
    void setOptions(Options *opts)
    {
        this->opts = opts;
    }
    bool hasAtom(std::string atomName);
    void addAtom(std::string atomName);
    std::string getAtomName(Atom atomID);
    void pushReactant(std::string atomName);
    void pushInhibitor(std::string atomName);
    void pushProduct(std::string atomName);
    void commitReaction(void);
    std::string atomToStr(const Atom atom) {
        return atoms_ids[atom];
    }
    std::string atomsToStr(const Atoms &atoms);
    void showReactions(void);
    void pushStateAtom(std::string atomName);
    void commitInitState(void);
    void addActionAtom(std::string atomName);
    bool isActionAtom(Atom atom);
    void resetInitStates(void) {
        initStates.clear();
    }
    unsigned int getAtomsSize(void) {
        return atoms_ids.size();
    }
    unsigned int getReactionsSize(void) {
        return reactions.size();
    }
    unsigned int getActionsSize(void) {
        return actionAtoms.size();
    }
    void showInitialStates(void);
    void showActionAtoms(void);
    void printSystem(void);
};

#endif

