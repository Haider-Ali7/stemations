"""
Reference Template: Math Proof Visualization (Vertical 9:16)
Compliant with Agent Skill: stem-animator
"""
from manim import *

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.background_color = "#0F172A"

class StemationScene(Scene):
    def construct(self):
        # 1. Title Header
        title = Text("Pythagorean Theorem Geometric Proof", font_size=40, color="#38BDF8", weight=BOLD)
        title.move_to(UP * 6.0)
        self.play(FadeIn(title, shift=DOWN * 0.5), run_time=1)
        
        # 2. Main Formula
        formula = Text("a² + b² = c²", font_size=46, color="#FBBF24", weight=BOLD)
        formula.next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(formula), run_time=1)
        
        # 3. Geometric Right-Angled Triangle
        triangle = Polygon(
            [-2.0, -1.0, 0], [1.5, -1.0, 0], [-2.0, 2.5, 0],
            color="#38BDF8", stroke_width=4, fill_color="#1E293B", fill_opacity=0.7
        )
        triangle.move_to(UP * 1.5)
        self.play(Create(triangle), run_time=1.5)
        
        # 4. Labels for Legs & Hypotenuse
        label_a = Text("a", font_size=32, color="#34D399").next_to(triangle, LEFT, buff=0.2)
        label_b = Text("b", font_size=32, color="#34D399").next_to(triangle, DOWN, buff=0.2)
        label_c = Text("c (Hypotenuse)", font_size=28, color="#F472B6").move_to(triangle.get_center() + UP*0.8 + RIGHT*0.8)
        
        self.play(FadeIn(label_a), FadeIn(label_b), FadeIn(label_c), run_time=1.2)
        
        # 5. Insight box at bottom
        insight = Text("The square of hypotenuse equals\nthe sum of squares of both sides.", font_size=26, color="#E2E8F0", line_spacing=0.8)
        insight.move_to(DOWN * 3.8)
        self.play(FadeIn(insight), run_time=1.2)
        
        self.wait(2)
