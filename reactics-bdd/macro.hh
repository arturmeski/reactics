#ifndef __MY_MACROS__
#define __MY_MACROS__

#include <cassert>
#include <iostream>


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
assert(opts != nullptr); \
if (opts->verbose > 0) { \
  std::cerr << "ii VERBOSE(1): " << __FILE__ << " (" << __func__ << ":" << __LINE__ << "): " << s << std::endl;   \
}

#define VERB_L2(s) \
assert(opts != nullptr); \
if (opts->verbose > 1) { \
  std::cerr << "ii VERBOSE(2): " << __FILE__ << " (" << __func__ << ":" << __LINE__ << "): " << s << std::endl;   \
}

#define VERB_L3(s) \
assert(opts != nullptr); \
if (opts->verbose > 2) { \
  std::cerr << "ii VERBOSE(3): " << __FILE__ << " (" << __func__ << ":" << __LINE__ << "): " << s << std::endl;   \
}

#define VERB_LN(n,s) \
assert(opts != nullptr); \
if (opts->verbose >= (n)) { \
  std::cerr << "ii VERBOSE(" << (n) << "): " << __FILE__ << " (" << __func__ << ":" << __LINE__ << "): " << s << std::endl;   \
}


#define SET_ADD(set1, set2) (set1).insert((set2).begin(), (set2).end())

#endif
