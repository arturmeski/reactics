from logics.rsltl import *


def simplify(x):
    return x


class rsLTL_Encoder(object):
    """Class for encoding rsLTL formulae for a given smt_checker instance"""

    def __init__(self, smt_checker):
        self.smt_checker = smt_checker
        self.rs = smt_checker.rs

        self.v = None
        self.v_ctx = None
        self.loop_position = None

        # self.load_variables(
        #     var_rs=smt_checker.v,
        #     var_ctx=smt_checker.v_ctx,
        #     var_loop_pos=smt_checker.loop_position)

        self.init_ncalls()

    def load_variables(self, var_rs, var_ctx, var_loop_pos):

        self.v = var_rs
        self.v_ctx = var_ctx
        self.loop_position = var_loop_pos

    def get_encoding(self, formula, bound):

        assert self.v is not None
        assert self.v_ctx is not None
        assert self.loop_position is not None

        self.cache_init(bound)
        self.init_ncalls()

        return self.encode(formula, 0, bound)

    def init_ncalls(self):
        self.ncalls_encode = 0
        self.ncalls_encode_approx = 0

    def cache_init(self, bound):
        """
        Cache for formulae encodings
        """
        self.cache_hits = 0
        self.enc_fcache = [{} for level in range(0, bound+1)]
        self.enc_fcache_approx = [{} for level in range(0, bound+1)]

    def cache_save(self, formula, level, formula_encoding):
        self.enc_fcache[level][formula] = formula_encoding

    def cache_approx_save(self, formula, level, formula_encoding):
        self.enc_fcache_approx[level][formula] = formula_encoding

    def cache_query(self, formula, level):
        if formula in self.enc_fcache[level]:
            self.cache_hits += 1
            return self.enc_fcache[level][formula]
        else:
            return None

    def cache_query_approx(self, formula, level):
        if formula in self.enc_fcache_approx[level]:
            self.cache_hits += 1
            return self.enc_fcache_approx[level][formula]
        else:
            return None

    def get_cache_hits(self):
        return self.cache_hits

    def flush_cache(self):
        self.enc_fcache = None
        self.enc_fcache_approx = None

    def get_ncalls(self):
        return (self.ncalls_encode, self.ncalls_encode_approx)

    def encode_bag(self, bag_formula, level, context=False):

        if not bag_formula:
            raise RuntimeError("bag_formula is None")

        if bag_formula.f_type == BagDesc_oper.entity:
            entity_id = self.rs.get_entity_id(bag_formula.entity)
            if context:
                return self.v_ctx[level][entity_id]
            else:
                return self.v[level][entity_id]

        if bag_formula.f_type == BagDesc_oper.true:
            return True

        if bag_formula.f_type == BagDesc_oper.l_and:
            return And(
                self.encode_bag(bag_formula.left_operand, level, context),
                self.encode_bag(bag_formula.right_operand, level, context))

        if bag_formula.f_type == BagDesc_oper.l_or:
            return Or(
                self.encode_bag(bag_formula.left_operand, level, context),
                self.encode_bag(bag_formula.right_operand, level, context))

        if bag_formula.f_type == BagDesc_oper.l_not:
            return Not(self.encode_bag(
                bag_formula.left_operand, level, context))

        if bag_formula.f_type == BagDesc_oper.lt:
            return self.encode_bag(
                bag_formula.left_operand, level, context) < int(
                bag_formula.right_operand)

        if bag_formula.f_type == BagDesc_oper.le:
            return self.encode_bag(
                bag_formula.left_operand, level, context) <= int(
                bag_formula.right_operand)

        if bag_formula.f_type == BagDesc_oper.eq:
            return self.encode_bag(
                bag_formula.left_operand, level, context) == int(
                bag_formula.right_operand)

        if bag_formula.f_type == BagDesc_oper.ge:
            return self.encode_bag(
                bag_formula.left_operand, level, context) >= int(
                bag_formula.right_operand)

        if bag_formula.f_type == BagDesc_oper.gt:
            return self.encode_bag(
                bag_formula.left_operand, level, context) > int(
                bag_formula.right_operand)

        assert False, "Unsupported case {:s}".format(bag_formula.f_type)

    def encode_bag_state(self, bag_formula, level):
        res = self.encode_bag(bag_formula, level)
        assert res is not None
        return res

    def encode_bag_ctx(self, bag_formula, level):
        res = self.encode_bag(bag_formula, level, context=True)
        assert res is not None
        return res

    def encode(self, formula, level, bound):

        self.ncalls_encode += 1

        from_cache = self.cache_query(formula, level)
        if from_cache is not None:
            return from_cache

        enc = None

        if not isinstance(formula, Formula_rsLTL):
            raise NotImplementedError(
                "Unsupported formula type: " + str(type(formula)))

        if level > bound:
            raise RuntimeError(
                "level > bound. Unexpected behaviour. The encoding does not support levels higher than a bound.")

        if formula.f_type == rsLTL_form_type.bag:
            enc = self.encode_bag_state(formula.bag_descr, level)

        elif formula.f_type == rsLTL_form_type.l_not:
            subform = formula.left_operand
            if subform.is_bag:
                enc = Not(self.encode_bag_state(subform, level))
            else:
                raise RuntimeError("Negation can be applied to bags only")

        elif formula.f_type == rsLTL_form_type.l_and:
            enc = And(
                self.encode(formula.left_operand, level, bound),
                self.encode(formula.right_operand, level, bound)
            )

        elif formula.f_type == rsLTL_form_type.l_or:
            enc = Or(
                self.encode(formula.left_operand, level, bound),
                self.encode(formula.right_operand, level, bound)
            )

        elif formula.f_type == rsLTL_form_type.l_implies:
            enc = Implies(
                self.encode(formula.left_operand, level, bound),
                self.encode(formula.right_operand, level, bound)
            )

        elif formula.f_type == rsLTL_form_type.t_next:
            if level < bound:
                enc = And(
                    self.encode(formula.left_operand, level + 1, bound),
                    self.encode_bag_ctx(formula.sub_operand, level)
                )
            else:
                # level == bound
                enc = False
                for loop_level in range(1, bound+1):
                    enc = simplify(Or(enc, And(self.loop_position == loop_level, self.encode(
                        formula.left_operand, loop_level, bound))))
                enc = And(enc, self.encode_bag_ctx(formula.sub_operand, level))
                enc = simplify(enc)

        elif formula.f_type == rsLTL_form_type.t_globally:
            if level < bound:
                enc = And(
                    self.encode(formula.left_operand, level, bound),
                    self.encode_bag_ctx(formula.sub_operand, level),
                    self.encode(formula, level + 1, bound)
                )
            else:
                # level == bound
                enc_loops = False
                for loop_level in range(1, bound+1):
                    enc_loops = simplify(Or(enc_loops,
                                            And(
                                                self.loop_position == loop_level,
                                                self.encode_approx(formula, loop_level, bound),
                                            )
                                            ))
                enc = And(
                    self.encode(formula.left_operand, bound, bound),
                    enc_loops,
                    self.encode_bag_ctx(formula.sub_operand, level)
                )
                enc = simplify(enc)

        elif formula.f_type == rsLTL_form_type.t_finally:
            if level < bound:
                enc = Or(
                    self.encode(formula.left_operand, level, bound),
                    And(
                        self.encode_bag_ctx(formula.sub_operand, level),
                        self.encode(formula, level + 1, bound)
                    )
                )
            else:
                # level == bound
                enc_loops = False
                for loop_level in range(1, bound+1):
                    enc_loops = simplify(Or(enc_loops,
                                            And(
                                                self.loop_position == loop_level,
                                                self.encode_approx(formula, loop_level, bound),
                                            )
                                            ))
                    # print(enc)
                enc = Or(self.encode(formula.left_operand, bound, bound),
                         And(
                    enc_loops,
                    self.encode_bag_ctx(formula.sub_operand, level)
                )
                )

                enc = simplify(enc)

        elif formula.f_type == rsLTL_form_type.t_until:
            if level < bound:
                inner_enc = self.encode(formula, level + 1, bound)
            else:
                # level == bound
                inner_enc = False
                for loop_level in range(1, bound+1):
                    inner_enc = simplify(Or(inner_enc,
                                            And(
                                                self.loop_position == loop_level,
                                                self.encode_approx(formula, loop_level, bound)
                                            )
                                            ))

            enc = Or(
                self.encode(formula.right_operand, level, bound),
                And(
                    self.encode(formula.left_operand, level, bound),
                    inner_enc,
                    self.encode_bag_ctx(formula.sub_operand, level)
                )
            )

        elif formula.f_type == rsLTL_form_type.t_release:
            if level < bound:
                inner_enc = self.encode(formula, level + 1, bound)
            else:
                # level == bound
                inner_enc = False
                for loop_level in range(1, bound+1):
                    inner_enc = simplify(Or(inner_enc,
                                            And(
                                                self.loop_position == loop_level,
                                                self.encode_approx(formula, loop_level, bound)
                                            )
                                            ))

            enc = And(
                self.encode(formula.right_operand, level, bound),
                Or(
                    self.encode(formula.left_operand, level, bound),
                    And(
                        inner_enc,
                        self.encode_bag_ctx(formula.sub_operand, level)
                    )
                )
            )

        else:
            raise NotImplementedError("Unsupported operator")

        if enc is None:
            raise RuntimeError("Encoding is NONE. Should never happen")

        self.cache_save(formula, level, enc)

        return enc

    def encode_approx(self, formula, level, bound):
        """Provides the approximation-encoding

        Used by encode()
        """

        self.ncalls_encode_approx += 1

        enc = None

        from_cache = self.cache_query_approx(formula, level)
        if from_cache is not None:
            return from_cache

        if formula.f_type == rsLTL_form_type.t_until:
            if level < bound:
                enc = Or(
                    self.encode(formula.right_operand, level, bound),
                    And(
                        self.encode(formula.left_operand, level, bound),
                        self.encode_approx(formula, level + 1, bound),
                        self.encode_bag_ctx(formula.sub_operand, level)
                    )
                )
            else:
                # level == bound
                enc = self.encode(formula.right_operand, bound, bound)

        elif formula.f_type == rsLTL_form_type.t_release:
            if level < bound:
                enc = And(
                    self.encode(formula.right_operand, level, bound),
                    Or(
                        self.encode(formula.left_operand, level, bound),
                        And(
                            self.encode_approx(formula, level + 1, bound),
                            self.encode_bag_ctx(formula.sub_operand, level)
                        )
                    )
                )
            else:
                # level == bound
                enc = self.encode(formula.right_operand, bound, bound)

        elif formula.f_type == rsLTL_form_type.t_globally:
            if level < bound:
                enc = And(
                    self.encode(formula.left_operand, level, bound),
                    self.encode_bag_ctx(formula.sub_operand, level),
                    self.encode_approx(formula, level + 1, bound)
                )
            else:
                # level == bound
                enc = self.encode(formula.left_operand, bound, bound)

        elif formula.f_type == rsLTL_form_type.t_finally:
            if level < bound:
                enc = Or(
                    self.encode(formula.left_operand, level, bound),
                    And(
                        self.encode_bag_ctx(formula.sub_operand, level),
                        self.encode_approx(formula, level + 1, bound)
                    )
                )
            else:
                # level == bound
                enc = self.encode(formula.left_operand, bound, bound)

        else:
            raise NotImplementedError(
                "Unsupported operator in approximation encoding")

        if enc is None:
            raise RuntimeError("Encoding is NONE. Should never happen")

        self.cache_approx_save(formula, level, enc)

        return enc
