%skeleton "lalr1.cc" /* -*- C++ -*- */
%require "2.5"
%defines
%define parser_class_name "rsin_parser"

%code requires {
#include <string>
#include <set>
#include "formrsctl.hh"

using std::set;
using std::string;

class rsin_driver;
}

// The parsing context
%parse-param { rsin_driver &driver }
%lex-param { rsin_driver &driver }

%locations
%initial-action
{
    // Initialise the initial location
    @$.begin.filename = @$.end.filename = &driver.file;
};

%debug
%error-verbose

// Symbols
%union
{
    int ival;
    std::string *sval;
    FormRSCTL *frsctl;
    Entity_f *ent;
    Action_f *act;
    ActionsVec_f *actionsVec;
	BoolContexts *fboolctx;
};

%code {
#include "rsin_driver.hh"
}

%token REACTIONS INITIALCONTEXTS CONTEXTENTITIES RSCTLFORM
%token LCB RCB LRB RRB LSB RSB LAB RAB SEMICOL COMMA RARR
%token AND OR XOR IMPLIES NOT
%token EX EU EF EG AX AU AF AG E A X U F G EMPTY

%token        END      0 "end of file"
%token <sval> IDENTIFIER "identifier"
%token <ival> NUMBER     "number"

%left AND OR XOR IMPLIES NOT
%left EX EU EF EG AX AU AF AG E A X U F G

//%right SRB

%type <frsctl> rsctl_form
%type <ent> entity
%type <act> action
%type <actionsVec> actions
%type <fboolctx> bool_contexts

//%printer    { yyoutput << *$$; } "identifier"
%destructor { delete $$; } "identifier"
//%printer    { yyoutput << $$; } <ival>


%%

%start system;

system: 
    | REACTIONS LCB reactions RCB system
    | INITIALCONTEXTS LCB initstates RCB system
    | CONTEXTENTITIES LCB actionatoms RCB system
    | RSCTLFORM LCB rsctl_form RCB system {
        driver.addFormRSCTL($3);
    }
    ;

reactions:
    | reactions reaction SEMICOL
    ;

reaction:
    | LCB reactionConditions RARR LCB reactionProducts RCB RCB {
        driver.rs->commitReaction();
    }
    ;

reactionConditions:
    | LCB reactants RCB COMMA LCB inhibitors RCB
    ;

reactants:
    reactant
    | reactants COMMA reactant
    ;

reactant: IDENTIFIER {
        driver.rs->pushReactant(*$1);
        free($1);
    }
    ;

inhibitors:
    inhibitor
    | inhibitors COMMA inhibitor 
    ;

inhibitor:
    | IDENTIFIER {
        driver.rs->pushInhibitor(*$1);
        free($1);
    }
    ;

reactionProducts:
    reactionProduct
    | reactionProducts COMMA reactionProduct
    ;

reactionProduct: IDENTIFIER {
        driver.rs->pushProduct(*$1);
        free($1);
    }
    ;

initstates:
    LCB initstate RCB {
        driver.rs->commitInitState();
    }
    | initstates COMMA LCB initstate RCB {
        driver.rs->commitInitState();
    }
    ;

initstate:
    | atom
    | initstate COMMA atom 
    ;

atom: IDENTIFIER {
        driver.rs->pushStateAtom(*$1);
        free($1);
    }
    ;

actionatoms: 
    | actatom
    | actionatoms COMMA actatom
    ;

actatom: IDENTIFIER {
        driver.rs->addActionAtom(*$1);
        free($1);
    }
    ;

/* formulae */
	
bool_contexts: IDENTIFIER {
        $$ = new BoolContexts(*$1);
        free($1);
    }
    | NOT bool_contexts {
        $$ = new BoolContexts(BCTX_NOT, $2);
    }
    | LRB bool_contexts RRB {
        $$ = $2;
    }
    | bool_contexts AND bool_contexts {
        $$ = new BoolContexts(BCTX_AND, $1, $3);
    }
    | bool_contexts OR bool_contexts {
        $$ = new BoolContexts(BCTX_OR, $1, $3);
    }
    | bool_contexts XOR bool_contexts {
        $$ = new BoolContexts(BCTX_XOR, $1, $3);
    }
	;

actions:
    LCB action RCB {
        $$ = new ActionsVec_f;
        $$->push_back(*$2);
        free($2);
    }
    | actions COMMA LCB action RCB {
        $$ = $1;
        $$->push_back(*$4);
        free($4);
    }
    ;

action:
    { 
        $$ = new Action_f;
    } 
    | entity {
        $$ = new Action_f;
        $$->insert(*$1);
        free($1);
    }
    | action COMMA entity {
        $$ = $1;        
        $$->insert(*$3);
        free($3);
    }
    ;

entity: IDENTIFIER {
        $$ = new Entity_f(*$1);
        free($1);
    }
    ;

rsctl_form: IDENTIFIER {
        $$ = new FormRSCTL(*$1);
        free($1);
    }
    | NOT rsctl_form {
        $$ = new FormRSCTL(RSCTL_NOT, $2);
    }
    | LRB rsctl_form RRB {
        $$ = $2;
    }
    | rsctl_form AND rsctl_form {
        $$ = new FormRSCTL(RSCTL_AND, $1, $3);
    }
    | rsctl_form OR rsctl_form {
        $$ = new FormRSCTL(RSCTL_OR, $1, $3);
    }
    | rsctl_form XOR rsctl_form {
        $$ = new FormRSCTL(RSCTL_XOR, $1, $3);
    }
    | rsctl_form IMPLIES rsctl_form {
        $$ = new FormRSCTL(RSCTL_IMPL, $1, $3);
    }
    | EX rsctl_form {
        $$ = new FormRSCTL(RSCTL_EX, $2);
    }
    | EU LRB rsctl_form COMMA rsctl_form RRB {
        $$ = new FormRSCTL(RSCTL_EU, $3, $5);
    }
    | EF rsctl_form {
        $$ = new FormRSCTL(RSCTL_EF, $2);
    }
    | EG rsctl_form {
        $$ = new FormRSCTL(RSCTL_EG, $2);
    }
    | AX rsctl_form {
        $$ = new FormRSCTL(RSCTL_AX, $2);
    }
    | AU LRB rsctl_form COMMA rsctl_form RRB {
        $$ = new FormRSCTL(RSCTL_AU, $3, $5);
    }
    | AF rsctl_form {
        $$ = new FormRSCTL(RSCTL_AF, $2);
    }
    | AG rsctl_form {
        $$ = new FormRSCTL(RSCTL_AG, $2);
    }
    | E LSB actions RSB X rsctl_form {
        $$ = new FormRSCTL(RSCTL_EX_ACT, $3, $6);
    }
    | E LSB actions RSB U LRB rsctl_form COMMA rsctl_form RRB {
        $$ = new FormRSCTL(RSCTL_EU_ACT, $3, $7, $9);
    }
    | E LSB actions RSB F rsctl_form {
        $$ = new FormRSCTL(RSCTL_EF_ACT, $3, $6);
    }
    | E LSB actions RSB G rsctl_form {
        $$ = new FormRSCTL(RSCTL_EG_ACT, $3, $6);
    }
    | A LSB actions RSB X rsctl_form {
        $$ = new FormRSCTL(RSCTL_AX_ACT, $3, $6);
    }
    | A LSB actions RSB U LRB rsctl_form COMMA rsctl_form RRB {
        $$ = new FormRSCTL(RSCTL_AU_ACT, $3, $7, $9);
    }
    | A LSB actions RSB F rsctl_form {
        $$ = new FormRSCTL(RSCTL_AF_ACT, $3, $6);
    }
    | A LSB actions RSB G rsctl_form {
        $$ = new FormRSCTL(RSCTL_AG_ACT, $3, $6);
    }
	/* contexts as boolean formulae  */
    | E LAB bool_contexts RAB X rsctl_form { 
        $$ = new FormRSCTL(RSCTL_EX_ACT, $3, $6);
    }
    | E LAB bool_contexts RAB U LRB rsctl_form COMMA rsctl_form RRB {
        $$ = new FormRSCTL(RSCTL_EU_ACT, $3, $7, $9);
    }
    | E LAB bool_contexts RAB F rsctl_form {
        $$ = new FormRSCTL(RSCTL_EF_ACT, $3, $6);
    }
    | E LAB bool_contexts RAB G rsctl_form {
        $$ = new FormRSCTL(RSCTL_EG_ACT, $3, $6);
    }
    | A LAB bool_contexts RAB X rsctl_form {
        $$ = new FormRSCTL(RSCTL_AX_ACT, $3, $6);
    }
    | A LAB bool_contexts RAB U LRB rsctl_form COMMA rsctl_form RRB {
        $$ = new FormRSCTL(RSCTL_AU_ACT, $3, $7, $9);
    }
    | A LAB bool_contexts RAB F rsctl_form {
        $$ = new FormRSCTL(RSCTL_AF_ACT, $3, $6);
    }
    | A LAB bool_contexts RAB G rsctl_form {
        $$ = new FormRSCTL(RSCTL_AG_ACT, $3, $6);
    }
    ;
%%

void
yy::rsin_parser::error(const yy::rsin_parser::location_type &l, const std::string &m)
{
    driver.error(l, m);
}

