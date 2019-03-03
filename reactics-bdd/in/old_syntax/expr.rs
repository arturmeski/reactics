#
# x', and y' are denoted by xp, and yp, respectively 
#


reactions {
    { { x; },{ Ix; } -> { x; } };
    { { x; },{ X; Z; } -> { xp; } };
    { { x; xp; },{ Iex; } -> { X; } };
    { { y; },{ Iy; } -> { y; } };
    { { y; }, { Q; } -> { yp; } };
    { { y; yp; },{ Iey; } -> { Y; } };
    { { z; },{ Iz; } -> { z; } };
    { { z; },{ X; } -> { zp; } };
    { { z; zp; },{ Iez; } -> { Z; } };
    { { U; X; },{ IQ; } -> { Q; } };
}

action-atoms { U; }

initial-state { x; y;  } 

#ctl-property { EG ( EF Q ) }
#ctl-property { AG ( Q IMPLIES AX ~yp ) }

#ctl-property { AG ( ( x AND xp AND U ) IMPLIES EF Q )  }

#ctl-property { EG ( ~Q ) }

ctl-property { AU ( ~yp , EX(EX(X)) ) }

