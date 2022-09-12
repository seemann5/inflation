import unittest
import numpy as np

from causalinflation.quantum.general_tools import (flatten,
                                           apply_source_permutation_coord_input)
from causalinflation import InflationProblem, InflationSDP
import warnings

class TestLPI(unittest.TestCase):
     def test_lpi_bounds(self):
         sdp = InflationSDP(
                   InflationProblem({"h1": ["a", "b"],
                                     "h2": ["b", "c"],
                                     "h3": ["a", "c"]},
                                     outcomes_per_party=[2, 2, 2],
                                     settings_per_party=[1, 1, 1],
                                     inflation_level_per_source=[3, 3, 3]),
                             commuting=False)
         cols = [np.array([]),
                 np.array([[1, 1, 0, 1, 0, 0]]),
                 np.array([[2, 2, 1, 0, 0, 0],
                           [2, 3, 1, 0, 0, 0]]),
                 np.array([[3, 0, 2, 2, 0, 0],
                           [3, 0, 3, 2, 0, 0]]),
                 np.array([[1, 1, 0, 1, 0, 0],
                           [2, 2, 1, 0, 0, 0],
                           [2, 3, 1, 0, 0, 0],
                           [3, 0, 2, 2, 0, 0],
                           [3, 0, 3, 2, 0, 0]])]
         sdp.generate_relaxation(cols)
         sdp.set_distribution(np.ones((2,2,2,1,1,1))/8,
                              use_lpi_constraints=True)

         self.assertTrue(np.all([abs(val[0]) <= 1.
                                 for val in sdp.semiknown_moments.values()]),
                     ("Semiknown moments need to be of the form " +
                     "mon_index1 = (number<=1) * mon_index2, this is failing."))


class TestMonomialGeneration(unittest.TestCase):
    bilocalDAG = {"h1": ["v1", "v2"], "h2": ["v2", "v3"]}
    inflation  = [2, 2]
    bilocality = InflationProblem(dag=bilocalDAG,
                                  settings_per_party=[1, 1, 1],
                                  outcomes_per_party=[2, 2, 2],
                                  inflation_level_per_source=inflation)
    bilocalSDP           = InflationSDP(bilocality)
    bilocalSDP_commuting = InflationSDP(bilocality, commuting=True)
    # Column structure for the NPA level 2 in a tripartite scenario
    col_structure = [[],
                     [0], [1], [2],
                     [0, 0], [0, 1], [0, 2], [1, 1], [1, 2], [2, 2]]
    # Monomials for the NPA level 2 in the bilocality scenario
    meas = bilocalSDP.measurements
    A_1_0_0_0 = meas[0][0][0][0]
    A_2_0_0_0 = meas[0][1][0][0]
    B_1_1_0_0 = meas[1][0][0][0]
    B_1_2_0_0 = meas[1][1][0][0]
    B_2_1_0_0 = meas[1][2][0][0]
    B_2_2_0_0 = meas[1][3][0][0]
    C_0_1_0_0 = meas[2][0][0][0]
    C_0_2_0_0 = meas[2][1][0][0]
    actual_cols = [1, A_1_0_0_0, A_2_0_0_0, B_1_1_0_0, B_1_2_0_0, B_2_1_0_0,
                   B_2_2_0_0, C_0_1_0_0, C_0_2_0_0, A_1_0_0_0*A_2_0_0_0,
                   A_1_0_0_0*B_1_1_0_0, A_1_0_0_0*B_1_2_0_0,
                   A_1_0_0_0*B_2_1_0_0, A_1_0_0_0*B_2_2_0_0,
                   A_2_0_0_0*B_1_1_0_0, A_2_0_0_0*B_1_2_0_0,
                   A_2_0_0_0*B_2_1_0_0, A_2_0_0_0*B_2_2_0_0,
                   A_1_0_0_0*C_0_1_0_0, A_1_0_0_0*C_0_2_0_0,
                   A_2_0_0_0*C_0_1_0_0, A_2_0_0_0*C_0_2_0_0,
                   B_1_1_0_0*B_1_2_0_0, B_1_1_0_0*B_2_1_0_0,
                   B_1_1_0_0*B_2_2_0_0, B_1_2_0_0*B_1_1_0_0,
                   B_1_2_0_0*B_2_1_0_0, B_1_2_0_0*B_2_2_0_0,
                   B_2_1_0_0*B_1_1_0_0, B_2_1_0_0*B_2_2_0_0,
                   B_2_2_0_0*B_1_2_0_0, B_2_2_0_0*B_2_1_0_0,
                   B_1_1_0_0*C_0_1_0_0, B_1_1_0_0*C_0_2_0_0,
                   B_1_2_0_0*C_0_1_0_0, B_1_2_0_0*C_0_2_0_0,
                   B_2_1_0_0*C_0_1_0_0, B_2_1_0_0*C_0_2_0_0,
                   B_2_2_0_0*C_0_1_0_0, B_2_2_0_0*C_0_2_0_0,
                   C_0_1_0_0*C_0_2_0_0]

    def test_generating_columns_c(self):
       truth = 37
       columns = self.bilocalSDP_commuting.build_columns(self.col_structure,
                                                return_columns_numerical=False)
       self.assertEqual(len(columns), truth,
                        "With commuting variables, there are  " +
                        str(len(columns)) + " columns but " + str(truth) +
                        " were expected.")

    def test_generating_columns_nc(self):
        truth = 41
        columns = self.bilocalSDP.build_columns(self.col_structure,
                                                return_columns_numerical=False)
        self.assertEqual(len(columns), truth,
                         "With noncommuting variables, there are  " +
                         str(len(columns)) + " columns but " + str(truth) +
                         " were expected.")

    def test_generation_from_columns(self):
        columns = self.bilocalSDP.build_columns(self.actual_cols,
                                                return_columns_numerical=False)
        self.assertEqual(columns, self.actual_cols,
                         "The direct copying of columns is failing.")

    def test_generation_from_lol(self):
        columns = self.bilocalSDP.build_columns(self.col_structure,
                                                return_columns_numerical=False)
        self.assertEqual(columns, self.actual_cols,
                         "Parsing a list-of-list description of columns fails.")

    def test_generation_from_str(self):
        columns = self.bilocalSDP.build_columns('npa2',
                                                return_columns_numerical=False)
        self.assertEqual(columns, self.actual_cols,
                        "Parsing the string description of columns is failing.")

    def test_generate_with_identities(self):
        oneParty = InflationSDP(InflationProblem({"h": ["v"]}, [2], [2], [1]))
        _, columns = oneParty.build_columns([[], [0, 0]],
                                            return_columns_numerical=True)
        truth   = [[],
                   [[1, 1, 0, 0], [1, 1, 1, 0]],
                   [[1, 1, 1, 0], [1, 1, 0, 0]]]
        truth = [np.array(mon) for mon in truth]
        self.assertTrue(len(columns) == len(truth),
                        "Generating columns with identities is not producing " +
                        "the correct number of columns.")
        areequal = all(np.array_equiv(r[0].T, np.array(r[1]).T) for r in zip(columns, truth))
        self.assertTrue(areequal,
                         "The column generation is not capable of handling " +
                         "monomials that reduce to the identity")
        self.assertTrue(areequal,
                        "The column generation is not capable of handling " +
                        "monomials that reduce to the identity.")


class TestSDPOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        warnings.simplefilter("ignore", category=DeprecationWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    def GHZ(self, v):
        dist = np.zeros((2,2,2,1,1,1))
        for a in [0, 1]:
            for b in [0, 1]:
                for c in [0, 1]:
                    if (a == b) and (b == c):
                        dist[a,b,c,0,0,0] = v/2 + (1-v)/8
                    else:
                        dist[a,b,c,0,0,0] = (1-v)/8
        return dist

    cutInflation = InflationProblem({"lambda": ["a", "b"],
                                     "mu": ["b", "c"],
                                     "sigma": ["a", "c"]},
                                     outcomes_per_party=[2, 2, 2],
                                     settings_per_party=[1, 1, 1],
                                     inflation_level_per_source=[2, 1, 1])

    def test_CHSH(self):
        bellScenario = InflationProblem({"Lambda": ["A", "B"]},
                                         outcomes_per_party=[2, 2],
                                         settings_per_party=[2, 2],
                                         inflation_level_per_source=[1])
        sdp = InflationSDP(bellScenario)
        sdp.generate_relaxation('npa1')
        self.assertEqual(len(sdp.generating_monomials), 5,
                         "The number of generating columns is not correct.")
        self.assertEqual(sdp.n_knowable, 8 + 1,  # only '1' is included here. No orthogonal moments in CG notation with one outcome.
                         "The count of knowable moments is wrong.")
        self.assertEqual(sdp.n_unknowable, 2,
                         "The count of unknowable moments is wrong.")
        meas = sdp.measurements
        A0 = 2*meas[0][0][0][0] - 1
        A1 = 2*meas[0][0][1][0] - 1
        B0 = 2*meas[1][0][0][0] - 1
        B1 = 2*meas[1][0][1][0] - 1

        sdp.set_objective(A0*(B0+B1)+A1*(B0-B1), 'max')
        self.assertEqual(len(sdp.objective), 7,
                         "The parsing of the objective function is failing")
        sdp.solve()
        self.assertTrue(np.isclose(sdp.objective_value, 2*np.sqrt(2)),
                        "The SDP is not recovering max(CHSH) = 2*sqrt(2)")
        bias = 3/4
        biased_chsh = 2.62132    # Value obtained by other means (ncpol2sdpa)
        sdp.set_values({meas[0][0][0][0]: bias,    # Variable for p(a=0|x=0)
                        'A_1_1_0': bias,           # Variable for p(a=0|x=1)
                        meas[1][0][0][0]: bias,    # Variable for p(b=0|y=0)
                        'B_1_1_0': bias            # Variable for p(b=0|y=1)
                        })
        sdp.solve()
        self.assertTrue(np.isclose(sdp.objective_value, biased_chsh),
                        f"The SDP is not recovering max(CHSH) = {biased_chsh} "
                        + "when the single-party marginals are biased towards "
                        + str(bias))
        bias = 1/4
        biased_chsh = 2.55890
        sdp.set_values({meas[0][0][0][0]: bias,    # Variable for p(a=0|x=0)
                        'A_1_1_0': bias,           # Variable for p(a=0|x=1)
                        meas[1][0][0][0]: bias,    # Variable for p(b=0|y=0)
                        'B_1_1_0': bias            # Variable for p(b=0|y=1)
                        })
        sdp.solve()
        self.assertTrue(np.isclose(sdp.objective_value, biased_chsh),
                        f"The SDP is not re-setting the objective correctly "
                        + "after re-setting known values.")

    def test_GHZ_commuting(self):
        sdp = InflationSDP(self.cutInflation, commuting=True)
        sdp.generate_relaxation('local1')
        self.assertEqual(len(sdp.generating_monomials), 18,
                         "The number of generating columns is not correct.")
        self.assertEqual(sdp.n_knowable, 8 + 1,  # only '1' is included here. No orthogonal moments in CG notation with one outcome.
                         "The count of knowable moments is wrong.")
        self.assertEqual(sdp.n_unknowable, 11,
                         "The count of unknowable moments is wrong.")

        sdp.set_distribution(self.GHZ(0.5 + 1e-2))
        sdp.solve()
        self.assertEqual(sdp.status, 'infeasible',
             "The commuting SDP is not identifying incompatible distributions.")
        sdp.solve(feas_as_optim=True)
        self.assertTrue(sdp.primal_objective <= 0,
                        "The commuting SDP with feasibility as optimization " +
                        "is not identifying incompatible distributions.")
        sdp.set_distribution(self.GHZ(0.5 - 1e-2))
        sdp.solve()
        self.assertEqual(sdp.status, 'feasible',
               "The commuting SDP is not recognizing compatible distributions.")
        sdp.solve(feas_as_optim=True)
        self.assertTrue(sdp.primal_objective >= 0,
                        "The commuting SDP with feasibility as optimization " +
                        "is not recognizing compatible distributions.")

    def test_GHZ_NC(self):
        sdp = InflationSDP(self.cutInflation)
        sdp.generate_relaxation('local1')
        self.assertEqual(len(sdp.generating_monomials), 18,
                         "The number of generating columns is not correct.")
        self.assertEqual(sdp.n_knowable, 8 + 1,  # only '1' is included here. No orthogonal moments in CG notation with one outcome.
                         "The count of knowable moments is wrong.")
        self.assertEqual(sdp.n_unknowable, 13,
                         "The count of unknowable moments is wrong.")

        sdp.set_distribution(self.GHZ(0.5 + 1e-2))
        self.assertTrue(np.isclose(sdp.known_moments[sdp.list_of_monomials[8]],
                        (0.5+1e-2)/2 + (0.5-1e-2)/8),
                        "Setting the distribution is failing.")
        sdp.solve()
        self.assertTrue(sdp.status in ['infeasible', 'unknown'],
                    "The NC SDP is not identifying incompatible distributions.")
        sdp.solve(feas_as_optim=True)
        self.assertTrue(sdp.primal_objective <= 0,
                        "The NC SDP with feasibility as optimization is not " +
                        "identifying incompatible distributions.")
        sdp.set_distribution(self.GHZ(0.5 - 1e-2))
        self.assertTrue(np.isclose(sdp.known_moments[sdp.list_of_monomials[8]],
                         (0.5-1e-2)/2 + (0.5+1e-2)/8),
                         "Re-setting the distribution is failing.")
        sdp.solve()
        self.assertEqual(sdp.status, 'feasible',
                      "The NC SDP is not recognizing compatible distributions.")
        sdp.solve(feas_as_optim=True)
        self.assertTrue(sdp.primal_objective >= 0,
                        "The NC SDP with feasibility as optimization is not " +
                        "recognizing compatible distributions.")

    def test_lpi(self):
        sdp = InflationSDP(
                  InflationProblem({"h": ["a"]},
                                    outcomes_per_party=[2],
                                    settings_per_party=[2],
                                    inflation_level_per_source=[2])
                            )
        [[[[A10], [A11]], [[A20], [A21]]]] = sdp.measurements
        sdp.generate_relaxation([1,
                                 A10, A11, A20, A21,
                                 A10*A11, A10*A21, A11*A20, A20*A21])
        sdp.set_distribution(np.array([[0.14873, 0.85168]]))
        # sdp.set_objective(A10*A11*A20*A21) # This produces an error
        sdp.set_objective(A11*A10*A20*A21)
        sdp.solve()
        self.assertTrue(np.isclose(sdp.objective_value, 0.0918999),
                        "Optimization of a simple SDP without LPI-like " +
                        "constraints is not obtaining the correct known value.")
        sdp.set_distribution(np.array([[0.14873, 0.85168]]),
            use_lpi_constraints=True
            )
        sdp.solve()
        self.assertTrue(np.isclose(sdp.objective_value, 0.0640776),
                        "Optimization of a simple SDP with LPI-like " +
                        "constraints is not obtaining the correct known value.")


class TestSymmetries(unittest.TestCase):
    def test_commutations_after_symmetrization(self):
        scenario = InflationSDP(InflationProblem(dag={"h": ["v"]},
                                                 outcomes_per_party=[2],
                                                 settings_per_party=[2],
                                                 inflation_level_per_source=[2]
                                                 ),
                                commuting=True)
        lexorder = scenario._lexorder
        notcomm = scenario._notcomm
        scenario._generate_parties()
        col_structure = [[], [0, 0]]

        _, ordered_cols_num = scenario.build_columns(col_structure,
                                                  return_columns_numerical=True)

        expected = [[],
                    [[1, 2, 0, 0], [1, 2, 1, 0]],
                    [[1, 1, 0, 0], [1, 2, 0, 0]],
                    [[1, 1, 1, 0], [1, 2, 0, 0]],
                    [[1, 1, 0, 0], [1, 2, 1, 0]],
                    [[1, 1, 1, 0], [1, 2, 1, 0]],
                    [[1, 1, 0, 0], [1, 1, 1, 0]]]

        permuted_cols = apply_source_permutation_coord_input(ordered_cols_num,
                                                             0,
                                                             (1, 0),
                                                             False,
                                                             notcomm,
                                                             lexorder
                                                             )
        self.assertTrue(np.array_equal(np.array(expected[5]), permuted_cols[5]),
                         "The commuting relations of different copies are not "
                         + "being applied properly after inflation symmetries.")
