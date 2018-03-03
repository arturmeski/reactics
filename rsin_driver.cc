#include "rsin_driver.hh"
#include "rsin_parser.hh"

rsin_driver::rsin_driver(void)
: trace_scanning(false), trace_parsing(false)
{
	initialise();
}

rsin_driver::rsin_driver(RctSys *rs)
: trace_scanning(false), trace_parsing(false)
{
	initialise();
	this->rs = rs;
}

void rsin_driver::initialise(void)
{
    rs = nullptr;
    rsctlform = nullptr;
	opts = nullptr;
	use_ctx_aut = false;
	use_concentrations = false;
}

rsin_driver::~rsin_driver ()
{
	// placeholder
}

int rsin_driver::parse(const std::string &f)
{
    file = f;
    scan_begin();
    yy::rsin_parser parser(*this);
    parser.set_debug_level(trace_parsing);
    int res = parser.parse();
    scan_end();
    return res;
}

void rsin_driver::error(const yy::location &l, const std::string &m)
{
    std::cerr << l << ": " << m << std::endl;
}

void rsin_driver::error(const std::string &m)
{
    std::cerr << m << std::endl;
}

FormRSCTL *rsin_driver::getFormRSCTL(void)
{
    if (rsctlform == nullptr)
    {
        FERROR("RSCTL formula was not supplied!");
    }

    return rsctlform;
}

//
// Checks if we are not too late to be setting any options
//
void rsin_driver::ensureOptionsAllowed(void)
{
	if (rs != nullptr)
	{
		FERROR("Options cannot be set/modified after the reaction system is initialised")
	}
}

void rsin_driver::ensureReactionSystemReady(void)
{
	if (rs == nullptr)
		setupReactionSystem();
}

void rsin_driver::setupReactionSystem(void)
{
	assert(rs == nullptr);
	rs = new RctSys;
	
	if (use_ctx_aut) VERB("Using RS with CA")
	else VERB("Using ordinary RS")

	rs->setOptions(opts);
}

RctSys *rsin_driver::getReactionSystem(void)
{
	ensureReactionSystemReady();
	assert(rs != nullptr);
	return rs;
}

