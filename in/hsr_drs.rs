options { use-context-automaton; }

reactions {
    mainA {
        {{hsf},{hsp} -> {hsf3}}; #10
        {{hsf,hsp,mfp},{dI} -> {hsf3}}; #11
        {{hsf3},{hse,hsp} -> {hsf}}; #12
        {{hsf3,hsp,mfp},{hse} -> {hsf}}; #13
        {{hsf3,hse},{hsp} -> {hsf3:hse}}; #14
        {{hsf3,hse,hsp,mfp},{dI} -> {hsf3:hse}}; #15
        {{hse},{hsf3} -> {hse}}; #16
        {{hse,hsf3,hsp},{mfp} -> {hse}}; #17
        {{hsf3:hse},{hsp} -> {hsf3:hse,hsp}}; #18
        {{hsf3:hse,hsp,mfp},{dI} -> {hsf3:hse,hsp}}; #19
        {{hsp,hsf},{mfp} -> {hsp:hsf}}; #20
        {{hsp:hsf,stress},{nostress} -> {hsp,hsf}}; #21
        {{hsp:hsf,nostress},{stress} -> {hsp:hsf}}; #22
        {{hsp,hsf3},{mfp} -> {hsp:hsf}}; #23
        {{hsp,hsf3:hse},{mfp} -> {hsp:hsf,hse}}; 
        {{prot,stress},{nostress} -> {prot,mfp}};
        {{prot,nostress},{stress} -> {prot}};
        {{hsp,mfp},{dI} -> {hsp:mfp}};
        {{mfp},{hsp} -> {mfp}};
        {{hsp:mfp},{dI} -> {hsp,prot}};
    };

    dummy {
        {{mfp},{hsp} -> {mfp}};
    };
    
}

context-automaton {
	states { s0, s1 }
    init-state { s0 }
	transitions {
		{ mainA={hsf,prot,hse,nostress} }: s0 -> s1;
		{ mainA={hsf,prot,hsp:hsf,stress} }: s0 -> s1;
		{ mainA={hsp,prot,hsf3:hse,mfp,hsp:mfp,nostress} }: s0 -> s1;
		{ mainA={stress} }: s1 -> s1;
		{ mainA={nostress} }: s1 -> s1;
		{ mainA={stress,nostress} }: s1 -> s1;
	}
}

# P1
rsctl-property { A<mainA.stress XOR mainA.nostress>G(mainA.hse OR mainA.hsf3:hse IMPLIES A<mainA.stress XOR mainA.nostress>X(mainA.hse OR mainA.hsf3:hse)) }

# P2
#rsctl-property { A[{stress},{nostress}]G(~(hse AND hsf3:hse) IMPLIES A[{stress},{nostress}]X(~(hse AND hsf3:hse))) }

# P3
#rsctl-property { A[{stress},{nostress}]G(prot IMPLIES A[{stress},{nostress}]X(prot)) }

# P4
#rsctl-property { A[{stress},{nostress}]G(mfp IMPLIES A[{stress},{nostress}]X(mfp OR hsp:mfp)) }
#rsctl-property { A< stress XOR nostress >G(mfp IMPLIES A[{stress},{nostress}]X(mfp OR hsp:mfp)) }

# P5
#rsctl-property { A[{stress},{nostress}]G( ((hsf XOR hsf3 XOR hsf3:hse XOR hsp:hsf) OR ~(hsf OR hsf3 OR hsf3:hse OR hsp:hsf)) IMPLIES A[{stress},{nostress}]X( (hsf XOR hsf3 XOR hsf3:hse XOR hsp:hsf) OR ~(hsf OR hsf3 OR hsf3:hse OR hsp:hsf) ) )  }

# P6
#rsctl-property { A[{nostress}]G(hsp:hsf IMPLIES A[{nostress}]X (hsp:hsf)) }

