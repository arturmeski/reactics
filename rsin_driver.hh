#ifndef RSIN_DRIVER_HH
#define RSIN_DRIVER_HH
#include <string>
#include <map>
#include "rsin_parser.hh"
#include "rs.hh"
#include "formrsctl.hh"
#include "options.hh"

// Tell Flex the lexer's prototype ...
#define YY_DECL                                  \
  yy::rsin_parser::token_type                    \
  yylex(yy::rsin_parser::semantic_type* yylval,  \
         yy::rsin_parser::location_type* yylloc, \
         rsin_driver& driver)
// ... and declare it for the parser's sake.
YY_DECL;

// Conducting the whole scanning an parsing of RS
class rsin_driver
{
public:
    rsin_driver(void);
    rsin_driver(RctSys *rs);
    virtual ~rsin_driver();

    //std::map<std::string, int> variables;
    FormRSCTL *rsctlform;
    Options *opts;
	
	// options in configuration file:
	bool use_ctx_aut;
	bool use_concentrations;

    // Handling the scanner
    void scan_begin();
    void scan_end();
    bool trace_scanning;

    int parse(const std::string &f);
    std::string file;
    bool trace_parsing;

	void setOptions(Options *opts) 		{ this->opts = opts; };
    void addFormRSCTL(FormRSCTL *f) 	{ rsctlform = f; };
    FormRSCTL *getFormRSCTL(void);

	void ensureOptionsAllowed(void);
	void useContextAutomaton(void);
	void useConcentrations(void)		{ ensureOptionsAllowed(); use_concentrations = true; };
	
	void ensureReactionSystemReady(void);
	void setupReactionSystem(void);
	
	RctSys *getReactionSystem(void);
	CtxAut *getCtxAut(void);

    // Error handling.
    void error(const yy::location &l, const std::string &m);
    void error(const std::string &m);
	
private:
    RctSys *rs;

	void initialise(void);
};

#endif

