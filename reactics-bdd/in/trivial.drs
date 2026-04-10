options { use-context-automaton; };

reactions {
    m {
        {{e1,e4},{e2} -> {e1,e2}}; 
        {{e2},{e4} -> {e1,e3,e4}}; 
	{{e1,e3},{e2} -> {e1,e2}};
	{{e3},{e2} -> {e1}};
    };

};

context-automaton {
	states { s0, s1 };
    init-state { s0 };
	transitions {
		{ m={e1,e4} }: s0 -> s1;
		{ m={} }: s1 -> s1;
		{ m={e4} }: s1 -> s1;
	};
};

