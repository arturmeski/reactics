#
# Coffee machine RS
#

reactions {

    { { button_coffee; },{ failure; busy; button_water; } -> { coffee; make; busy; } };
    { { button_water; },{ failure; busy; button_coffee; } -> { water; make; busy; } };
    { { busy; },{ coffee_ready; water_ready; failure; release; } -> { busy; } };
    { { warm_up; }, { failure; } -> { warm; } };
    { { grind; },{ failure; } -> { ground; } };
    { { chk_water; },{ failure; } -> { water_ok; } };
    { { chk_water; failure; },{ } -> { more_water; } };
    { { make; },{ failure; } -> { warm_up; chk_water; } };
    { { make; },{ water; failure; } -> { grind; } };
    { { warm; ground; water_ok; },{ water; failure; } -> { brew_coffee; release; } };
    { { warm; water_ok; },{ ground; failure; } -> { fill_water; release; } };
    { { brew_coffee; },{ failure; } -> { coffee_ready; } };
    { { fill_water; },{ failure; } -> { water_ready; } };
    #{ { make; },{ coffe_ready; water_ready; } -> { make; } };
    #{ { coffee; },{ brew_coffee; } -> { coffee; } };
    #{ { water; },{ fill_water; failure; } -> { water; } };
    ###{ { button_water; brew_coffe; },{ failure; } -> { failure; } };
}

action-atoms { failure; button_coffee; button_water; }
initial-states { { button_coffee; fill_water; }; { failure; }; } 
ctl-property { EF ( coffee_ready ) }
#ctl-property { AG( coffee_ready IMPLIES ~water_ready ) }
#ctl-property { AG( failure IMPLIES AX ~busy ) }
#ctl-property { EG ( EF coffee_ready ) }


