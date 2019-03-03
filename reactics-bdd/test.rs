#
# Coffee machine RS
#

reactions {

    { { a; },{ z; } -> { b; } };
    #{ { c; },{ z; } -> { d; } };

}

action-atoms { z; }
initial-state { a; } 
ctl-property { EF ( coffee_ready ) }
#ctl-property { AG( coffee_ready IMPLIES ~water_ready ) }
#ctl-property { AG( failure IMPLIES AX ~busy ) }
#ctl-property { EG ( EF coffee_ready ) }


