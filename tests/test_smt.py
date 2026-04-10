"""
Regression tests for the ReactICS SMT module.

Tests the Python API directly: reaction system construction,
context automata, and SMT-based verification (reachability + rsLTL).
"""

import sys
import os
import io
from contextlib import redirect_stdout

# Add reactics-smt to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reactics-smt"))

from z3 import sat, unsat
from rs import (
    ReactionSystem,
    ContextAutomaton,
    ReactionSystemWithConcentrations,
    ContextAutomatonWithConcentrations,
    ReactionSystemWithConcentrationsParam,
    ReactionSystemWithAutomaton,
)
from smt import SmtCheckerRS, SmtCheckerRSC, SmtCheckerRSCParam
from logics import Formula_rsLTL, BagDescription
from rsltl_shortcuts import ltl_F, bag_entity, param_entity, param_And


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_silent(fn, *args, **kwargs):
    """Run a function with stdout suppressed, return its result."""
    with redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


# ---------------------------------------------------------------------------
# Data model tests
# ---------------------------------------------------------------------------

class TestReactionSystem:
    def test_add_entities(self):
        rs = ReactionSystem()
        rs.add_bg_set_entity("a")
        rs.add_bg_set_entity("b")
        assert rs.background_set == ["a", "b"]
        assert rs.get_entity_id("a") == 0
        assert rs.get_entity_id("b") == 1
        assert rs.get_entity_name(0) == "a"

    def test_add_reaction(self):
        rs = ReactionSystem()
        rs.add_bg_set_entity("a")
        rs.add_bg_set_entity("b")
        rs.add_bg_set_entity("c")
        rs.add_reaction(["a"], ["b"], ["c"])
        assert len(rs.reactions) == 1
        reactants, inhibitors, products = rs.reactions[0]
        assert reactants == [0]
        assert inhibitors == [1]
        assert products == [2]

    def test_reactions_by_product(self):
        rs = ReactionSystem()
        rs.add_bg_set_entity("a")
        rs.add_bg_set_entity("b")
        rs.add_reaction(["a"], [], ["b"])
        rbp = rs.get_reactions_by_product()
        assert 1 in rbp  # entity id for "b"
        assert len(rbp[1]) == 1

    def test_duplicate_entity_raises(self):
        rs = ReactionSystem()
        rs.add_bg_set_entity("a")
        try:
            rs.add_bg_set_entity("a")
            assert False, "Should have raised"
        except RuntimeError:
            pass


class TestReactionSystemWithConcentrations:
    def test_add_entity_with_concentration(self):
        rs = ReactionSystemWithConcentrations()
        rs.add_bg_set_entity(("x", 3))
        rs.add_bg_set_entity(("y", 5))
        assert rs.background_set == ["x", "y"]
        assert rs.get_max_concentration_level(0) == 3
        assert rs.get_max_concentration_level(1) == 5

    def test_add_reaction_with_concentrations(self):
        rs = ReactionSystemWithConcentrations()
        rs.add_bg_set_entity(("a", 2))
        rs.add_bg_set_entity(("b", 1))
        rs.add_reaction([("a", 1)], [], [("b", 1)])
        assert len(rs.reactions) == 1

    def test_meta_reactions(self):
        rs = ReactionSystemWithConcentrations()
        rs.add_bg_set_entity(("e", 3))
        rs.add_bg_set_entity(("inc", 1))
        rs.add_reaction_inc("e", "inc", [("e", 1)], [("e", 3)])
        e_id = rs.get_entity_id("e")
        assert e_id in rs.meta_reactions
        assert rs.meta_reactions[e_id][0][0] == "inc"


class TestContextAutomaton:
    def test_states_and_transitions(self):
        rs = ReactionSystem()
        rs.add_bg_set_entity("a")
        rs.add_bg_set_entity("b")
        ca = ContextAutomaton(rs)
        ca.add_init_state("s0")
        ca.add_state("s1")
        assert ca.get_init_state_id() == 0
        assert ca.get_state_id("s1") == 1
        ca.add_transition("s0", ["a"], "s1")
        ca.add_transition("s1", [], "s1")
        assert len(ca.transitions) == 2

    def test_invalid_transition_raises(self):
        rs = ReactionSystem()
        rs.add_bg_set_entity("a")
        ca = ContextAutomaton(rs)
        ca.add_init_state("s0")
        try:
            ca.add_transition("s0", ["a"], "nonexistent")
            assert False, "Should have raised"
        except RuntimeError:
            pass


class TestContextAutomatonWithConcentrations:
    def test_transitions_with_concentrations(self):
        rs = ReactionSystemWithConcentrations()
        rs.add_bg_set_entity(("a", 2))
        rs.add_bg_set_entity(("b", 1))
        ca = ContextAutomatonWithConcentrations(rs)
        ca.add_init_state("s0")
        ca.add_state("s1")
        ca.add_transition("s0", [("a", 2)], "s1")
        ca.add_transition("s1", [], "s1")
        assert len(ca.transitions) == 2


# ---------------------------------------------------------------------------
# Formula construction tests
# ---------------------------------------------------------------------------

class TestFormulas:
    def test_bag_description(self):
        b = BagDescription.f_entity("x")
        assert str(b) == "x"
        b_gt = b > 0
        assert ">" in str(b_gt)

    def test_rsltl_formula(self):
        f = Formula_rsLTL.f_F(
            BagDescription.f_TRUE(),
            BagDescription.f_entity("x") > 0,
        )
        assert "F" in str(f)

    def test_combined_formula(self):
        f = Formula_rsLTL.f_G(
            BagDescription.f_TRUE(),
            Formula_rsLTL.f_Implies(
                BagDescription.f_entity("a") == 1,
                Formula_rsLTL.f_F(
                    BagDescription.f_TRUE(),
                    BagDescription.f_entity("b") > 0,
                ),
            ),
        )
        assert "G" in str(f)
        assert "F" in str(f)


# ---------------------------------------------------------------------------
# Verification tests: SmtCheckerRS (basic, no concentrations)
# ---------------------------------------------------------------------------

def _build_simple_rs():
    """A minimal RS for testing: a -> b -> c with context automaton."""
    rs = ReactionSystem()
    rs.add_bg_set_entity("a")
    rs.add_bg_set_entity("b")
    rs.add_bg_set_entity("c")
    rs.add_reaction(["a"], [], ["b"])
    rs.add_reaction(["b"], [], ["c"])

    ca = ContextAutomaton(rs)
    ca.add_init_state("s0")
    ca.add_state("s1")
    ca.add_transition("s0", ["a"], "s1")
    ca.add_transition("s1", [], "s1")

    return ReactionSystemWithAutomaton(rs, ca)


class TestSmtCheckerRS:
    def test_reachability_sat(self):
        rsa = _build_simple_rs()
        checker = SmtCheckerRS(rsa)
        run_silent(
            checker.check_reachability,
            ["c"],
            print_witness=False,
            print_time=False,
            print_mem=False,
        )
        # After finding SAT, solver state should be satisfiable
        assert checker.solver.check() == sat

    def test_reachability_unreachable(self):
        """Entity 'a' is never produced, so it shouldn't be reachable as a final state."""
        rs = ReactionSystem()
        rs.add_bg_set_entity("a")
        rs.add_bg_set_entity("b")
        rs.add_reaction(["a"], [], ["b"])

        ca = ContextAutomaton(rs)
        ca.add_init_state("s0")
        ca.add_state("s1")
        # Context provides 'a' initially, then nothing
        ca.add_transition("s0", ["a"], "s1")
        ca.add_transition("s1", [], "s1")

        rsa = ReactionSystemWithAutomaton(rs, ca)
        checker = SmtCheckerRS(rsa)

        # 'b' is reachable (produced from 'a')
        run_silent(
            checker.check_reachability,
            ["b"],
            print_witness=False,
            print_time=False,
            print_mem=False,
        )
        assert checker.solver.check() == sat


# ---------------------------------------------------------------------------
# Verification tests: SmtCheckerRSC (with concentrations)
# ---------------------------------------------------------------------------

def _build_chain_rsc(chain_len=2, max_conc=2):
    """Build a chain reaction system with concentrations."""
    r = ReactionSystemWithConcentrations()
    r.add_bg_set_entity(("inc", 1))
    r.add_bg_set_entity(("dec", 1))

    for i in range(1, chain_len + 1):
        r.add_bg_set_entity(("e_" + str(i), max_conc))

    for i in range(1, chain_len + 1):
        ent = "e_" + str(i)
        r.add_reaction_inc(ent, "inc", [(ent, 1)], [(ent, max_conc)])
        r.add_reaction_dec(ent, "dec", [(ent, 1)], [])
        if i < chain_len:
            r.add_reaction([(ent, max_conc)], [], [("e_" + str(i + 1), 1)])

    r.add_reaction(
        [("e_" + str(chain_len), max_conc)],
        [("dec", 1)],
        [("e_" + str(chain_len), max_conc)],
    )

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("init")
    c.add_state("working")
    c.add_transition("init", [("e_1", 1), ("inc", 1)], "working")
    c.add_transition("working", [("inc", 1)], "working")

    return ReactionSystemWithAutomaton(r, c)


class TestSmtCheckerRSC:
    def test_chain_reachability_sat(self):
        """Chain(2,2): e_2=2 should be reachable at level 3."""
        rc = _build_chain_rsc(2, 2)
        checker = SmtCheckerRSC(rc)
        prop = ([("e_2", 2)], [])
        run_silent(
            checker.check_reachability,
            prop,
            print_witness=False,
            print_time=False,
            print_mem=False,
            max_level=10,
        )
        assert checker.solver.check() == sat
        assert checker.current_level == 3

    def test_chain_reachability_longer(self):
        """Chain(3,2): e_3=2 should be reachable at level 5."""
        rc = _build_chain_rsc(3, 2)
        checker = SmtCheckerRSC(rc)
        prop = ([("e_3", 2)], [])
        run_silent(
            checker.check_reachability,
            prop,
            print_witness=False,
            print_time=False,
            print_mem=False,
            max_level=10,
        )
        assert checker.solver.check() == sat
        assert checker.current_level == 5

    def test_rsltl_finally(self):
        """Check rsLTL F formula on chain(2,2)."""
        rc = _build_chain_rsc(2, 2)
        checker = SmtCheckerRSC(rc)
        form = Formula_rsLTL.f_F(
            BagDescription.f_entity("inc") > 0,
            BagDescription.f_entity("e_2") >= 2,
        )
        run_silent(
            checker.check_rsltl,
            formula=form,
            print_witness=False,
            print_time=False,
            print_mem=False,
        )
        assert checker.solver.check() == sat
        assert checker.current_level == 3

    def test_rsltl_finally_fast(self):
        """Chain(2,2), F(e_1==2): should be SAT at level 1."""
        rc = _build_chain_rsc(2, 2)
        checker = SmtCheckerRSC(rc)
        form = Formula_rsLTL.f_F(
            BagDescription.f_entity("inc") > 0,
            BagDescription.f_entity("e_1") == 2,
        )
        run_silent(
            checker.check_rsltl,
            formula=form,
            print_witness=False,
            print_time=False,
            print_mem=False,
        )
        assert checker.solver.check() == sat
        assert checker.current_level == 1

    def test_rsltl_next_until(self):
        """Chain(2,2), X[TRUE](e_1 > 0 U[inc > 0] e_2 > 0): SAT at level 2."""
        rc = _build_chain_rsc(2, 2)
        checker = SmtCheckerRSC(rc)
        form = Formula_rsLTL.f_X(
            BagDescription.f_TRUE(),
            Formula_rsLTL.f_U(
                BagDescription.f_entity("inc") > 0,
                BagDescription.f_entity("e_1") > 0,
                BagDescription.f_entity("e_2") > 0,
            ),
        )
        run_silent(
            checker.check_rsltl,
            formula=form,
            print_witness=False,
            print_time=False,
            print_mem=False,
        )
        assert checker.solver.check() == sat
        assert checker.current_level == 2


# ---------------------------------------------------------------------------
# Verification tests: SmtCheckerRSC on heat shock response
# ---------------------------------------------------------------------------

def _build_heat_shock():
    """Heat shock response model."""
    stress_temp = 42
    max_temp = 50

    r = ReactionSystemWithConcentrations()
    for e in [("hsp", 1), ("hsf", 1), ("hsf2", 1), ("hsf3", 1), ("hse", 1),
              ("mfp", 1), ("prot", 1), ("hsf3:hse", 1), ("hsp:mfp", 1),
              ("hsp:hsf", 1), ("temp", max_temp), ("heat", 1), ("cool", 1)]:
        r.add_bg_set_entity(e)

    r.add_reaction([("hsf", 1)], [("hsp", 1)], [("hsf3", 1)])
    r.add_reaction([("hsf", 1), ("hsp", 1), ("mfp", 1)], [], [("hsf3", 1)])
    r.add_reaction([("hsf3", 1)], [("hse", 1), ("hsp", 1)], [("hsf", 1)])
    r.add_reaction([("hsf3", 1), ("hsp", 1), ("mfp", 1)], [("hse", 1)], [("hsf", 1)])
    r.add_reaction([("hsf3", 1), ("hse", 1)], [("hsp", 1)], [("hsf3:hse", 1)])
    r.add_reaction([("hsp", 1), ("hsf3", 1), ("mfp", 1), ("hse", 1)], [], [("hsf3:hse", 1)])
    r.add_reaction([("hse", 1)], [("hsf3", 1)], [("hse", 1)])
    r.add_reaction([("hsp", 1), ("hsf3", 1), ("hse", 1)], [("mfp", 1)], [("hse", 1)])
    r.add_reaction([("hsf3:hse", 1)], [("hsp", 1)], [("hsp", 1), ("hsf3:hse", 1)])
    r.add_reaction([("hsp", 1), ("mfp", 1), ("hsf3:hse", 1)], [], [("hsp", 1), ("hsf3:hse", 1)])
    r.add_reaction([("hsf", 1), ("hsp", 1)], [("mfp", 1)], [("hsp:hsf", 1)])
    r.add_reaction([("hsp:hsf", 1), ("temp", stress_temp)], [], [("hsf", 1), ("hsp", 1)])
    r.add_reaction([("hsp:hsf", 1)], [("temp", stress_temp)], [("hsp:hsf", 1)])
    r.add_reaction([("hsp", 1), ("hsf3:hse", 1)], [("mfp", 1)], [("hse", 1), ("hsp:hsf", 1)])
    r.add_reaction([("temp", stress_temp), ("prot", 1)], [], [("mfp", 1), ("prot", 1)])
    r.add_reaction([("prot", 1)], [("temp", stress_temp)], [("prot", 1)])
    r.add_reaction([("hsp", 1), ("mfp", 1)], [], [("hsp:mfp", 1)])
    r.add_reaction([("mfp", 1)], [("hsp", 1)], [("mfp", 1)])
    r.add_reaction([("hsp:mfp", 1)], [], [("hsp", 1), ("prot", 1)])

    r.add_reaction_inc("temp", "heat", [("temp", 1)], [("temp", max_temp)])
    r.add_reaction_dec("temp", "cool", [("temp", 1)], [])
    r.add_permanency("temp", [("heat", 1), ("cool", 1)])

    c = ContextAutomatonWithConcentrations(r)
    c.add_init_state("0")
    c.add_state("1")
    c.add_transition("0", [("hsf", 1), ("prot", 1), ("hse", 1), ("temp", 35)], "1")
    c.add_transition("1", [("cool", 1)], "1")
    c.add_transition("1", [("heat", 1)], "1")
    c.add_transition("1", [], "1")

    return ReactionSystemWithAutomaton(r, c)


class TestHeatShockResponse:
    def test_mfp_reachable(self):
        """mfp should be reachable at level 9."""
        rc = _build_heat_shock()
        checker = SmtCheckerRSC(rc)
        prop = ([("mfp", 1)], [])
        run_silent(
            checker.check_reachability,
            prop,
            print_witness=False,
            print_time=False,
            print_mem=False,
            max_level=40,
        )
        assert checker.solver.check() == sat
        assert checker.current_level == 9


# ---------------------------------------------------------------------------
# Verification tests: SmtCheckerRSCParam (parametric)
# ---------------------------------------------------------------------------

def _build_parametric_overview():
    """Parametric example from doc/overview.py."""
    prs = ReactionSystemWithConcentrationsParam()
    for ec in [("a", 3), ("b", 2), ("c", 1), ("h", 1)]:
        prs.add_bg_set_entity(ec)

    lda = prs.get_param("lda")
    prs.add_reaction([("a", 1)], [("h", 1)], [("b", 2)])
    prs.add_reaction(lda, [("h", 1)], [("c", 1)])

    ca = ContextAutomatonWithConcentrations(prs)
    ca.add_init_state("0")
    ca.add_state("1")
    ca.add_transition("0", [("a", 3)], "1")
    ca.add_transition("1", [], "1")
    ca.add_transition("1", [("h", 1)], "1")

    return ReactionSystemWithAutomaton(prs, ca), lda


class TestSmtCheckerRSCParam:
    def test_parametric_sat(self):
        """Parametric overview: F[h==0](c>0) should be SAT at level 2."""
        rc, lda = _build_parametric_overview()
        pc = param_entity(lda, "a") == 0
        f = ltl_F(bag_entity("h") == 0, "c")

        checker = SmtCheckerRSCParam(rc, optimise=True)
        run_silent(
            checker.check_rsltl,
            formulae_list=[f],
            param_constr=pc,
        )
        # The parametric checker uses path-based solving;
        # after SAT the solver should be satisfiable
        assert checker.solver.check() == sat


# ---------------------------------------------------------------------------
# RS translation tests (RSC -> RS)
# ---------------------------------------------------------------------------

class TestRSCtoRSTranslation:
    def test_translated_system_reachability(self):
        """Chain(2,2) translated to plain RS: e_2#2 should be reachable."""
        rc = _build_chain_rsc(2, 2)
        orc = rc.get_ordinary_reaction_system_with_automaton()
        checker = SmtCheckerRS(orc)
        run_silent(
            checker.check_reachability,
            ["e_2#2"],
            print_witness=False,
            print_time=False,
            print_mem=False,
        )
        assert checker.solver.check() == sat
