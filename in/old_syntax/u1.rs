#
# Coffee machine RS
#

reactions {

    { { a1;a4; },{ a2; } -> { a1;a2; } };
    { { a2; },{ a3; } -> { a1;a3;a4; } };
    { { a1;a3; },{ a2; } -> {a1;a2;} };
    { {a3;},{a2;} -> {a1;} };
}

action-atoms { a4; }

initial-state { a1; a4; }

#ctl-property { EF ( coffee_ready ) }
#ctl-property { AG( coffee_ready IMPLIES ~water_ready ) }

#ctl-property { AG( failure IMPLIES AX ~busy ) }

#ctl-property { EG ( EF coffee_ready ) }


