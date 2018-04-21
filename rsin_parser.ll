%{ /* -*- C++ -*- */
#include <cstdlib>
#include <cerrno>
#include <climits>
#include <string>
#include "rsin_driver.hh"
#include "rsin_parser.hh"

/* Work around an incompatibility in flex (at least versions
   2.5.31 through 2.5.33): it generates code that does
   not conform to C89.  See Debian bug 333231
   <http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=333231>.  */
#undef yywrap
#define yywrap() 1

/* By default yylex returns int, we use token_type.
   Unfortunately yyterminate by default returns 0, which is
   not of token_type.  */
#define yyterminate() return token::END
%}

%option noyywrap nounput batch debug

id [a-zA-Z][a-zA-Z_0-9:-]*
int [0-9]+
blank [ \t]

%{
#define YY_USER_ACTION  yylloc->columns(yyleng);
%}
%%
%{
  yylloc->step();
%}
{blank}+   yylloc->step();
[\n]+      yylloc->lines(yyleng); yylloc->step();
%{
  typedef yy::rsin_parser::token token;
%}

"options"				        return token::OPTIONS;
"use-context-automaton"	return token::USE_CTX_AUT;
"use-concentrations"	  return token::USE_CONCENTRATIONS;
"reactions"             return token::REACTIONS;
"initial-contexts"      return token::INITIALCONTEXTS;
"context-entities"      return token::CONTEXTENTITIES;
"context-automaton"		  return token::CONTEXTAUTOMATON;
"transitions"			      return token::TRANSITIONS;
"states"				        return token::STATES;
"init-state"			      return token::INITSTATE;
"rsctlk-property"        return token::RSCTLKFORM;
"{"                     return token::LCB;
"}"                     return token::RCB;
"("                     return token::LRB;
")"                     return token::RRB;
"["                     return token::LSB;
"]"                     return token::RSB;
"="						          return token::EQ;
"<"						          return token::LAB;
">"						          return token::RAB;
":"						          return token::COL;
";"                     return token::SEMICOL;
"."                     return token::DOT;
","                     return token::COMMA;
"->"                    return token::RARR;
"AND"                   return token::AND;
"OR"                    return token::OR;
"XOR"					          return token::XOR;
"IMPLIES"               return token::IMPLIES;
"~"                     return token::NOT;
"A"                     return token::A;
"E"                     return token::E;
"EX"                    return token::EX;
"EU"                    return token::EU;
"EF"                    return token::EF;
"EG"                    return token::EG;
"AX"                    return token::AX;
"AU"                    return token::AU;
"AF"                    return token::AF;
"AG"                    return token::AG;
"X"                     return token::X;
"U"                     return token::U;
"F"                     return token::F;
"G"                     return token::G;
"K"                     return token::UK;
"C"                     return token::UC;
"D"                     return token::UD;
"UE"                    return token::UE;
"NK"                    return token::NK;
"NC"                    return token::NC;
"ND"                    return token::ND;
"NE"                    return token::NE;
"empty"                 return token::EMPTY;
"#".*                   ;

{int}    {
           errno = 0;
           long n = strtol(yytext, NULL, 10);
           if (! (INT_MIN <= n && n <= INT_MAX && errno != ERANGE))
             driver.error(*yylloc, "integer is out of range");
           yylval->ival = n;
           return token::NUMBER;
         }

{id}     {
           yylval->sval = new std::string(yytext);
           return token::IDENTIFIER;
         }

.        driver.error(*yylloc, "invalid character");
%%

void
rsin_driver::scan_begin()
{
  yy_flex_debug = trace_scanning;
  if (file.empty () || file == "-")
    yyin = stdin;
  else if (!(yyin = fopen (file.c_str (), "r")))
    {
      error("cannot open " + file + ": " + strerror(errno));
      exit(EXIT_FAILURE);
    }
}

void
rsin_driver::scan_end()
{
  fclose(yyin);
}

