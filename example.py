from z3 import *

p0 = Bool('p0')
p1 = Bool('p1')
p2 = Bool('p2') 
p3 = Bool('p3')
p4 = Bool('p4')

p0e = Bool('p0e')
p1e = Bool('p1e')
p2e = Bool('p2e')
p3e = Bool('p3e')
p4e = Bool('p4e')

p0p = Bool('p0p')
p1p = Bool('p1p')
p2p = Bool('p2p')
p3p = Bool('p3p')
p4p = Bool('p4p')

Cd_a1 = And( Or(p1,p1e), Or(p4,p4e), Not( Or(p2,p2e) ) )
Cd_a2 = And( Or(p2,p2e),             Not( Or(p3,p3e) ) )
Cd_a3 = And( Or(p1,p1e), Or(p3,p3e), Not( Or(p2,p2e) ) )
Cd_a4 = And( Or(p3,p3e),             Not( Or(p2,p2e) ) )

En1 = Or(Cd_a1,Cd_a2,Cd_a3,Cd_a4)
En2 = Or(Cd_a1,Cd_a3)
En3 = Cd_a2
En4 = Cd_a2

Pr1 = Or( And(En1,p1p) , And( Not(En1), Not(p1p)) )
Pr2 = Or( And(En2,p2p) , And( Not(En2), Not(p2p)) )
Pr3 = Or( And(En3,p3p) , And( Not(En3), Not(p3p)) )
Pr4 = Or( And(En4,p4p) , And( Not(En4), Not(p4p)) )

PrConjunction = And( Pr1, Pr2, Pr3, Pr4 )

print PrConjunction

