from rs import *
from smt import *
from logics import *
from rsltl_shortcuts import *

from itertools import chain, combinations

import sys
import resource
import argparse


def powerset(iterable, N=None):
    if N is None:
        N = len(s)
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(N + 1))


def mutex_param_bench(cmd_args):
    """
    Mutex Benchmark
    
    Parametric
    """

    base_entities = ["out", "req", "in", "act"]
    shared_entities = ["lock", "done", "s"]

    if not cmd_args.scaling_parameter:
        print("Missing scaling parameter")
        return
    n_proc = int(cmd_args.scaling_parameter)

    r = ReactionSystemWithConcentrationsParam()

    def E(a, b, c=1):
        return (a + "_" + str(b), c)

    for i in range(n_proc):
        for ent in base_entities:
            max_conc = 1
            if ent == "in":
                max_conc = 3
            elif ent == "req":
                max_conc = 2
            r.add_bg_set_entity(E(ent, i, max_conc))

    for ent in shared_entities:
        max_conc = 1
        r.add_bg_set_entity((ent, max_conc))

    ###################################################

    Inhib = [("s", 1)]

    for i in range(n_proc):

        r.add_reaction([E("out", i), E("act", i)], Inhib, [E("req", i)])
        r.add_reaction([E("out", i)], [E("act", i)], [E("out", i)])

        for j in range(n_proc):
            if i != j:
                r.add_reaction(
                    [E("req", i), E("act", i), E("act", j)], Inhib, [E("req", i)]
                )

        r.add_reaction([E("req", i)], [E("act", i)], [E("req", i, 2)])

        enter_inhib = [E("act", j) for j in range(n_proc) if i != j] + [("lock", 1)]
        r.add_reaction(
            [E("req", i, 2), E("act", i)], enter_inhib, [E("in", i, 3), ("lock", 1)]
        )

        r.add_reaction([E("in", i, 3), E("act", i)], Inhib, [E("in", i, 2)])
        r.add_reaction([E("in", i, 2), E("act", i)], Inhib, [E("in", i, 1)])

        r.add_reaction([E("in", i), E("act", i)], Inhib, [E("out", i), ("done", 1)])
        r.add_reaction([E("in", i)], [E("act", i)], [E("in", i)])

    r.add_reaction([("lock", 1)], [("done", 1)], [("lock", 1)])

    lda1 = r.get_param("lda1")
    lda2 = r.get_param("lda2")
    lda3 = r.get_param("lda3")

    r.add_reaction(lda1, lda2, lda3)

    ###################################################

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")

    init_ctx = []
    for i in range(n_proc):
        init_ctx.append(E("out", i))

    # the experiments starts with adding x and y:
    c.add_transition("0", init_ctx, "1")

    all_act = powerset([E("act", i) for i in range(n_proc)], 2)

    for actions in all_act:
        actions = list(actions)

        c.add_transition("1", actions, "1")

    # for all the remaining steps we have empty context sequences
    # c.add_transition("1", [], "1")
    # c.add_transition("1", [("h", 1)], "1")

    ###################################################

    rc = ReactionSystemWithAutomaton(r, c)
    rc.show()

    f_attack = ltl_F(
        True, bag_And(bag_entity("in_0") == 1, bag_entity("in_" + str(n_proc - 1)) == 1)
    )

    ent_of_Nth_proc = [
        ent + "_" + str(n_proc - 1) for ent in base_entities
    ] + shared_entities
    disallow = ["in_" + str(n_proc - 1)]
    for ent in r.background_set:
        if ent not in ent_of_Nth_proc:
            disallow.append(ent)

    # disallow.append("act_" + str(n_proc-1))

    # disallow = ["in_0", "in_" + str(n_proc)] #, "req_0", "req_1"]
    lda1_disallow = [param_entity(lda1, ent) == 0 for ent in disallow]
    lda2_disallow = [param_entity(lda2, ent) == 0 for ent in disallow]
    lda3_disallow = [param_entity(lda3, ent) == 0 for ent in disallow]
    lda_disallow = lda1_disallow + lda2_disallow + lda3_disallow

    # for bent in base_entities:
    #     print(param_entity(lda3, bent + "_0"))

    param_constr = param_And(*lda_disallow)

    smt_rsc = SmtCheckerRSCParam(rc, optimise=cmd_args.optimise)
    smt_rsc.check_rsltl(
        formulae_list=[f_attack], param_constr=param_constr
    )  # , max_level=4, cont_if_sat=True)

    log_suffix = ""
    if cmd_args.optimise:
        log_suffix = "_OPT"

    time = 0
    mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)
    filename_t = "bench_mutex_param" + log_suffix + "_time.dat"
    filename_m = "bench_mutex_param" + log_suffix + "_mem.dat"
    time = smt_rsc.get_verification_time()

    with open(filename_t, "a") as f:
        log_str = "{:d} {:f}\n".format(n_proc, time)
        f.write(log_str)

    with open(filename_m, "a") as f:
        log_str = "{:d} {:f}\n".format(n_proc, mem_usage)
        f.write(log_str)


def mutex_nonparam_bench(cmd_args):
    """
    Mutex Benchmark
    
    Parametric
    """

    base_entities = ["out", "req", "in", "act"]
    shared_entities = ["lock", "done", "s"]

    if not cmd_args.scaling_parameter:
        raise RuntimeError("Missing scaling parameter")
    n_proc = int(cmd_args.scaling_parameter)

    r = ReactionSystemWithConcentrationsParam()

    def E(a, b):
        return (a + "_" + str(b), 1)

    for i in range(n_proc):
        for ent in base_entities:
            r.add_bg_set_entity(E(ent, i))

    for ent in shared_entities:
        r.add_bg_set_entity((ent, 1))

    ###################################################

    Inhib = [("s", 1)]

    for i in range(n_proc):

        r.add_reaction([E("out", i), E("act", i)], Inhib, [E("req", i)])
        r.add_reaction([E("out", i)], [E("act", i)], [E("out", i)])

        for j in range(n_proc):
            if i != j:
                r.add_reaction(
                    [E("req", i), E("act", i), E("act", j)], Inhib, [E("req", i)]
                )

        r.add_reaction([E("req", i)], [E("act", i)], [E("req", i)])

        enter_inhib = [E("act", j) for j in range(n_proc) if i != j] + [("lock", 1)]
        r.add_reaction(
            [E("req", i), E("act", i)], enter_inhib, [E("in", i), ("lock", 1)]
        )

        r.add_reaction([E("in", i), E("act", i)], Inhib, [E("out", i), ("done", 1)])
        r.add_reaction([E("in", i)], [E("act", i)], [E("in", i)])

    r.add_reaction([("lock", 1)], [("done", 1)], [("lock", 1)])

    r.add_reaction(
        [E("out", n_proc - 1)], [("s", 1)], [("done", 1), E("req", n_proc - 1)]
    )

    ###################################################

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")

    init_ctx = []
    for i in range(n_proc):
        init_ctx.append(E("out", i))

    # the experiments starts with adding x and y:
    c.add_transition("0", init_ctx, "1")

    all_act = powerset([E("act", i) for i in range(n_proc)], 2)

    for actions in all_act:
        actions = list(actions)

        c.add_transition("1", actions, "1")

    # for all the remaining steps we have empty context sequences
    # c.add_transition("1", [], "1")
    # c.add_transition("1", [("h", 1)], "1")

    ###################################################

    rc = ReactionSystemWithAutomaton(r, c)
    rc.show()

    f_attack = ltl_F(
        True, bag_And(bag_entity("in_0") == 1, bag_entity("in_" + str(n_proc - 1)) == 1)
    )

    smt_rsc = SmtCheckerRSCParam(rc, optimise=cmd_args.optimise)
    smt_rsc.check_rsltl(formulae_list=[f_attack])

    time = 0
    mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)
    filename_t = "bench_mutex_nonparam_time.dat"
    filename_m = "bench_mutex_nonparam_mem.dat"
    time = smt_rsc.get_verification_time()

    with open(filename_t, "a") as f:
        log_str = "{:d} {:f}\n".format(n_proc, time)
        f.write(log_str)

    with open(filename_m, "a") as f:
        log_str = "{:d} {:f}\n".format(n_proc, mem_usage)
        f.write(log_str)


def mutex_nonparam_bench_oldimpl(cmd_args):
    """
    Mutex Benchmark
    
    Parametric
    """

    base_entities = ["out", "req", "in", "act"]
    shared_entities = ["lock", "done", "s"]

    if not cmd_args.scaling_parameter:
        raise RuntimeError("Missing scaling parameter")
    n_proc = int(cmd_args.scaling_parameter)

    r = ReactionSystemWithConcentrations()

    def E(a, b):
        return (a + "_" + str(b), 1)

    for i in range(n_proc):
        for ent in base_entities:
            r.add_bg_set_entity(E(ent, i))

    for ent in shared_entities:
        r.add_bg_set_entity((ent, 1))

    ###################################################

    Inhib = [("s", 1)]

    for i in range(n_proc):

        r.add_reaction([E("out", i), E("act", i)], Inhib, [E("req", i)])
        r.add_reaction([E("out", i)], [E("act", i)], [E("out", i)])

        for j in range(n_proc):
            if i != j:
                r.add_reaction(
                    [E("req", i), E("act", i), E("act", j)], Inhib, [E("req", i)]
                )

        r.add_reaction([E("req", i)], [E("act", i)], [E("req", i)])

        enter_inhib = [E("act", j) for j in range(n_proc) if i != j] + [("lock", 1)]
        r.add_reaction(
            [E("req", i), E("act", i)], enter_inhib, [E("in", i), ("lock", 1)]
        )

        r.add_reaction([E("in", i), E("act", i)], Inhib, [E("out", i), ("done", 1)])
        r.add_reaction([E("in", i)], [E("act", i)], [E("in", i)])

    r.add_reaction([("lock", 1)], [("done", 1)], [("lock", 1)])

    r.add_reaction(
        [E("out", n_proc - 1)], [("s", 1)], [("done", 1), E("req", n_proc - 1)]
    )

    ###################################################

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")

    init_ctx = []
    for i in range(n_proc):
        init_ctx.append(E("out", i))

    # the experiments starts with adding x and y:
    c.add_transition("0", init_ctx, "1")

    all_act = powerset([E("act", i) for i in range(n_proc)], 2)

    for actions in all_act:
        actions = list(actions)

        c.add_transition("1", actions, "1")

    # for all the remaining steps we have empty context sequences
    # c.add_transition("1", [], "1")
    # c.add_transition("1", [("h", 1)], "1")

    ###################################################

    rc = ReactionSystemWithAutomaton(r, c)
    rc.show()

    f_attack = ltl_F(
        True, bag_And(bag_entity("in_0") == 1, bag_entity("in_" + str(n_proc - 1)) == 1)
    )

    smt_rsc = SmtCheckerRSC(rc)
    smt_rsc.check_rsltl(formula=f_attack)

    time = 0
    mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)
    filename_t = "bench_mutex_nonparam_oldimpl_time.dat"
    filename_m = "bench_mutex_nonparam_oldimpl_mem.dat"
    time = smt_rsc.get_verification_time()

    with open(filename_t, "a") as f:
        log_str = "{:d} {:f}\n".format(n_proc, time)
        f.write(log_str)

    with open(filename_m, "a") as f:
        log_str = "{:d} {:f}\n".format(n_proc, mem_usage)
        f.write(log_str)


def state_translate_rsc2rs(p):
    return [e[0] + "#" + str(e[1]) for e in p]


def mutex_bench_main(cmd_args):

    if not cmd_args.special_mode:
        print("Missing special mode parameter")
        print("*    1 - parametric")
        print("*    2 - non-parametric (with parametric implementation)")
        print("*    3 - non-parametric (with non-parametric implementation)")
        return

    smode = int(cmd_args.special_mode)

    if smode == 1:
        mutex_param_bench(cmd_args)
    elif smode == 2:
        mutex_nonparam_bench(cmd_args)
    elif smode == 3:
        mutex_nonparam_bench_oldimpl(cmd_args)
    else:
        print("Unrecognised mode")
        return


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v", "--verbose", help="turn verbosity on", action="store_true"
    )
    parser.add_argument(
        "-o",
        "--optimise",
        help="minimise the parametric computation result",
        action="store_true",
    )
    parser.add_argument(
        "-n",
        "--scaling-parameter",
        help="scaling parameter value (used in some benchmarks)",
    )
    parser.add_argument(
        "-s", "--special_mode", help="special mode (used in some benchmarks)"
    )

    args = parser.parse_args()

    mutex_bench_main(args)


if __name__ == "__main__":
    main()

# EOF
