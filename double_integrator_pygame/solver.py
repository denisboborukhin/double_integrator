from __future__ import annotations

from dataclasses import dataclass
from math import isclose, sqrt


EPSILON = 1e-9


def sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


@dataclass(frozen=True)
class BangBangSolution:
    p0: float
    v0: float
    amax: float
    b_value: float
    first_sign: int
    t1: float
    t2: float
    tf: float
    degenerate: bool

    @property
    def first_acceleration(self) -> float:
        return self.first_sign * self.amax

    @property
    def second_acceleration(self) -> float:
        return -self.first_sign * self.amax

    def acceleration_at(self, time: float) -> float:
        if self.tf <= EPSILON or time >= self.tf:
            return 0.0
        if self.degenerate:
            return self.first_acceleration
        return self.first_acceleration if time < self.t1 else self.second_acceleration

    def state_at(self, time: float) -> tuple[float, float, float]:
        if self.tf <= EPSILON:
            return self.p0, self.v0, 0.0

        t = max(0.0, min(time, self.tf))

        if self.degenerate:
            a = self.first_acceleration
            position = self.p0 + self.v0 * t + 0.5 * a * t * t
            velocity = self.v0 + a * t
            if isclose(t, self.tf, abs_tol=EPSILON):
                return 0.0, 0.0, 0.0
            return position, velocity, a

        a1 = self.first_acceleration
        a2 = self.second_acceleration

        if t <= self.t1:
            position = self.p0 + self.v0 * t + 0.5 * a1 * t * t
            velocity = self.v0 + a1 * t
            return position, velocity, a1

        p_switch = self.p0 + self.v0 * self.t1 + 0.5 * a1 * self.t1 * self.t1
        v_switch = self.v0 + a1 * self.t1
        tau = t - self.t1
        position = p_switch + v_switch * tau + 0.5 * a2 * tau * tau
        velocity = v_switch + a2 * tau
        if isclose(t, self.tf, abs_tol=EPSILON):
            return 0.0, 0.0, 0.0
        return position, velocity, a2

    def samples(self, count: int = 180) -> list[tuple[float, float, float, float]]:
        if count <= 1:
            p, v, a = self.state_at(0.0)
            return [(0.0, p, v, a)]
        if self.tf <= EPSILON:
            p, v, a = self.state_at(0.0)
            return [(0.0, p, v, a) for _ in range(count)]
        return [
            (time, *self.state_at(time))
            for time in (self.tf * index / (count - 1) for index in range(count))
        ]


def solve_problem6(p0: float, v0: float, amax: float) -> BangBangSolution:
    if amax <= 0:
        raise ValueError("amax must be positive")

    b_value = 2.0 * amax * p0 + v0 * abs(v0)

    if abs(b_value) <= EPSILON:
        brake_sign = -sign(v0)
        tf = abs(v0) / amax
        return BangBangSolution(
            p0=p0,
            v0=v0,
            amax=amax,
            b_value=0.0,
            first_sign=brake_sign,
            t1=tf,
            t2=0.0,
            tf=tf,
            degenerate=True,
        )

    first_sign = -sign(b_value)
    radicand = (v0 * v0 - 2.0 * first_sign * amax * p0) / (2.0 * amax * amax)
    t2 = sqrt(max(0.0, radicand))
    t1 = t2 - first_sign * v0 / amax
    if t1 < 0 and t1 > -EPSILON:
        t1 = 0.0
    tf = t1 + t2

    return BangBangSolution(
        p0=p0,
        v0=v0,
        amax=amax,
        b_value=b_value,
        first_sign=first_sign,
        t1=t1,
        t2=t2,
        tf=tf,
        degenerate=False,
    )
