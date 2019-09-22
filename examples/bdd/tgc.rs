
options { use-context-automaton; }
reactions {

    proc0 {
        {{out}, {} -> {approach}};
        {{approach}, {req} -> {req}};
        {{allowed}, {} -> {in}};
        {{in}, {} -> {out,leave}};
        {{req}, {in} -> {req}};
    };

    proc1 {
        {{out}, {} -> {approach}};
        {{approach}, {req} -> {req}};
        {{allowed}, {} -> {in}};
        {{in}, {} -> {out,leave}};
        {{req}, {in} -> {req}};
    };

    proc2 {
        {{out}, {} -> {approach}};
        {{approach}, {req} -> {req}};
        {{allowed}, {} -> {in}};
        {{in}, {} -> {out,leave}};
        {{req}, {in} -> {req}};
    };
}

context-automaton {
    states { init, green, red }
    init-state { init }
    transitions {
        { proc0={out} proc1={out} proc2={out} }: init -> green;
        { proc0={} proc1={} proc2={} }: green -> green : ~proc0.req AND ~proc1.req AND ~proc2.req;
        { proc0={allowed} }: green -> red : proc0.req;
        { proc1={allowed} }: green -> red : proc1.req;
        { proc2={allowed} }: green -> red : proc2.req;
        { proc0={} }: red -> green : proc0.leave;
        { proc1={} }: red -> green : proc1.leave;
        { proc2={} }: red -> green : proc2.leave;
        { proc0={} proc1={} proc2={} } : red -> red : ~proc0.leave AND ~proc1.leave AND ~proc2.leave;
    }
}

rsctlk-property { f1 : EF( proc0.in ) AND EF( proc1.in ) AND EF( proc2.in ) }

rsctlk-property { f2 : AG( proc0.in IMPLIES K[proc0](~proc1.in AND ~proc2.in) ) }

