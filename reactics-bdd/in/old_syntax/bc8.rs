reactions {
	# (1) no decrement, no increment
	{ { p0; },{ dec; inc; } -> { p0; } };
	{ { p1; },{ dec; inc; } -> { p1; } };
	{ { p2; },{ dec; inc; } -> { p2; } };
	{ { p3; },{ dec; inc; } -> { p3; } };
	{ { p4; },{ dec; inc; } -> { p4; } };
	{ { p5; },{ dec; inc; } -> { p5; } };
	{ { p6; },{ dec; inc; } -> { p6; } };
	{ { p7; },{ dec; inc; } -> { p7; } };

	# (2) increment operation
	{ { inc; },{ dec; p0; } -> { p0; } };
	# the more significant bits remain (inc)
	{ { inc; p0; },{ dec; p0; } -> { p0; } };
	{ { inc; p1; },{ dec; p0; } -> { p1; } };
	{ { inc; p2; },{ dec; p0; } -> { p2; } };
	{ { inc; p3; },{ dec; p0; } -> { p3; } };
	{ { inc; p4; },{ dec; p0; } -> { p4; } };
	{ { inc; p5; },{ dec; p0; } -> { p5; } };
	{ { inc; p6; },{ dec; p0; } -> { p6; } };
	{ { inc; p7; },{ dec; p0; } -> { p7; } };
	{ { inc; p0; },{ dec; p1; } -> { p1; } };
	# the more significant bits remain (inc)
	{ { inc; p1; },{ dec; p1; } -> { p1; } };
	{ { inc; p2; },{ dec; p1; } -> { p2; } };
	{ { inc; p3; },{ dec; p1; } -> { p3; } };
	{ { inc; p4; },{ dec; p1; } -> { p4; } };
	{ { inc; p5; },{ dec; p1; } -> { p5; } };
	{ { inc; p6; },{ dec; p1; } -> { p6; } };
	{ { inc; p7; },{ dec; p1; } -> { p7; } };
	{ { inc; p0; p1; },{ dec; p2; } -> { p2; } };
	# the more significant bits remain (inc)
	{ { inc; p2; },{ dec; p2; } -> { p2; } };
	{ { inc; p3; },{ dec; p2; } -> { p3; } };
	{ { inc; p4; },{ dec; p2; } -> { p4; } };
	{ { inc; p5; },{ dec; p2; } -> { p5; } };
	{ { inc; p6; },{ dec; p2; } -> { p6; } };
	{ { inc; p7; },{ dec; p2; } -> { p7; } };
	{ { inc; p0; p1; p2; },{ dec; p3; } -> { p3; } };
	# the more significant bits remain (inc)
	{ { inc; p3; },{ dec; p3; } -> { p3; } };
	{ { inc; p4; },{ dec; p3; } -> { p4; } };
	{ { inc; p5; },{ dec; p3; } -> { p5; } };
	{ { inc; p6; },{ dec; p3; } -> { p6; } };
	{ { inc; p7; },{ dec; p3; } -> { p7; } };
	{ { inc; p0; p1; p2; p3; },{ dec; p4; } -> { p4; } };
	# the more significant bits remain (inc)
	{ { inc; p4; },{ dec; p4; } -> { p4; } };
	{ { inc; p5; },{ dec; p4; } -> { p5; } };
	{ { inc; p6; },{ dec; p4; } -> { p6; } };
	{ { inc; p7; },{ dec; p4; } -> { p7; } };
	{ { inc; p0; p1; p2; p3; p4; },{ dec; p5; } -> { p5; } };
	# the more significant bits remain (inc)
	{ { inc; p5; },{ dec; p5; } -> { p5; } };
	{ { inc; p6; },{ dec; p5; } -> { p6; } };
	{ { inc; p7; },{ dec; p5; } -> { p7; } };
	{ { inc; p0; p1; p2; p3; p4; p5; },{ dec; p6; } -> { p6; } };
	# the more significant bits remain (inc)
	{ { inc; p6; },{ dec; p6; } -> { p6; } };
	{ { inc; p7; },{ dec; p6; } -> { p7; } };
	{ { inc; p0; p1; p2; p3; p4; p5; p6; },{ dec; p7; } -> { p7; } };
	# the more significant bits remain (inc)
	{ { inc; p7; },{ dec; p7; } -> { p7; } };

	# (3) decrement operation
	{ { dec; },{ inc; } -> { p0; } };
	# the more significant bits remain (dec)
	{ { dec; p0; p0; },{ inc; } -> { p0; } };
	{ { dec; p0; p1; },{ inc; } -> { p1; } };
	{ { dec; p0; p2; },{ inc; } -> { p2; } };
	{ { dec; p0; p3; },{ inc; } -> { p3; } };
	{ { dec; p0; p4; },{ inc; } -> { p4; } };
	{ { dec; p0; p5; },{ inc; } -> { p5; } };
	{ { dec; p0; p6; },{ inc; } -> { p6; } };
	{ { dec; p0; p7; },{ inc; } -> { p7; } };
	{ { dec; },{ inc; p0; } -> { p1; } };
	# the more significant bits remain (dec)
	{ { dec; p1; p1; },{ inc; } -> { p1; } };
	{ { dec; p1; p2; },{ inc; } -> { p2; } };
	{ { dec; p1; p3; },{ inc; } -> { p3; } };
	{ { dec; p1; p4; },{ inc; } -> { p4; } };
	{ { dec; p1; p5; },{ inc; } -> { p5; } };
	{ { dec; p1; p6; },{ inc; } -> { p6; } };
	{ { dec; p1; p7; },{ inc; } -> { p7; } };
	{ { dec; },{ inc; p0; p1; } -> { p2; } };
	# the more significant bits remain (dec)
	{ { dec; p2; p2; },{ inc; } -> { p2; } };
	{ { dec; p2; p3; },{ inc; } -> { p3; } };
	{ { dec; p2; p4; },{ inc; } -> { p4; } };
	{ { dec; p2; p5; },{ inc; } -> { p5; } };
	{ { dec; p2; p6; },{ inc; } -> { p6; } };
	{ { dec; p2; p7; },{ inc; } -> { p7; } };
	{ { dec; },{ inc; p0; p1; p2; } -> { p3; } };
	# the more significant bits remain (dec)
	{ { dec; p3; p3; },{ inc; } -> { p3; } };
	{ { dec; p3; p4; },{ inc; } -> { p4; } };
	{ { dec; p3; p5; },{ inc; } -> { p5; } };
	{ { dec; p3; p6; },{ inc; } -> { p6; } };
	{ { dec; p3; p7; },{ inc; } -> { p7; } };
	{ { dec; },{ inc; p0; p1; p2; p3; } -> { p4; } };
	# the more significant bits remain (dec)
	{ { dec; p4; p4; },{ inc; } -> { p4; } };
	{ { dec; p4; p5; },{ inc; } -> { p5; } };
	{ { dec; p4; p6; },{ inc; } -> { p6; } };
	{ { dec; p4; p7; },{ inc; } -> { p7; } };
	{ { dec; },{ inc; p0; p1; p2; p3; p4; } -> { p5; } };
	# the more significant bits remain (dec)
	{ { dec; p5; p5; },{ inc; } -> { p5; } };
	{ { dec; p5; p6; },{ inc; } -> { p6; } };
	{ { dec; p5; p7; },{ inc; } -> { p7; } };
	{ { dec; },{ inc; p0; p1; p2; p3; p4; p5; } -> { p6; } };
	# the more significant bits remain (dec)
	{ { dec; p6; p6; },{ inc; } -> { p6; } };
	{ { dec; p6; p7; },{ inc; } -> { p7; } };
	{ { dec; },{ inc; p0; p1; p2; p3; p4; p5; p6; } -> { p7; } };
	# the more significant bits remain (dec)
	{ { dec; p7; p7; },{ inc; } -> { p7; } };
}
action-atoms { inc; dec; }
initial-state { }
ctl-property { EF( p7 AND ~p4 ) }

