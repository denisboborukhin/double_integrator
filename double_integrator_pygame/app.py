from __future__ import annotations

import sys
from dataclasses import dataclass

import pygame

from double_integrator_pygame.solver import BangBangSolution, solve_problem6


WIDTH = 1180
HEIGHT = 760
FPS = 60
BG_TOP = (242, 247, 251)
BG_BOTTOM = (232, 238, 244)
INK = (17, 24, 39)
MUTED = (91, 103, 120)
FAINT = (226, 232, 240)
GRID = (211, 220, 230)
BLUE = (39, 104, 194)
BLUE_DARK = (24, 73, 145)
RED = (204, 49, 63)
GREEN = (26, 150, 96)
ORANGE = (226, 116, 45)
PURPLE = (115, 91, 184)
PANEL = (255, 255, 255)
PLOT_BG = (249, 251, 253)
SHADOW = (197, 207, 219)


@dataclass
class Parameter:
    name: str
    value: float
    step: float
    minimum: float
    maximum: float

    def adjust(self, direction: int) -> None:
        self.value = min(self.maximum, max(self.minimum, self.value + direction * self.step))


class Problem6App:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Problem 6: Bang-Bang Transfer to Origin")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 15)
        self.tiny_font = pygame.font.SysFont("Arial", 13)
        self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.panel_font = pygame.font.SysFont("Arial", 19, bold=True)
        self.params = {
            "p0": Parameter("p0", 0.0, 0.5, -10.0, 10.0),
            "v0": Parameter("v0", 4.0, 0.5, -8.0, 8.0),
            "amax": Parameter("amax", 1.5, 0.25, 0.25, 5.0),
        }
        self.playing = True
        self.elapsed = 0.0
        self.speed = 1.0
        self.solution = self.recompute()

    def recompute(self) -> BangBangSolution:
        solution = solve_problem6(
            self.params["p0"].value,
            self.params["v0"].value,
            self.params["amax"].value,
        )
        self.elapsed = 0.0
        return solution

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            if self.playing and self.solution.tf > 0:
                self.elapsed += dt * self.speed
                if self.elapsed > self.solution.tf:
                    self.elapsed = self.solution.tf
                    self.playing = False
            self.draw()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                self.handle_key(event.key)

    def handle_key(self, key: int) -> None:
        changed = False
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit(0)
        if key == pygame.K_SPACE:
            self.playing = not self.playing
        elif key == pygame.K_r:
            self.elapsed = 0.0
            self.playing = True
        elif key in (pygame.K_q, pygame.K_a):
            self.params["p0"].adjust(1 if key == pygame.K_q else -1)
            changed = True
        elif key in (pygame.K_w, pygame.K_s):
            self.params["v0"].adjust(1 if key == pygame.K_w else -1)
            changed = True
        elif key in (pygame.K_e, pygame.K_d):
            self.params["amax"].adjust(1 if key == pygame.K_e else -1)
            changed = True
        elif key == pygame.K_RIGHT:
            self.speed = min(4.0, self.speed + 0.25)
        elif key == pygame.K_LEFT:
            self.speed = max(0.25, self.speed - 0.25)

        if changed:
            self.solution = self.recompute()
            self.playing = True

    def draw(self) -> None:
        self.draw_background()
        self.draw_header()
        self.draw_motion_panel(pygame.Rect(30, 95, 740, 255))
        self.draw_phase_panel(pygame.Rect(30, 380, 520, 330))
        self.draw_time_panel(pygame.Rect(580, 380, 560, 330))
        self.draw_side_panel(pygame.Rect(800, 95, 340, 255))
        pygame.display.flip()

    def draw_header(self) -> None:
        title = self.title_font.render("Problem 6: arbitrary (p0, v0) to the origin", True, INK)
        self.screen.blit(title, (30, 24))
        subtitle = self.font.render("Bang-bang acceleration, with B = 2*a_bar*p0 + v0*|v0| choosing the first arc.", True, MUTED)
        self.screen.blit(subtitle, (30, 58))
        state_text = "PLAYING" if self.playing else "PAUSED"
        self.draw_pill(pygame.Rect(WIDTH - 150, 27, 110, 30), state_text, GREEN if self.playing else ORANGE)

    def draw_side_panel(self, rect: pygame.Rect) -> None:
        self.draw_panel(rect)
        solution = self.solution
        self.label(rect, "Controls and solution")
        y = rect.y + 52
        controls = [
            ("Q / A", "p0"),
            ("W / S", "v0"),
            ("E / D", "a_bar"),
            ("Space", "play or pause"),
            ("R", "restart"),
            ("Left / Right", "speed"),
        ]
        for key, action in controls:
            key_rect = pygame.Rect(rect.x + 18, y, 88, 24)
            pygame.draw.rect(self.screen, (241, 245, 249), key_rect, border_radius=6)
            pygame.draw.rect(self.screen, FAINT, key_rect, 1, border_radius=6)
            self.screen.blit(self.tiny_font.render(key, True, INK), (key_rect.x + 9, key_rect.y + 5))
            self.screen.blit(self.small_font.render(action, True, MUTED), (rect.x + 118, y + 4))
            y += 28

        y += 6
        self.draw_metric(rect.x + 18, y, "p0", f"{solution.p0:.2f}", BLUE)
        self.draw_metric(rect.x + 124, y, "v0", f"{solution.v0:.2f}", ORANGE)
        self.draw_metric(rect.x + 230, y, "a_bar", f"{solution.amax:.2f}", GREEN)

        y += 62
        b_color = GREEN if abs(solution.b_value) <= 1e-9 else ORANGE
        case_label = "B = 0 braking" if solution.degenerate else "B != 0 switch"
        self.draw_pill(pygame.Rect(rect.x + 18, y, 136, 28), f"B {solution.b_value:.2f}", b_color)
        self.draw_pill(pygame.Rect(rect.x + 164, y, 146, 28), case_label, PURPLE)

        y += 44
        accel_color = RED if solution.first_acceleration < 0 else GREEN
        lines = [
            f"first acceleration: {solution.first_acceleration:.2f}",
            f"t1 = {solution.t1:.3f}   t2 = {solution.t2:.3f}",
            f"tf = {solution.tf:.3f}   speed = {self.speed:.2f}x",
        ]
        for index, text in enumerate(lines):
            color = accel_color if index == 0 else INK
            self.screen.blit(self.small_font.render(text, True, color), (rect.x + 20, y))
            y += 23

    def draw_motion_panel(self, rect: pygame.Rect) -> None:
        self.draw_panel(rect)
        self.label(rect, "Position animation")
        solution = self.solution
        samples = solution.samples(240)
        positions = [sample[1] for sample in samples] + [0.0, solution.p0]
        span = max(2.0, max(abs(value) for value in positions) * 1.25)
        axis_y = rect.y + 142
        left = rect.x + 55
        right = rect.right - 45
        plot_rect = pygame.Rect(left, rect.y + 72, right - left, 118)

        track = pygame.Rect(left, axis_y - 9, right - left, 18)
        pygame.draw.rect(self.screen, (231, 237, 244), track, border_radius=9)
        pygame.draw.line(self.screen, GRID, (left, axis_y), (right, axis_y), 2)
        origin_x = self.map_x(0.0, -span, span, left, right)
        pygame.draw.line(self.screen, INK, (origin_x, plot_rect.top), (origin_x, plot_rect.bottom), 2)
        self.draw_motion_badge(rect.x + 24, rect.y + 47, "origin", INK)

        path = [(self.map_x(p, -span, span, left, right), axis_y) for _, p, _, _ in samples]
        if len(path) > 1:
            pygame.draw.lines(self.screen, BLUE_DARK, False, path, 8)
            pygame.draw.lines(self.screen, BLUE, False, path, 4)

        if not solution.degenerate and solution.t1 > 0:
            p_switch, _, _ = solution.state_at(solution.t1)
            switch_x = self.map_x(p_switch, -span, span, left, right)
            pygame.draw.line(self.screen, PURPLE, (switch_x, plot_rect.top), (switch_x, plot_rect.bottom), 2)
            self.draw_motion_badge(rect.x + 102, rect.y + 47, "switch", PURPLE)

        position, velocity, acceleration = solution.state_at(self.elapsed)
        body_x = self.map_x(position, -span, span, left, right)
        color = RED if acceleration < 0 else GREEN if acceleration > 0 else MUTED
        pygame.draw.circle(self.screen, (255, 255, 255), (body_x, axis_y), 22)
        pygame.draw.circle(self.screen, color, (body_x, axis_y), 16)
        pygame.draw.circle(self.screen, INK, (body_x, axis_y), 16, 2)

        arrow_len = max(-70, min(70, velocity * 14))
        if abs(arrow_len) > 2:
            pygame.draw.line(self.screen, ORANGE, (body_x, axis_y - 38), (body_x + arrow_len, axis_y - 38), 4)
            direction = self.sign_or_one(arrow_len)
            pygame.draw.polygon(
                self.screen,
                ORANGE,
                [(body_x + arrow_len, axis_y - 38), (body_x + arrow_len - 8 * direction, axis_y - 44), (body_x + arrow_len - 8 * direction, axis_y - 32)],
            )

        status = f"t = {self.elapsed:.2f} / {solution.tf:.2f}    p = {position:.3f}    v = {velocity:.3f}    a = {acceleration:.2f}"
        status_rect = pygame.Rect(rect.x + 18, rect.bottom - 52, rect.width - 36, 34)
        pygame.draw.rect(self.screen, (247, 250, 252), status_rect, border_radius=7)
        self.screen.blit(self.font.render(status, True, INK), (status_rect.x + 10, status_rect.y + 7))
        self.draw_progress_bar(pygame.Rect(rect.x + 24, rect.bottom - 18, rect.width - 48, 7), self.elapsed, max(solution.tf, 1e-9))

    def draw_phase_panel(self, rect: pygame.Rect) -> None:
        self.draw_panel(rect)
        self.label(rect, "Phase plane (p, v)")
        solution = self.solution
        samples = solution.samples(260)
        ps = [sample[1] for sample in samples] + [0.0, solution.p0]
        vs = [sample[2] for sample in samples] + [0.0, solution.v0]
        p_span = max(2.0, max(abs(value) for value in ps) * 1.25)
        v_span = max(2.0, max(abs(value) for value in vs) * 1.25)
        plot = rect.inflate(-70, -76)
        self.draw_axes(plot, -p_span, p_span, -v_span, v_span, "", "")
        points = [self.map_point(p, v, -p_span, p_span, -v_span, v_span, plot) for _, p, v, _ in samples]
        if len(points) > 1:
            pygame.draw.lines(self.screen, BLUE_DARK, False, points, 5)
            pygame.draw.lines(self.screen, BLUE, False, points, 3)
        if not solution.degenerate and solution.t1 > 0:
            p_switch, v_switch, _ = solution.state_at(solution.t1)
            switch_point = self.map_point(p_switch, v_switch, -p_span, p_span, -v_span, v_span, plot)
            pygame.draw.circle(self.screen, PURPLE, switch_point, 6)
        p, v, _ = solution.state_at(self.elapsed)
        current = self.map_point(p, v, -p_span, p_span, -v_span, v_span, plot)
        target = self.map_point(0.0, 0.0, -p_span, p_span, -v_span, v_span, plot)
        pygame.draw.circle(self.screen, (255, 255, 255), current, 11)
        pygame.draw.circle(self.screen, RED, current, 7)
        pygame.draw.circle(self.screen, GREEN, target, 7)

    def draw_time_panel(self, rect: pygame.Rect) -> None:
        self.draw_panel(rect)
        self.label(rect, "Time histories")
        solution = self.solution
        samples = solution.samples(300)
        plot = rect.inflate(-70, -76)
        values = [sample[1] for sample in samples] + [sample[2] for sample in samples] + [solution.amax, -solution.amax]
        y_span = max(1.0, max(abs(value) for value in values) * 1.18)
        self.draw_axes(plot, 0.0, max(solution.tf, 1.0), -y_span, y_span, "", "")

        for index, color in ((1, BLUE), (2, ORANGE), (3, GREEN)):
            points = [
                self.map_point(sample[0], sample[index], 0.0, max(solution.tf, 1.0), -y_span, y_span, plot)
                for sample in samples
            ]
            if len(points) > 1:
                pygame.draw.lines(self.screen, color, False, points, 3)

        cursor_x = self.map_x(self.elapsed, 0.0, max(solution.tf, 1.0), plot.left, plot.right)
        pygame.draw.line(self.screen, RED, (cursor_x, plot.top), (cursor_x, plot.bottom), 2)
        if not solution.degenerate and solution.t1 > 0:
            switch_x = self.map_x(solution.t1, 0.0, max(solution.tf, 1.0), plot.left, plot.right)
            pygame.draw.line(self.screen, PURPLE, (switch_x, plot.top), (switch_x, plot.bottom), 2)
        self.draw_legend(rect.x + 24, rect.bottom - 36)

    def draw_background(self) -> None:
        for y in range(HEIGHT):
            blend = y / max(1, HEIGHT - 1)
            color = tuple(int(BG_TOP[i] * (1.0 - blend) + BG_BOTTOM[i] * blend) for i in range(3))
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

    def draw_panel(self, rect: pygame.Rect) -> None:
        shadow_rect = rect.move(0, 3)
        pygame.draw.rect(self.screen, SHADOW, shadow_rect, border_radius=8)
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=8)
        pygame.draw.rect(self.screen, FAINT, rect, width=1, border_radius=8)

    def label(self, rect: pygame.Rect, text: str) -> None:
        self.screen.blit(self.panel_font.render(text, True, INK), (rect.x + 18, rect.y + 14))

    def draw_axes(self, rect: pygame.Rect, xmin: float, xmax: float, ymin: float, ymax: float, xlabel: str, ylabel: str) -> None:
        pygame.draw.rect(self.screen, PLOT_BG, rect, border_radius=6)
        for fraction in (0.25, 0.5, 0.75):
            x = int(rect.left + rect.width * fraction)
            y = int(rect.top + rect.height * fraction)
            pygame.draw.line(self.screen, (235, 240, 246), (x, rect.top), (x, rect.bottom), 1)
            pygame.draw.line(self.screen, (235, 240, 246), (rect.left, y), (rect.right, y), 1)
        pygame.draw.rect(self.screen, GRID, rect, 1)
        zero_x = self.map_x(0.0, xmin, xmax, rect.left, rect.right)
        zero_y = self.map_y(0.0, ymin, ymax, rect.top, rect.bottom)
        pygame.draw.line(self.screen, (157, 170, 185), (rect.left, zero_y), (rect.right, zero_y), 1)
        pygame.draw.line(self.screen, (157, 170, 185), (zero_x, rect.top), (zero_x, rect.bottom), 1)
        if xlabel:
            self.screen.blit(self.small_font.render(xlabel, True, MUTED), (rect.right - 16, zero_y + 5))
        if ylabel:
            self.screen.blit(self.small_font.render(ylabel, True, MUTED), (zero_x + 5, rect.top + 4))

    def draw_metric(self, x: int, y: int, label: str, value: str, color: tuple[int, int, int]) -> None:
        rect = pygame.Rect(x, y, 88, 50)
        pygame.draw.rect(self.screen, (247, 250, 252), rect, border_radius=8)
        pygame.draw.rect(self.screen, color, (rect.x, rect.y, 5, rect.height), border_radius=3)
        self.screen.blit(self.tiny_font.render(label, True, MUTED), (x + 14, y + 7))
        self.screen.blit(self.font.render(value, True, INK), (x + 14, y + 24))

    def draw_pill(self, rect: pygame.Rect, text: str, color: tuple[int, int, int]) -> None:
        pygame.draw.rect(self.screen, color, rect, border_radius=rect.height // 2)
        label = self.tiny_font.render(text, True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_motion_badge(self, x: int, y: int, text: str, color: tuple[int, int, int]) -> None:
        pygame.draw.circle(self.screen, color, (x + 7, y + 10), 5)
        label = self.small_font.render(text, True, INK)
        self.screen.blit(label, (x + 18, y + 1))

    def draw_progress_bar(self, rect: pygame.Rect, value: float, maximum: float) -> None:
        pygame.draw.rect(self.screen, FAINT, rect, border_radius=rect.height // 2)
        width = int(rect.width * max(0.0, min(1.0, value / maximum)))
        if width > 0:
            pygame.draw.rect(self.screen, BLUE, pygame.Rect(rect.x, rect.y, width, rect.height), border_radius=rect.height // 2)

    def draw_legend(self, x: int, y: int) -> None:
        items = (("p(t)", BLUE), ("v(t)", ORANGE), ("a(t)", GREEN), ("switch", PURPLE))
        cursor = x
        for label, color in items:
            pygame.draw.circle(self.screen, color, (cursor + 6, y + 8), 5)
            self.screen.blit(self.small_font.render(label, True, INK), (cursor + 17, y))
            cursor += 92

    def map_point(self, x: float, y: float, xmin: float, xmax: float, ymin: float, ymax: float, rect: pygame.Rect) -> tuple[int, int]:
        return (
            self.map_x(x, xmin, xmax, rect.left, rect.right),
            self.map_y(y, ymin, ymax, rect.top, rect.bottom),
        )

    @staticmethod
    def map_x(value: float, minimum: float, maximum: float, left: int, right: int) -> int:
        if maximum <= minimum:
            return left
        return int(left + (value - minimum) * (right - left) / (maximum - minimum))

    @staticmethod
    def map_y(value: float, minimum: float, maximum: float, top: int, bottom: int) -> int:
        if maximum <= minimum:
            return bottom
        return int(bottom - (value - minimum) * (bottom - top) / (maximum - minimum))

    @staticmethod
    def sign_or_one(value: float) -> int:
        return -1 if value < 0 else 1


def main() -> None:
    Problem6App().run()


if __name__ == "__main__":
    main()
