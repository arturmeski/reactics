#include "rsin_driver.hh"
#include "rsin_parser.hh"

rsin_driver::rsin_driver(RctSys *rs)
: trace_scanning(false), trace_parsing(false)
{
    this->rsctlform = NULL;
    this->rs = rs;
}

rsin_driver::~rsin_driver ()
{
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
    if (rsctlform == NULL)
    {
        FERROR("RSCTL formula was not supplied!");
    }

    return rsctlform;
}

