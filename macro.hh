#ifndef __MY_MACROS__
#define __MY_MACROS__

#define LINENUM std::cout << __FILE__ <<  " (function " << __func__ << "), line " << __LINE__ << std::endl;
/* Fatal error */
#define FERROR(s) \
{ \
	std::cerr << "EE: " << __FILE__ << " (function " << __func__ << "), line " << __LINE__ << ": " << s << std::endl; \
	exit(1); \
}
#define WARNING(s) \
{ \
    std::cerr << "== WARNING: " << s << std::endl;        \
}

#define VERB(s) \
if (opts->verbose > 0) { \
	std::cerr << "ii VERBOSE(1): " << __FILE__ << " (" << __func__ << ":" << __LINE__ << "): " << s << std::endl;		\
}

#define VERB_L2(s) \
if (opts->verbose > 1) { \
	std::cerr << "ii VERBOSE(2): " << __FILE__ << " (" << __func__ << ":" << __LINE__ << "): " << s << std::endl;		\
}

#define VERB_L3(s) \
if (opts->verbose > 2) { \
	std::cerr << "ii VERBOSE(3): " << __FILE__ << " (" << __func__ << ":" << __LINE__ << "): " << s << std::endl;		\
}

#endif
