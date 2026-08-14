"""
Battery Safety Systems: Preventing and Containing Thermal Runaway
--------------------------------------------------------------------
Moderate-detail explainer for a general (non-technical) audience.
Shows: a module of cells, a single-cell fault, thermal barriers
stopping it spreading, active cooling, and detection + suppression.
No title card - opens directly on the module.

Consistent color coding with the lithium_ion_battery.py scene:
    Anode = blue, Cathode = red, Ions = yellow
Here, cell "temperature" state uses a blue -> orange -> red ramp,
and containment/safety systems use green/teal.

Text uses Tex() (LaTeX rendering) for the classic Manim look, so
a LaTeX distribution (e.g. MacTeX, TeX Live, MiKTeX) must be
installed alongside Manim.

Run with:
    manim -pql battery_safety_systems.py BatterySafetySystems
(swap -pql for -pqh for high quality render)
"""

from manim import *

NORMAL_COLOR = BLUE_D
WARM_COLOR = ORANGE
HOT_COLOR = RED_D
SAFE_COLOR = GREEN
COOLANT_COLOR = TEAL
BARRIER_COLOR = GREY_B


class BatterySafetySystems(Scene):
    def construct(self):
        cells = self.build_module()
        self.show_fault(cells)
        self.show_barrier_containment(cells)
        self.show_cooling(cells)
        self.show_detection_suppression(cells)
        self.wrap_up(cells)

    # ------------------------------------------------------------------
    def build_module(self):
        """Row of 5 cells with visible gaps = thermal barriers between them."""
        n = 5
        cell_w, cell_h, gap = 1.0, 2.2, 0.35
        total_w = n * cell_w + (n - 1) * gap
        start_x = -total_w / 2 + cell_w / 2

        cells = VGroup()
        barriers = VGroup()
        for i in range(n):
            cell = Rectangle(width=cell_w, height=cell_h, color=NORMAL_COLOR,
                             fill_color=NORMAL_COLOR, fill_opacity=0.35)
            cell.move_to(RIGHT * (start_x + i * (cell_w + gap)))
            cells.add(cell)
            if i < n - 1:
                barrier = Rectangle(width=gap*0.6, height=cell_h*1.05,
                                    color=BARRIER_COLOR, fill_color=BARRIER_COLOR,
                                    fill_opacity=0.6, stroke_width=0)
                barrier.move_to(cell.get_center() + RIGHT * (cell_w/2 + gap/2))
                barriers.add(barrier)

        label = Tex("One battery module (thermal barriers in grey)",
                    font_size=20, color=GREY_A)
        label.next_to(cells, DOWN, buff=0.5)

        self.play(*[Create(c) for c in cells])
        self.play(*[FadeIn(b) for b in barriers])
        self.play(FadeIn(label))
        self.wait(0.5)
        self.play(FadeOut(label))

        return {"cells": cells, "barriers": barriers, "n": n}

    # ------------------------------------------------------------------
    def show_fault(self, cells):
        caption = Tex("A single cell develops an internal fault",
                      font_size=26, color=WARM_COLOR)
        caption.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(caption))

        fault_cell = cells["cells"][2]  # middle cell

        thermometer = VGroup(
            Line(UP*0.6, DOWN*0.6, color=WHITE, stroke_width=3),
            Circle(radius=0.15, color=RED, fill_color=RED, fill_opacity=1)
        )
        thermometer[1].next_to(thermometer[0], DOWN, buff=-0.1)
        thermometer.next_to(fault_cell, UP, buff=0.3)
        temp_label = Tex("Temp rising", font_size=16, color=GREY_A)
        temp_label.next_to(thermometer, UP, buff=0.15)

        self.play(FadeIn(thermometer), FadeIn(temp_label))
        self.play(
            fault_cell.animate.set_color(
                WARM_COLOR).set_fill(WARM_COLOR, opacity=0.6),
            run_time=1.2
        )
        self.play(
            fault_cell.animate.set_color(
                HOT_COLOR).set_fill(HOT_COLOR, opacity=0.8),
            run_time=1.2
        )
        self.wait(0.5)

        self.hot_cell = fault_cell
        self.thermometer = VGroup(thermometer, temp_label)
        self.fault_caption = caption

    # ------------------------------------------------------------------
    def show_barrier_containment(self, cells):
        caption = Tex("Thermal barriers stop it spreading to neighbors",
                      font_size=26, color=BARRIER_COLOR)
        caption.to_edge(DOWN, buff=0.5)
        self.play(FadeOut(self.fault_caption), FadeIn(caption))

        # heat arrows trying to spread outward, blocked at barriers
        left_arrow = Arrow(self.hot_cell.get_left(),
                           self.hot_cell.get_left() + LEFT * 0.6,
                           color=HOT_COLOR, buff=0, stroke_width=6)
        right_arrow = Arrow(self.hot_cell.get_right(),
                            self.hot_cell.get_right() + RIGHT * 0.6,
                            color=HOT_COLOR, buff=0, stroke_width=6)

        def make_cross(pos, size=0.18, color=WHITE):
            l1 = Line(pos + UL * size, pos + DR * size,
                      color=color, stroke_width=5)
            l2 = Line(pos + UR * size, pos + DL * size,
                      color=color, stroke_width=5)
            return VGroup(l1, l2)

        blocked_x = make_cross(left_arrow.get_end())
        blocked_x2 = make_cross(right_arrow.get_end())

        self.play(GrowArrow(left_arrow), GrowArrow(right_arrow), run_time=0.8)
        self.play(FadeIn(blocked_x), FadeIn(blocked_x2), run_time=0.5)
        self.wait(0.5)

        # confirm neighbor cells stay cool
        neighbor_check = VGroup(*[
            cells["cells"][i] for i in [1, 3] if i < cells["n"]
        ])
        self.play(Indicate(neighbor_check, color=NORMAL_COLOR, scale_factor=1.05))

        self.play(FadeOut(left_arrow), FadeOut(right_arrow),
                  FadeOut(blocked_x), FadeOut(blocked_x2))
        self.play(FadeOut(caption))
        self.barrier_caption_done = True

    # ------------------------------------------------------------------
    def show_cooling(self, cells):
        caption = Tex("Active cooling keeps the whole module in range",
                      font_size=26, color=COOLANT_COLOR)
        caption.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(caption))

        # coolant loop: a rounded path above and below the module
        top_pipe = Line(cells["cells"][0].get_top() + UP*0.3,
                        cells["cells"][-1].get_top() + UP*0.3,
                        color=COOLANT_COLOR, stroke_width=6)
        bottom_pipe = Line(cells["cells"][0].get_bottom() + DOWN*0.3,
                           cells["cells"][-1].get_bottom() + DOWN*0.3,
                           color=COOLANT_COLOR, stroke_width=6)
        pipe_label = Tex("coolant loop", font_size=16, color=COOLANT_COLOR)
        pipe_label.next_to(top_pipe, UP, buff=0.15)

        self.play(Create(top_pipe), Create(bottom_pipe), FadeIn(pipe_label))

        # flowing coolant dots
        flow_dots = VGroup(*[Dot(radius=0.06, color=COOLANT_COLOR)
                           for _ in range(4)])
        for i, d in enumerate(flow_dots):
            d.move_to(top_pipe.point_from_proportion(i / 4))

        self.play(*[
            MoveAlongPath(d, top_pipe) for d in flow_dots
        ], run_time=1.5, rate_func=linear)

        # fault cell cools back down as system responds
        self.play(
            self.hot_cell.animate.set_color(
                WARM_COLOR).set_fill(WARM_COLOR, opacity=0.5),
            FadeOut(self.thermometer),
            run_time=1.5
        )
        self.wait(0.5)

        self.play(FadeOut(top_pipe), FadeOut(bottom_pipe),
                  FadeOut(pipe_label), FadeOut(flow_dots), FadeOut(caption))

    # ------------------------------------------------------------------
    def show_detection_suppression(self, cells):
        caption = Tex("Sensors detect it early and suppression takes over",
                      font_size=26, color=SAFE_COLOR)
        caption.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(caption))

        sensor = Triangle(color=YELLOW, fill_color=YELLOW, fill_opacity=0.8)
        sensor.scale(0.2)
        sensor.next_to(self.hot_cell, UP, buff=0.4)
        sensor_label = Tex("gas/smoke sensor", font_size=14, color=YELLOW)
        sensor_label.next_to(sensor, UP, buff=0.1)

        self.play(FadeIn(sensor), FadeIn(sensor_label))
        self.play(Flash(sensor, color=YELLOW, flash_radius=0.4))

        alarm = Tex("ALARM: cell isolated", font_size=18, color=YELLOW)
        alarm.next_to(sensor_label, UP, buff=0.15)
        self.play(FadeIn(alarm))
        self.wait(0.3)

        # suppression: mist icon over the fault cell, cell fades to safe grey
        mist = VGroup(*[
            Dot(radius=0.05, color=SAFE_COLOR).move_to(
                self.hot_cell.get_top() + DOWN*0.3 + RIGHT*np.random.uniform(-0.3, 0.3)
            ) for _ in range(10)
        ])
        self.play(FadeIn(mist), run_time=0.5)
        self.play(
            self.hot_cell.animate.set_color(
                GREY_C).set_fill(GREY_C, opacity=0.4),
            FadeOut(mist),
            run_time=1.5
        )

        contained_label = Tex("Fault contained, module keeps running",
                              font_size=18, color=SAFE_COLOR)
        contained_label.next_to(cells["cells"], DOWN, buff=0.5)
        self.play(FadeIn(contained_label))
        self.wait(1.5)

        self.play(FadeOut(caption), FadeOut(sensor), FadeOut(sensor_label),
                  FadeOut(alarm), FadeOut(contained_label))

    # ------------------------------------------------------------------
    def wrap_up(self, cells):
        line1 = Tex("A battery farm does not rely on just one safeguard:",
                    font_size=24, color=WHITE)
        line2 = Tex("physical barriers, active cooling, early detection",
                    font_size=24, color=WHITE)
        line3 = Tex("and suppression all work together, layer on layer.",
                    font_size=24, color=WHITE)
        summary = VGroup(line1, line2, line3).arrange(DOWN, buff=0.2)
        summary.next_to(cells["cells"], DOWN, buff=0.8)
        self.play(FadeIn(summary, shift=UP*0.3))
        self.wait(3)