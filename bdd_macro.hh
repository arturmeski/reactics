#ifndef __BDD_MACRO_HH__
#define __BDD_MACRO_HH__

#define BDD_IFF(p,q) (!(p+q)+(p*q))
#define BDD_TRUE (cuddMgr->bddOne())
#define BDD_FALSE (cuddMgr->bddZero())

#endif
