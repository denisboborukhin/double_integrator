import unittest

from double_integrator_pygame.solver import solve_problem6


class Problem6SolverTest(unittest.TestCase):
    def assert_reaches_origin(self, p0: float, v0: float, amax: float) -> None:
        solution = solve_problem6(p0, v0, amax)
        position, velocity, acceleration = solution.state_at(solution.tf)
        self.assertAlmostEqual(position, 0.0, places=8)
        self.assertAlmostEqual(velocity, 0.0, places=8)
        self.assertEqual(acceleration, 0.0)
        self.assertGreaterEqual(solution.t1, -1e-9)
        self.assertGreaterEqual(solution.t2, -1e-9)

    def test_generic_positive_b_uses_negative_first_arc(self) -> None:
        solution = solve_problem6(6.0, -2.0, 1.5)
        self.assertGreater(solution.b_value, 0.0)
        self.assertEqual(solution.first_sign, -1)
        self.assert_reaches_origin(6.0, -2.0, 1.5)

    def test_generic_negative_b_uses_positive_first_arc(self) -> None:
        solution = solve_problem6(-6.0, 2.0, 1.5)
        self.assertLess(solution.b_value, 0.0)
        self.assertEqual(solution.first_sign, 1)
        self.assert_reaches_origin(-6.0, 2.0, 1.5)

    def test_degenerate_braking_case(self) -> None:
        solution = solve_problem6(-2.0, 2.0, 1.0)
        self.assertTrue(solution.degenerate)
        self.assertEqual(solution.first_sign, -1)
        self.assertAlmostEqual(solution.tf, 2.0)
        self.assert_reaches_origin(-2.0, 2.0, 1.0)

    def test_origin_is_stationary(self) -> None:
        solution = solve_problem6(0.0, 0.0, 1.0)
        self.assertTrue(solution.degenerate)
        self.assertEqual(solution.tf, 0.0)
        self.assert_reaches_origin(0.0, 0.0, 1.0)


if __name__ == "__main__":
    unittest.main()
