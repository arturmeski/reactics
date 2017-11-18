reactions {
    {{hsf},{hsp} -> {hsf3}}; 
    {{hsf,hsp,mfp},{dI} -> {hsf3}};
    {{hsf3},{hse,hsp} -> {hsf}}; 
    {{hsf3,hsp,mfp},{hse} -> {hsf}}; 
    {{hsf3,hse},{hsp} -> {hsf3:hse}};
    {{hsf3,hse,hsp,mfp},{dI} -> {hsf3:hse}};
    {{hse},{hsf3} -> {hse}}; 
    {{hse,hsf3,hsp},{mfp} -> {hse}};
    {{hsf3:hse},{hsp} -> {hsf3:hse,hsp}};
    {{hsf3:hse,hsp,mfp},{dI} -> {hsf3:hse,hsp}};
    {{hsp,hsf},{mfp} -> {hsp:hsf}};
    {{hsp:hsf,stress},{nostress} -> {hsp,hsf}};
    {{hsp:hsf,nostress},{stress} -> {hsp:hsf}};
    {{hsp,hsf3},{mfp} -> {hsp:hsf}};
    {{hsp,hsf3:hse},{mfp} -> {hsp:hsf,hse}}; 
    {{prot,stress},{nostress} -> {prot,mfp}};
    {{prot,nostress},{stress} -> {prot}};
    {{hsp,mfp},{dI} -> {hsp:mfp}};
    {{mfp},{hsp} -> {mfp}};
    {{hsp:mfp},{dI} -> {hsp,prot}};
}

context-entities { stress, nostress }
initial-contexts { {hsf,prot,hse,nostress},{hsf,prot,hsp:hsf,stress},{hsp,prot,hsf3:hse,mfp,hsp:mfp,nostress} }

# P1
rsctl-property { A[{stress},{nostress}]G(hse OR hsf3:hse IMPLIES A[{stress},{nostress}]X(hse OR hsf3:hse)) }

# P2
#rsctl-property { A[{stress},{nostress}]G(~(hse AND hsf3:hse) IMPLIES A[{stress},{nostress}]X(~(hse AND hsf3:hse))) }

# P3
#rsctl-property { A[{stress},{nostress}]G(prot IMPLIES A[{stress},{nostress}]X(prot)) }

# P4
#rsctl-property { A[{stress},{nostress}]G(mfp IMPLIES A[{stress},{nostress}]X(mfp OR hsp:mfp)) }

# P5
#rsctl-property { A[{stress},{nostress}]G( ((hsf XOR hsf3 XOR hsf3:hse XOR hsp:hsf) OR ~(hsf OR hsf3 OR hsf3:hse OR hsp:hsf)) IMPLIES A[{stress},{nostress}]X( (hsf XOR hsf3 XOR hsf3:hse XOR hsp:hsf) OR ~(hsf OR hsf3 OR hsf3:hse OR hsp:hsf) ) )  }

# P6
#rsctl-property { A[{nostress}]G(hsp:hsf IMPLIES A[{nostress}]X (hsp:hsf)) }
