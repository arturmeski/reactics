#
# Coffee machine RS
#

reactions {
    { { e1; e4; }, { e2; } -> { e1; e2; } };
    { { e2; }, { e3; } -> { e1; e3; e4; } };
    { { e1; e3; }, { e2; } -> { e1; e2; } };
    { { e3; }, { e2; } -> { e1; } };
}

action-atoms { e4; }
initial-state { e1; e4; } 
ctl-property { EF ( coffee_ready ) }
#ctl-property { AG( coffee_ready IMPLIES ~water_ready ) }
#ctl-property { AG( failure IMPLIES AX ~busy ) }
#ctl-property { EG ( EF coffee_ready ) }


