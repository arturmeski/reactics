%skeleton "lalr1.cc" /* -*- C++ -*- */
%require "2.5"
%defines
%define parser_class_name {rsin_parser}

%code requires {
#include <string>
#include <set>
#include "formrsctlk.hh"
#include "rs.hh"
// #include "stateconstr.hh"

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
    FormRSCTLK *frsctlk;
    // Entity_f *ent;
    // Action_f *act;
    // ActionsVec_f *actionsVec;
    StateConstr *fstc;
    Agents_f *agents;
};

%code {
#include "rsin_driver.hh"
}

%token OPTIONS USE_CTX_AUT USE_CONCENTRATIONS MAKE_PROGRESSIVE
%token REACTIONS INITIALCONTEXTS CONTEXTENTITIES RSCTLKFORM
%token CONTEXTAUTOMATON STATES INITSTATE TRANSITIONS
%token EQ LCB RCB LRB RRB LSB RSB LAB RAB COL SEMICOL DOT COMMA RARR
%token AND OR XOR IMPLIES NOT
%token EX EU EF EG AX AU AF AG E A X U F G UK UC UD UE NK NC ND NE EMPTY

%token        END      0 "end of file"
%token <sval> IDENTIFIER "identifier"
%token <ival> NUMBER     "number"

%left AND OR XOR IMPLIES NOT
%left EX EU EF EG AX AU AF AG E A X U F G UK UC UD UE NK NC ND NE

//%right SRB

%type <frsctlk> rsctlk_form
// %type <ent> f_entity
// %type <act> action
// %type <actionsVec> actions
%type <fstc> state_constr
%type <agents> agents;

//%printer    { yyoutput << *$$; } "identifier"
%destructor { delete $$; } "identifier"
//%printer    { yyoutput << $$; } <ival>


%%

%start system;

system:
	| OPTIONS LCB options RCB system
  | REACTIONS LCB reactionsets RCB system
  | INITIALCONTEXTS LCB initstates RCB system
  | CONTEXTENTITIES LCB actionentities RCB system
	| CONTEXTAUTOMATON LCB ctxaut RCB system
  {
    driver.getReactionSystem()->ctxAutFinalise();
  }
  | RSCTLKFORM LCB IDENTIFIER COL rsctlk_form RCB system {
    driver.addFormRSCTLK(*$3, $5);
    free($3);
  }
  ;

options:
	| options option SEMICOL
	;

option:
	| USE_CTX_AUT {
		driver.useContextAutomaton();
	}
	| USE_CONCENTRATIONS {
		driver.useConcentrations();
	}
  | MAKE_PROGRESSIVE {
    driver.makeProgressive();
  }
	;

/*
 * -------------------------
 *         REACTIONS
 * -------------------------
 */

reactionsets:
	| reactionsets process_reactions
	;

process_reactions: processname LCB reactions RCB SEMICOL

processname: IDENTIFIER {
		driver.getReactionSystem()->setCurrentProcess(*$1);
		free($1);
	}

reactions:
    | reactions reaction SEMICOL
    ;

reaction:
    | LCB reactionConditions RARR LCB reactionProducts RCB RCB {
        driver.getReactionSystem()->commitReaction();
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
        driver.getReactionSystem()->pushReactant(*$1);
        free($1);
    }
    ;

inhibitors:
    inhibitor
    | inhibitors COMMA inhibitor
    ;

inhibitor:
    | IDENTIFIER {
        driver.getReactionSystem()->pushInhibitor(*$1);
        free($1);
    }
    ;

reactionProducts:
    reactionProduct
    | reactionProducts COMMA reactionProduct
    ;

reactionProduct: IDENTIFIER {
        driver.getReactionSystem()->pushProduct(*$1);
        free($1);
    }
    ;

/*******************************************/

initstates:
    LCB initstate RCB {
        driver.getReactionSystem()->commitInitState();
    }
    | initstates COMMA LCB initstate RCB {
        driver.getReactionSystem()->commitInitState();
    }
    ;

initstate:
    | entity
    | initstate COMMA entity
    ;

entity: IDENTIFIER {
        driver.getReactionSystem()->pushStateEntity(*$1);
        free($1);
    }
    ;

/*******************************************/

actionentities:
    | actentity
    | actionentities COMMA actentity
    ;

actentity: IDENTIFIER {
        driver.getReactionSystem()->addActionEntity(*$1);
        free($1);
    }
    ;

/*******************************************/

ctxaut:
	| STATES LCB autstates RCB ctxaut
	| INITSTATE LCB autinitstate RCB ctxaut
	| TRANSITIONS LCB auttransitions RCB ctxaut
	;

autstate: IDENTIFIER {
		driver.getReactionSystem()->ctxAutAddState(*$1);
		free($1);
	}
	;

autstates:
	autstate
	| autstate COMMA autstates
	;

autinitstate: IDENTIFIER {
		driver.getReactionSystem()->ctxAutSetInitState(*$1);
		free($1);
	}
	;

auttransitions:
	| auttrans
	| auttrans SEMICOL auttransitions
	;

auttrans: LCB proc_ctxsets RCB COL IDENTIFIER RARR IDENTIFIER {
		driver.getReactionSystem()->ctxAutAddTransition(*$5, *$7);
		free($5);
		free($7);
	}
    | LCB proc_ctxsets RCB COL IDENTIFIER RARR IDENTIFIER COL state_constr {
        driver.getReactionSystem()->ctxAutAddTransition(*$5, *$7, $9);
        free($5);
        free($7);
    }
	;

proc_ctxsets:
  | proc_ctxsets single_proc_ctxset
  ;

single_proc_ctxset: IDENTIFIER EQ LCB contextset RCB {
  driver.getReactionSystem()->ctxAutSaveCurrentContextSet(*$1);
		free($1);
	}
	;

contextset:
	| ctxentity
	| contextset COMMA ctxentity
	;

ctxentity: IDENTIFIER {
		driver.getReactionSystem()->ctxAutPushNamedContextEntity(*$1);
		free($1);
	}
	;

/* formulae */

state_constr: IDENTIFIER DOT IDENTIFIER {
        $$ = new StateConstr(*$1, *$3);
        free($1);
        free($3);
    }
    | NOT state_constr {
        $$ = new StateConstr(STC_NOT, $2);
    }
    | LRB state_constr RRB {
        $$ = $2;
    }
    | state_constr AND state_constr {
        $$ = new StateConstr(STC_AND, $1, $3);
    }
    | state_constr OR state_constr {
        $$ = new StateConstr(STC_OR, $1, $3);
    }
    | state_constr XOR state_constr {
        $$ = new StateConstr(STC_XOR, $1, $3);
    }
	;

// actions:
//     LCB action RCB {
//         $$ = new ActionsVec_f;
//         $$->push_back(*$2);
//         free($2);
//     }
//     | actions COMMA LCB action RCB {
//         $$ = $1;
//         $$->push_back(*$4);
//         free($4);
//     }
//     ;

// action:
//     {
//         $$ = new Action_f;
//     }
//     | f_entity {
//         $$ = new Action_f;
//         $$->insert(*$1);
//         free($1);
//     }
//     | action COMMA f_entity {
//         $$ = $1;
//         $$->insert(*$3);
//         free($3);
//     }
//     ;

// f_entity: IDENTIFIER {
//         $$ = new Entity_f(*$1);
//         free($1);
//     }
//     ;

agents:
    IDENTIFIER {
      Agents_f *ag = new Agents_f;
      ag->insert(*$1);
      free($1);
      $$ = ag;
    }
    | agents COMMA IDENTIFIER {
      $1->insert(*$3);
      free($3);
      $$ = $1;
    }

rsctlk_form:
    IDENTIFIER DOT IDENTIFIER {
        $$ = new FormRSCTLK(*$1, *$3);
        free($1);
        free($3);
    }
    | NOT rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_NOT, $2);
    }
    | LRB rsctlk_form RRB {
        $$ = $2;
    }
    | rsctlk_form AND rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_AND, $1, $3);
    }
    | rsctlk_form OR rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_OR, $1, $3);
    }
    | rsctlk_form XOR rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_XOR, $1, $3);
    }
    | rsctlk_form IMPLIES rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_IMPL, $1, $3);
    }
    | EX rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_EX, $2);
    }
    | EU LRB rsctlk_form COMMA rsctlk_form RRB {
        $$ = new FormRSCTLK(RSCTLK_EU, $3, $5);
    }
    | EF rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_EF, $2);
    }
    | EG rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_EG, $2);
    }
    | AX rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_AX, $2);
    }
    | AU LRB rsctlk_form COMMA rsctlk_form RRB {
        $$ = new FormRSCTLK(RSCTLK_AU, $3, $5);
    }
    | AF rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_AF, $2);
    }
    | AG rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_AG, $2);
    }
    | UK LSB agents RSB LRB rsctlk_form RRB {
        $$ = new FormRSCTLK(RSCTLK_UK, *$3, $6);
        free($3);
    }
    | NK LSB agents RSB LRB rsctlk_form RRB {
        $$ = new FormRSCTLK(RSCTLK_NK, *$3, $6);
        free($3);
    }
    | UE LSB agents RSB LRB rsctlk_form RRB {
        $$ = new FormRSCTLK(RSCTLK_UE, *$3, $6);
        free($3);
    }
    | NE LSB agents RSB LRB rsctlk_form RRB {
        $$ = new FormRSCTLK(RSCTLK_NE, *$3, $6);
        free($3);
    }

    // | E LSB actions RSB X rsctlk_form {
    //     $$ = new FormRSCTLK(RSCTLK_EX_ACT, $3, $6);
    // }
    // | E LSB actions RSB U LRB rsctlk_form COMMA rsctlk_form RRB {
    //     $$ = new FormRSCTLK(RSCTLK_EU_ACT, $3, $7, $9);
    // }
    // | E LSB actions RSB F rsctlk_form {
    //     $$ = new FormRSCTLK(RSCTLK_EF_ACT, $3, $6);
    // }
    // | E LSB actions RSB G rsctlk_form {
    //     $$ = new FormRSCTLK(RSCTLK_EG_ACT, $3, $6);
    // }
    // | A LSB actions RSB X rsctlk_form {
    //     $$ = new FormRSCTLK(RSCTLK_AX_ACT, $3, $6);
    // }
    // | A LSB actions RSB U LRB rsctlk_form COMMA rsctlk_form RRB {
    //     $$ = new FormRSCTLK(RSCTLK_AU_ACT, $3, $7, $9);
    // }
    // | A LSB actions RSB F rsctlk_form {
    //     $$ = new FormRSCTLK(RSCTLK_AF_ACT, $3, $6);
    // }
    // | A LSB actions RSB G rsctlk_form {
    //     $$ = new FormRSCTLK(RSCTLK_AG_ACT, $3, $6);
    // }

	  /* contexts as boolean formulae  */
    | E LAB state_constr RAB X rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_EX_ACT, $3, $6);
    }
    | E LAB state_constr RAB U LRB rsctlk_form COMMA rsctlk_form RRB {
        $$ = new FormRSCTLK(RSCTLK_EU_ACT, $3, $7, $9);
    }
    | E LAB state_constr RAB F rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_EF_ACT, $3, $6);
    }
    | E LAB state_constr RAB G rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_EG_ACT, $3, $6);
    }
    | A LAB state_constr RAB X rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_AX_ACT, $3, $6);
    }
    | A LAB state_constr RAB U LRB rsctlk_form COMMA rsctlk_form RRB {
        $$ = new FormRSCTLK(RSCTLK_AU_ACT, $3, $7, $9);
    }
    | A LAB state_constr RAB F rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_AF_ACT, $3, $6);
    }
    | A LAB state_constr RAB G rsctlk_form {
        $$ = new FormRSCTLK(RSCTLK_AG_ACT, $3, $6);
    }
    ;
%%

void
yy::rsin_parser::error(const yy::rsin_parser::location_type &l, const std::string &m)
{
    driver.error(l, m);
}
