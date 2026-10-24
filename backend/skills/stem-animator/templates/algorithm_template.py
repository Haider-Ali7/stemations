"""
Reference Template: Algorithm Visualization (Vertical 9:16)
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
        title = Text("Binary Search", font_size=44, color="#38BDF8", weight=BOLD)
        title.move_to(UP * 6.0)
        self.play(FadeIn(title, shift=DOWN * 0.5), run_time=1)
        
        # 2. Subtitle Concept
        subtitle = Text("Divide & Conquer in O(log n)", font_size=28, color="#94A3B8")
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(subtitle), run_time=0.8)
        
        # 3. Create Array Elements
        values = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
        boxes = VGroup()
        for v in values:
            box = Square(side_length=0.7, color="#334155", fill_color="#1E293B", fill_opacity=0.9)
            num = Text(str(v), font_size=24, color="#F8FAFC")
            num.move_to(box.get_center())
            cell = VGroup(box, num)
            boxes.add(cell)
            
        boxes.arrange(RIGHT, buff=0.1)
        boxes.scale_to_fit_width(7.6)
        boxes.move_to(UP * 1.5)
        self.play(Create(boxes), run_time=1.5)
        
        # 4. Target Annotation
        target_label = Text("Search Target: 23", font_size=32, color="#FBBF24")
        target_label.move_to(DOWN * 0.5)
        self.play(FadeIn(target_label), run_time=0.8)
        
        # 5. Visual Search Step: Middle Element (Index 4 or 5)
        mid_box = boxes[5][0] # 23 is at index 5
        self.play(
            mid_box.animate.set_fill("#34D399", opacity=0.9).set_stroke("#10B981", width=3),
            run_time=1.2
        )
        self.play(Indicate(boxes[5]), run_time=1.0)
        
        # 6. Conclusion Text
        found_text = Text("Target Found! Steps: 3", font_size=32, color="#34D399", weight=BOLD)
        found_text.move_to(DOWN * 3.5)
        self.play(FadeIn(found_text, shift=UP * 0.3), run_time=1.0)
        
        self.wait(2)
