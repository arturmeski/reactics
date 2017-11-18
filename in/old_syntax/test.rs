#
# Testowy RS
#

reactions {
    { { a;b; },{ c;d; } -> { x;y;c; } };
}

action-atoms {
    e;
}

initial-state {
    a; b;
}

ctl-property {
    ( EF ( (x AND y)  ) )
}

