reactions {
	{{out0,act0},{} -> {request0}};
	{{out0},{act0} -> {out0}};
	{{request0,act0,act1},{} -> {request0}};
	{{request0,act0,act2},{} -> {request0}};
	{{request0,act0,act3},{} -> {request0}};
	{{request0,act0,act4},{} -> {request0}};
	{{request0,act0,act5},{} -> {request0}};
	{{request0},{act0} -> {request0}};
	{{request0,act0},{act1,act2,act3,act4,act5,lock} -> {in0,lock}};
	{{in0,act0},{} -> {out0,done}};
	{{in0},{act0} -> {in0}};

	{{out1,act1},{} -> {request1}};
	{{out1},{act1} -> {out1}};
	{{request1,act1,act0},{} -> {request1}};
	{{request1,act1,act2},{} -> {request1}};
	{{request1,act1,act3},{} -> {request1}};
	{{request1,act1,act4},{} -> {request1}};
	{{request1,act1,act5},{} -> {request1}};
	{{request1},{act1} -> {request1}};
	{{request1,act1},{act0,act2,act3,act4,act5,lock} -> {in1,lock}};
	{{in1,act1},{} -> {out1,done}};
	{{in1},{act1} -> {in1}};

	{{out2,act2},{} -> {request2}};
	{{out2},{act2} -> {out2}};
	{{request2,act2,act0},{} -> {request2}};
	{{request2,act2,act1},{} -> {request2}};
	{{request2,act2,act3},{} -> {request2}};
	{{request2,act2,act4},{} -> {request2}};
	{{request2,act2,act5},{} -> {request2}};
	{{request2},{act2} -> {request2}};
	{{request2,act2},{act0,act1,act3,act4,act5,lock} -> {in2,lock}};
	{{in2,act2},{} -> {out2,done}};
	{{in2},{act2} -> {in2}};

	{{out3,act3},{} -> {request3}};
	{{out3},{act3} -> {out3}};
	{{request3,act3,act0},{} -> {request3}};
	{{request3,act3,act1},{} -> {request3}};
	{{request3,act3,act2},{} -> {request3}};
	{{request3,act3,act4},{} -> {request3}};
	{{request3,act3,act5},{} -> {request3}};
	{{request3},{act3} -> {request3}};
	{{request3,act3},{act0,act1,act2,act4,act5,lock} -> {in3,lock}};
	{{in3,act3},{} -> {out3,done}};
	{{in3},{act3} -> {in3}};

	{{out4,act4},{} -> {request4}};
	{{out4},{act4} -> {out4}};
	{{request4,act4,act0},{} -> {request4}};
	{{request4,act4,act1},{} -> {request4}};
	{{request4,act4,act2},{} -> {request4}};
	{{request4,act4,act3},{} -> {request4}};
	{{request4,act4,act5},{} -> {request4}};
	{{request4},{act4} -> {request4}};
	{{request4,act4},{act0,act1,act2,act3,act5,lock} -> {in4,lock}};
	{{in4,act4},{} -> {out4,done}};
	{{in4},{act4} -> {in4}};

	{{out5,act5},{} -> {request5}};
	{{out5},{act5} -> {out5}};
	{{request5,act5,act0},{} -> {request5}};
	{{request5,act5,act1},{} -> {request5}};
	{{request5,act5,act2},{} -> {request5}};
	{{request5,act5,act3},{} -> {request5}};
	{{request5,act5,act4},{} -> {request5}};
	{{request5},{act5} -> {request5}};
	{{request5,act5},{act0,act1,act2,act3,act4,lock} -> {in5,lock}};
	{{in5,act5},{} -> {out5,done}};
	{{in5},{act5} -> {in5}};

	{{lock},{done} -> {lock}};
}
context-entities {act0,act1,act2,act3,act4,act5}

initial-contexts { {out0,out1,out2,out3,out4,out5} }

rsctl-property { AG(~(in0 AND in1) AND ~(in0 AND in2) AND ~(in0 AND in3) AND ~(in0 AND in4) AND ~(in0 AND in5) AND ~(in1 AND in2) AND ~(in1 AND in3) AND ~(in1 AND in4) AND ~(in1 AND in5) AND ~(in2 AND in3) AND ~(in2 AND in4) AND ~(in2 AND in5) AND ~(in3 AND in4) AND ~(in3 AND in5) AND ~(in4 AND in5)) }
