reactions {
	# (1) no decrement, no increment
	{{p0},{dec,inc} -> {p0}};
	{{p1},{dec,inc} -> {p1}};
	{{p2},{dec,inc} -> {p2}};
	{{p3},{dec,inc} -> {p3}};
	{{p4},{dec,inc} -> {p4}};
	{{p5},{dec,inc} -> {p5}};
	{{p6},{dec,inc} -> {p6}};
	{{p7},{dec,inc} -> {p7}};
	{{p8},{dec,inc} -> {p8}};
	{{p9},{dec,inc} -> {p9}};
	{{p10},{dec,inc} -> {p10}};
	{{p11},{dec,inc} -> {p11}};
	{{p12},{dec,inc} -> {p12}};
	{{p13},{dec,inc} -> {p13}};
	{{p14},{dec,inc} -> {p14}};
	{{p15},{dec,inc} -> {p15}};

	# (2) increment operation
	{{inc},{dec,p0} -> {p0}};
	{{inc,p0},{dec,p1} -> {p1}};
	{{inc,p0,p1},{dec,p2} -> {p2}};
	{{inc,p0,p1,p2},{dec,p3} -> {p3}};
	{{inc,p0,p1,p2,p3},{dec,p4} -> {p4}};
	{{inc,p0,p1,p2,p3,p4},{dec,p5} -> {p5}};
	{{inc,p0,p1,p2,p3,p4,p5},{dec,p6} -> {p6}};
	{{inc,p0,p1,p2,p3,p4,p5,p6},{dec,p7} -> {p7}};
	{{inc,p0,p1,p2,p3,p4,p5,p6,p7},{dec,p8} -> {p8}};
	{{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8},{dec,p9} -> {p9}};
	{{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9},{dec,p10} -> {p10}};
	{{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10},{dec,p11} -> {p11}};
	{{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11},{dec,p12} -> {p12}};
	{{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12},{dec,p13} -> {p13}};
	{{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13},{dec,p14} -> {p14}};
	{{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14},{dec,p15} -> {p15}};

	# the more significant bits remain (inc)
	{{inc,p1},{dec,p0} -> {p1}};
	{{inc,p2},{dec,p0} -> {p2}};
	{{inc,p3},{dec,p0} -> {p3}};
	{{inc,p4},{dec,p0} -> {p4}};
	{{inc,p5},{dec,p0} -> {p5}};
	{{inc,p6},{dec,p0} -> {p6}};
	{{inc,p7},{dec,p0} -> {p7}};
	{{inc,p8},{dec,p0} -> {p8}};
	{{inc,p9},{dec,p0} -> {p9}};
	{{inc,p10},{dec,p0} -> {p10}};
	{{inc,p11},{dec,p0} -> {p11}};
	{{inc,p12},{dec,p0} -> {p12}};
	{{inc,p13},{dec,p0} -> {p13}};
	{{inc,p14},{dec,p0} -> {p14}};
	{{inc,p15},{dec,p0} -> {p15}};
	{{inc,p2},{dec,p1} -> {p2}};
	{{inc,p3},{dec,p1} -> {p3}};
	{{inc,p4},{dec,p1} -> {p4}};
	{{inc,p5},{dec,p1} -> {p5}};
	{{inc,p6},{dec,p1} -> {p6}};
	{{inc,p7},{dec,p1} -> {p7}};
	{{inc,p8},{dec,p1} -> {p8}};
	{{inc,p9},{dec,p1} -> {p9}};
	{{inc,p10},{dec,p1} -> {p10}};
	{{inc,p11},{dec,p1} -> {p11}};
	{{inc,p12},{dec,p1} -> {p12}};
	{{inc,p13},{dec,p1} -> {p13}};
	{{inc,p14},{dec,p1} -> {p14}};
	{{inc,p15},{dec,p1} -> {p15}};
	{{inc,p3},{dec,p2} -> {p3}};
	{{inc,p4},{dec,p2} -> {p4}};
	{{inc,p5},{dec,p2} -> {p5}};
	{{inc,p6},{dec,p2} -> {p6}};
	{{inc,p7},{dec,p2} -> {p7}};
	{{inc,p8},{dec,p2} -> {p8}};
	{{inc,p9},{dec,p2} -> {p9}};
	{{inc,p10},{dec,p2} -> {p10}};
	{{inc,p11},{dec,p2} -> {p11}};
	{{inc,p12},{dec,p2} -> {p12}};
	{{inc,p13},{dec,p2} -> {p13}};
	{{inc,p14},{dec,p2} -> {p14}};
	{{inc,p15},{dec,p2} -> {p15}};
	{{inc,p4},{dec,p3} -> {p4}};
	{{inc,p5},{dec,p3} -> {p5}};
	{{inc,p6},{dec,p3} -> {p6}};
	{{inc,p7},{dec,p3} -> {p7}};
	{{inc,p8},{dec,p3} -> {p8}};
	{{inc,p9},{dec,p3} -> {p9}};
	{{inc,p10},{dec,p3} -> {p10}};
	{{inc,p11},{dec,p3} -> {p11}};
	{{inc,p12},{dec,p3} -> {p12}};
	{{inc,p13},{dec,p3} -> {p13}};
	{{inc,p14},{dec,p3} -> {p14}};
	{{inc,p15},{dec,p3} -> {p15}};
	{{inc,p5},{dec,p4} -> {p5}};
	{{inc,p6},{dec,p4} -> {p6}};
	{{inc,p7},{dec,p4} -> {p7}};
	{{inc,p8},{dec,p4} -> {p8}};
	{{inc,p9},{dec,p4} -> {p9}};
	{{inc,p10},{dec,p4} -> {p10}};
	{{inc,p11},{dec,p4} -> {p11}};
	{{inc,p12},{dec,p4} -> {p12}};
	{{inc,p13},{dec,p4} -> {p13}};
	{{inc,p14},{dec,p4} -> {p14}};
	{{inc,p15},{dec,p4} -> {p15}};
	{{inc,p6},{dec,p5} -> {p6}};
	{{inc,p7},{dec,p5} -> {p7}};
	{{inc,p8},{dec,p5} -> {p8}};
	{{inc,p9},{dec,p5} -> {p9}};
	{{inc,p10},{dec,p5} -> {p10}};
	{{inc,p11},{dec,p5} -> {p11}};
	{{inc,p12},{dec,p5} -> {p12}};
	{{inc,p13},{dec,p5} -> {p13}};
	{{inc,p14},{dec,p5} -> {p14}};
	{{inc,p15},{dec,p5} -> {p15}};
	{{inc,p7},{dec,p6} -> {p7}};
	{{inc,p8},{dec,p6} -> {p8}};
	{{inc,p9},{dec,p6} -> {p9}};
	{{inc,p10},{dec,p6} -> {p10}};
	{{inc,p11},{dec,p6} -> {p11}};
	{{inc,p12},{dec,p6} -> {p12}};
	{{inc,p13},{dec,p6} -> {p13}};
	{{inc,p14},{dec,p6} -> {p14}};
	{{inc,p15},{dec,p6} -> {p15}};
	{{inc,p8},{dec,p7} -> {p8}};
	{{inc,p9},{dec,p7} -> {p9}};
	{{inc,p10},{dec,p7} -> {p10}};
	{{inc,p11},{dec,p7} -> {p11}};
	{{inc,p12},{dec,p7} -> {p12}};
	{{inc,p13},{dec,p7} -> {p13}};
	{{inc,p14},{dec,p7} -> {p14}};
	{{inc,p15},{dec,p7} -> {p15}};
	{{inc,p9},{dec,p8} -> {p9}};
	{{inc,p10},{dec,p8} -> {p10}};
	{{inc,p11},{dec,p8} -> {p11}};
	{{inc,p12},{dec,p8} -> {p12}};
	{{inc,p13},{dec,p8} -> {p13}};
	{{inc,p14},{dec,p8} -> {p14}};
	{{inc,p15},{dec,p8} -> {p15}};
	{{inc,p10},{dec,p9} -> {p10}};
	{{inc,p11},{dec,p9} -> {p11}};
	{{inc,p12},{dec,p9} -> {p12}};
	{{inc,p13},{dec,p9} -> {p13}};
	{{inc,p14},{dec,p9} -> {p14}};
	{{inc,p15},{dec,p9} -> {p15}};
	{{inc,p11},{dec,p10} -> {p11}};
	{{inc,p12},{dec,p10} -> {p12}};
	{{inc,p13},{dec,p10} -> {p13}};
	{{inc,p14},{dec,p10} -> {p14}};
	{{inc,p15},{dec,p10} -> {p15}};
	{{inc,p12},{dec,p11} -> {p12}};
	{{inc,p13},{dec,p11} -> {p13}};
	{{inc,p14},{dec,p11} -> {p14}};
	{{inc,p15},{dec,p11} -> {p15}};
	{{inc,p13},{dec,p12} -> {p13}};
	{{inc,p14},{dec,p12} -> {p14}};
	{{inc,p15},{dec,p12} -> {p15}};
	{{inc,p14},{dec,p13} -> {p14}};
	{{inc,p15},{dec,p13} -> {p15}};
	{{inc,p15},{dec,p14} -> {p15}};

	# (3) decrement operation
	{{dec},{inc,p0} -> {p0}};
	{{dec},{inc,p0,p1} -> {p1}};
	{{dec},{inc,p0,p1,p2} -> {p2}};
	{{dec},{inc,p0,p1,p2,p3} -> {p3}};
	{{dec},{inc,p0,p1,p2,p3,p4} -> {p4}};
	{{dec},{inc,p0,p1,p2,p3,p4,p5} -> {p5}};
	{{dec},{inc,p0,p1,p2,p3,p4,p5,p6} -> {p6}};
	{{dec},{inc,p0,p1,p2,p3,p4,p5,p6,p7} -> {p7}};
	{{dec},{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8} -> {p8}};
	{{dec},{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9} -> {p9}};
	{{dec},{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10} -> {p10}};
	{{dec},{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11} -> {p11}};
	{{dec},{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12} -> {p12}};
	{{dec},{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13} -> {p13}};
	{{dec},{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14} -> {p14}};
	{{dec},{inc,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15} -> {p15}};

	# the more significant bits remain (dec)
	{{dec,p0,p1},{inc} -> {p1}};
	{{dec,p0,p2},{inc} -> {p2}};
	{{dec,p0,p3},{inc} -> {p3}};
	{{dec,p0,p4},{inc} -> {p4}};
	{{dec,p0,p5},{inc} -> {p5}};
	{{dec,p0,p6},{inc} -> {p6}};
	{{dec,p0,p7},{inc} -> {p7}};
	{{dec,p0,p8},{inc} -> {p8}};
	{{dec,p0,p9},{inc} -> {p9}};
	{{dec,p0,p10},{inc} -> {p10}};
	{{dec,p0,p11},{inc} -> {p11}};
	{{dec,p0,p12},{inc} -> {p12}};
	{{dec,p0,p13},{inc} -> {p13}};
	{{dec,p0,p14},{inc} -> {p14}};
	{{dec,p0,p15},{inc} -> {p15}};
	{{dec,p1,p2},{inc} -> {p2}};
	{{dec,p1,p3},{inc} -> {p3}};
	{{dec,p1,p4},{inc} -> {p4}};
	{{dec,p1,p5},{inc} -> {p5}};
	{{dec,p1,p6},{inc} -> {p6}};
	{{dec,p1,p7},{inc} -> {p7}};
	{{dec,p1,p8},{inc} -> {p8}};
	{{dec,p1,p9},{inc} -> {p9}};
	{{dec,p1,p10},{inc} -> {p10}};
	{{dec,p1,p11},{inc} -> {p11}};
	{{dec,p1,p12},{inc} -> {p12}};
	{{dec,p1,p13},{inc} -> {p13}};
	{{dec,p1,p14},{inc} -> {p14}};
	{{dec,p1,p15},{inc} -> {p15}};
	{{dec,p2,p3},{inc} -> {p3}};
	{{dec,p2,p4},{inc} -> {p4}};
	{{dec,p2,p5},{inc} -> {p5}};
	{{dec,p2,p6},{inc} -> {p6}};
	{{dec,p2,p7},{inc} -> {p7}};
	{{dec,p2,p8},{inc} -> {p8}};
	{{dec,p2,p9},{inc} -> {p9}};
	{{dec,p2,p10},{inc} -> {p10}};
	{{dec,p2,p11},{inc} -> {p11}};
	{{dec,p2,p12},{inc} -> {p12}};
	{{dec,p2,p13},{inc} -> {p13}};
	{{dec,p2,p14},{inc} -> {p14}};
	{{dec,p2,p15},{inc} -> {p15}};
	{{dec,p3,p4},{inc} -> {p4}};
	{{dec,p3,p5},{inc} -> {p5}};
	{{dec,p3,p6},{inc} -> {p6}};
	{{dec,p3,p7},{inc} -> {p7}};
	{{dec,p3,p8},{inc} -> {p8}};
	{{dec,p3,p9},{inc} -> {p9}};
	{{dec,p3,p10},{inc} -> {p10}};
	{{dec,p3,p11},{inc} -> {p11}};
	{{dec,p3,p12},{inc} -> {p12}};
	{{dec,p3,p13},{inc} -> {p13}};
	{{dec,p3,p14},{inc} -> {p14}};
	{{dec,p3,p15},{inc} -> {p15}};
	{{dec,p4,p5},{inc} -> {p5}};
	{{dec,p4,p6},{inc} -> {p6}};
	{{dec,p4,p7},{inc} -> {p7}};
	{{dec,p4,p8},{inc} -> {p8}};
	{{dec,p4,p9},{inc} -> {p9}};
	{{dec,p4,p10},{inc} -> {p10}};
	{{dec,p4,p11},{inc} -> {p11}};
	{{dec,p4,p12},{inc} -> {p12}};
	{{dec,p4,p13},{inc} -> {p13}};
	{{dec,p4,p14},{inc} -> {p14}};
	{{dec,p4,p15},{inc} -> {p15}};
	{{dec,p5,p6},{inc} -> {p6}};
	{{dec,p5,p7},{inc} -> {p7}};
	{{dec,p5,p8},{inc} -> {p8}};
	{{dec,p5,p9},{inc} -> {p9}};
	{{dec,p5,p10},{inc} -> {p10}};
	{{dec,p5,p11},{inc} -> {p11}};
	{{dec,p5,p12},{inc} -> {p12}};
	{{dec,p5,p13},{inc} -> {p13}};
	{{dec,p5,p14},{inc} -> {p14}};
	{{dec,p5,p15},{inc} -> {p15}};
	{{dec,p6,p7},{inc} -> {p7}};
	{{dec,p6,p8},{inc} -> {p8}};
	{{dec,p6,p9},{inc} -> {p9}};
	{{dec,p6,p10},{inc} -> {p10}};
	{{dec,p6,p11},{inc} -> {p11}};
	{{dec,p6,p12},{inc} -> {p12}};
	{{dec,p6,p13},{inc} -> {p13}};
	{{dec,p6,p14},{inc} -> {p14}};
	{{dec,p6,p15},{inc} -> {p15}};
	{{dec,p7,p8},{inc} -> {p8}};
	{{dec,p7,p9},{inc} -> {p9}};
	{{dec,p7,p10},{inc} -> {p10}};
	{{dec,p7,p11},{inc} -> {p11}};
	{{dec,p7,p12},{inc} -> {p12}};
	{{dec,p7,p13},{inc} -> {p13}};
	{{dec,p7,p14},{inc} -> {p14}};
	{{dec,p7,p15},{inc} -> {p15}};
	{{dec,p8,p9},{inc} -> {p9}};
	{{dec,p8,p10},{inc} -> {p10}};
	{{dec,p8,p11},{inc} -> {p11}};
	{{dec,p8,p12},{inc} -> {p12}};
	{{dec,p8,p13},{inc} -> {p13}};
	{{dec,p8,p14},{inc} -> {p14}};
	{{dec,p8,p15},{inc} -> {p15}};
	{{dec,p9,p10},{inc} -> {p10}};
	{{dec,p9,p11},{inc} -> {p11}};
	{{dec,p9,p12},{inc} -> {p12}};
	{{dec,p9,p13},{inc} -> {p13}};
	{{dec,p9,p14},{inc} -> {p14}};
	{{dec,p9,p15},{inc} -> {p15}};
	{{dec,p10,p11},{inc} -> {p11}};
	{{dec,p10,p12},{inc} -> {p12}};
	{{dec,p10,p13},{inc} -> {p13}};
	{{dec,p10,p14},{inc} -> {p14}};
	{{dec,p10,p15},{inc} -> {p15}};
	{{dec,p11,p12},{inc} -> {p12}};
	{{dec,p11,p13},{inc} -> {p13}};
	{{dec,p11,p14},{inc} -> {p14}};
	{{dec,p11,p15},{inc} -> {p15}};
	{{dec,p12,p13},{inc} -> {p13}};
	{{dec,p12,p14},{inc} -> {p14}};
	{{dec,p12,p15},{inc} -> {p15}};
	{{dec,p13,p14},{inc} -> {p14}};
	{{dec,p13,p15},{inc} -> {p15}};
	{{dec,p14,p15},{inc} -> {p15}};
}

context-entities { inc,dec }
initial-contexts { {} }
rsctl-property { AG((p0 AND p1 AND p2 AND p3 AND p4 AND p5 AND p6 AND p7 AND p8 AND p9 AND p10 AND p11 AND p12 AND p13 AND p14 AND p15) IMPLIES A[{inc}]X(~p0 AND ~p1 AND ~p2 AND ~p3 AND ~p4 AND ~p5 AND ~p6 AND ~p7 AND ~p8 AND ~p9 AND ~p10 AND ~p11 AND ~p12 AND ~p13 AND ~p14 AND ~p15)) }
