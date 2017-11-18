reactions {
	{{out0,act0},{} -> {request0}};
	{{out0},{act0} -> {out0}};
	{{request0,act0,act1},{} -> {request0}};
	{{request0,act0,act2},{} -> {request0}};
	{{request0,act0,act3},{} -> {request0}};
	{{request0,act0,act4},{} -> {request0}};
	{{request0,act0,act5},{} -> {request0}};
	{{request0,act0,act6},{} -> {request0}};
	{{request0,act0,act7},{} -> {request0}};
	{{request0,act0,act8},{} -> {request0}};
	{{request0,act0,act9},{} -> {request0}};
	{{request0},{act0} -> {request0}};
	{{request0,act0},{act1,act2,act3,act4,act5,act6,act7,act8,act9,lock} -> {in0,lock}};
	{{in0,act0},{} -> {out0,done}};
	{{in0},{act0} -> {in0}};

	{{out1,act1},{} -> {request1}};
	{{out1},{act1} -> {out1}};
	{{request1,act1,act0},{} -> {request1}};
	{{request1,act1,act2},{} -> {request1}};
	{{request1,act1,act3},{} -> {request1}};
	{{request1,act1,act4},{} -> {request1}};
	{{request1,act1,act5},{} -> {request1}};
	{{request1,act1,act6},{} -> {request1}};
	{{request1,act1,act7},{} -> {request1}};
	{{request1,act1,act8},{} -> {request1}};
	{{request1,act1,act9},{} -> {request1}};
	{{request1},{act1} -> {request1}};
	{{request1,act1},{act0,act2,act3,act4,act5,act6,act7,act8,act9,lock} -> {in1,lock}};
	{{in1,act1},{} -> {out1,done}};
	{{in1},{act1} -> {in1}};

	{{out2,act2},{} -> {request2}};
	{{out2},{act2} -> {out2}};
	{{request2,act2,act0},{} -> {request2}};
	{{request2,act2,act1},{} -> {request2}};
	{{request2,act2,act3},{} -> {request2}};
	{{request2,act2,act4},{} -> {request2}};
	{{request2,act2,act5},{} -> {request2}};
	{{request2,act2,act6},{} -> {request2}};
	{{request2,act2,act7},{} -> {request2}};
	{{request2,act2,act8},{} -> {request2}};
	{{request2,act2,act9},{} -> {request2}};
	{{request2},{act2} -> {request2}};
	{{request2,act2},{act0,act1,act3,act4,act5,act6,act7,act8,act9,lock} -> {in2,lock}};
	{{in2,act2},{} -> {out2,done}};
	{{in2},{act2} -> {in2}};

	{{out3,act3},{} -> {request3}};
	{{out3},{act3} -> {out3}};
	{{request3,act3,act0},{} -> {request3}};
	{{request3,act3,act1},{} -> {request3}};
	{{request3,act3,act2},{} -> {request3}};
	{{request3,act3,act4},{} -> {request3}};
	{{request3,act3,act5},{} -> {request3}};
	{{request3,act3,act6},{} -> {request3}};
	{{request3,act3,act7},{} -> {request3}};
	{{request3,act3,act8},{} -> {request3}};
	{{request3,act3,act9},{} -> {request3}};
	{{request3},{act3} -> {request3}};
	{{request3,act3},{act0,act1,act2,act4,act5,act6,act7,act8,act9,lock} -> {in3,lock}};
	{{in3,act3},{} -> {out3,done}};
	{{in3},{act3} -> {in3}};

	{{out4,act4},{} -> {request4}};
	{{out4},{act4} -> {out4}};
	{{request4,act4,act0},{} -> {request4}};
	{{request4,act4,act1},{} -> {request4}};
	{{request4,act4,act2},{} -> {request4}};
	{{request4,act4,act3},{} -> {request4}};
	{{request4,act4,act5},{} -> {request4}};
	{{request4,act4,act6},{} -> {request4}};
	{{request4,act4,act7},{} -> {request4}};
	{{request4,act4,act8},{} -> {request4}};
	{{request4,act4,act9},{} -> {request4}};
	{{request4},{act4} -> {request4}};
	{{request4,act4},{act0,act1,act2,act3,act5,act6,act7,act8,act9,lock} -> {in4,lock}};
	{{in4,act4},{} -> {out4,done}};
	{{in4},{act4} -> {in4}};

	{{out5,act5},{} -> {request5}};
	{{out5},{act5} -> {out5}};
	{{request5,act5,act0},{} -> {request5}};
	{{request5,act5,act1},{} -> {request5}};
	{{request5,act5,act2},{} -> {request5}};
	{{request5,act5,act3},{} -> {request5}};
	{{request5,act5,act4},{} -> {request5}};
	{{request5,act5,act6},{} -> {request5}};
	{{request5,act5,act7},{} -> {request5}};
	{{request5,act5,act8},{} -> {request5}};
	{{request5,act5,act9},{} -> {request5}};
	{{request5},{act5} -> {request5}};
	{{request5,act5},{act0,act1,act2,act3,act4,act6,act7,act8,act9,lock} -> {in5,lock}};
	{{in5,act5},{} -> {out5,done}};
	{{in5},{act5} -> {in5}};

	{{out6,act6},{} -> {request6}};
	{{out6},{act6} -> {out6}};
	{{request6,act6,act0},{} -> {request6}};
	{{request6,act6,act1},{} -> {request6}};
	{{request6,act6,act2},{} -> {request6}};
	{{request6,act6,act3},{} -> {request6}};
	{{request6,act6,act4},{} -> {request6}};
	{{request6,act6,act5},{} -> {request6}};
	{{request6,act6,act7},{} -> {request6}};
	{{request6,act6,act8},{} -> {request6}};
	{{request6,act6,act9},{} -> {request6}};
	{{request6},{act6} -> {request6}};
	{{request6,act6},{act0,act1,act2,act3,act4,act5,act7,act8,act9,lock} -> {in6,lock}};
	{{in6,act6},{} -> {out6,done}};
	{{in6},{act6} -> {in6}};

	{{out7,act7},{} -> {request7}};
	{{out7},{act7} -> {out7}};
	{{request7,act7,act0},{} -> {request7}};
	{{request7,act7,act1},{} -> {request7}};
	{{request7,act7,act2},{} -> {request7}};
	{{request7,act7,act3},{} -> {request7}};
	{{request7,act7,act4},{} -> {request7}};
	{{request7,act7,act5},{} -> {request7}};
	{{request7,act7,act6},{} -> {request7}};
	{{request7,act7,act8},{} -> {request7}};
	{{request7,act7,act9},{} -> {request7}};
	{{request7},{act7} -> {request7}};
	{{request7,act7},{act0,act1,act2,act3,act4,act5,act6,act8,act9,lock} -> {in7,lock}};
	{{in7,act7},{} -> {out7,done}};
	{{in7},{act7} -> {in7}};

	{{out8,act8},{} -> {request8}};
	{{out8},{act8} -> {out8}};
	{{request8,act8,act0},{} -> {request8}};
	{{request8,act8,act1},{} -> {request8}};
	{{request8,act8,act2},{} -> {request8}};
	{{request8,act8,act3},{} -> {request8}};
	{{request8,act8,act4},{} -> {request8}};
	{{request8,act8,act5},{} -> {request8}};
	{{request8,act8,act6},{} -> {request8}};
	{{request8,act8,act7},{} -> {request8}};
	{{request8,act8,act9},{} -> {request8}};
	{{request8},{act8} -> {request8}};
	{{request8,act8},{act0,act1,act2,act3,act4,act5,act6,act7,act9,lock} -> {in8,lock}};
	{{in8,act8},{} -> {out8,done}};
	{{in8},{act8} -> {in8}};

	{{out9,act9},{} -> {request9}};
	{{out9},{act9} -> {out9}};
	{{request9,act9,act0},{} -> {request9}};
	{{request9,act9,act1},{} -> {request9}};
	{{request9,act9,act2},{} -> {request9}};
	{{request9,act9,act3},{} -> {request9}};
	{{request9,act9,act4},{} -> {request9}};
	{{request9,act9,act5},{} -> {request9}};
	{{request9,act9,act6},{} -> {request9}};
	{{request9,act9,act7},{} -> {request9}};
	{{request9,act9,act8},{} -> {request9}};
	{{request9},{act9} -> {request9}};
	{{request9,act9},{act0,act1,act2,act3,act4,act5,act6,act7,act8,lock} -> {in9,lock}};
	{{in9,act9},{} -> {out9,done}};
	{{in9},{act9} -> {in9}};

	{{lock},{done} -> {lock}};
}
context-entities {act0,act1,act2,act3,act4,act5,act6,act7,act8,act9}

initial-contexts { {out0,out1,out2,out3,out4,out5,out6,out7,out8,out9} }

rsctl-property { A[{act1}]F(in1) }
