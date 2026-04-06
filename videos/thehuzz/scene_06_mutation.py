import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.style import *


class MutationScene(Scene):
    """Scene 6: Seed Generation and Mutation -- ~90 seconds.

    Phase 1: Program structure (CI section dimmed, TI section highlighted with brace).
    Phase 2: Bit-level view of a 32-bit RISC-V instruction with two mutation types.
    Phase 3: 2x2 gallery of four mutation strategy icons.
    """

    # Field layout for a 32-bit RISC-V R-type instruction
    # [opcode:7, rd:5, funct3:3, rs1:5, rs2:5, funct7:7]  standard order
    # Simplified for display: [opcode:7, rs1:5, rs2:5, rd:5, funct:10]
    FIELDS = [
        ("opcode", 7, BUG_RED),
        ("rs1",    5, CHIP_BLUE),
        ("rs2",    5, CHIP_BLUE),
        ("rd",     5, CHIP_BLUE),
        ("funct", 10, COVERAGE_TEAL),
    ]

    def construct(self) -> None:
        self.camera.background_color = BG_COLOR

        # ------------------------------------------------------------------ #
        # Phase 1: Program structure                                          #
        # ------------------------------------------------------------------ #
        title = safe_text(
            "Seed Generation and Mutation",
            font_size=TITLE_SIZE,
            color=WHITE,
        ).move_to([0, TITLE_Y, 0])

        self.play(Write(title))
        self.wait(HOLD_SHORT)

        prog_group, ci_rect, ti_rect, ci_label, ci_sub, ti_label, ti_sub = (
            self._build_program_view()
        )
        prog_group.move_to([0, -0.1, 0])

        self.play(FadeIn(prog_group, shift=UP * 0.2))
        self.wait(HOLD_SHORT)

        # Brace pointing to TI section
        brace = Brace(ti_rect, direction=RIGHT, color=MUTATION_YELLOW)
        brace_label = safe_text(
            "These get mutated",
            font_size=LABEL_SIZE,
            color=MUTATION_YELLOW,
            max_width=3.5,
        )
        brace_label.next_to(brace, RIGHT, buff=0.15)

        self.play(Create(brace), Write(brace_label))
        self.wait(HOLD_MEDIUM)

        # Fade everything before phase 2
        self.play(
            FadeOut(title),
            FadeOut(prog_group),
            FadeOut(brace),
            FadeOut(brace_label),
        )

        # ------------------------------------------------------------------ #
        # Phase 2: Bit-level instruction view                                 #
        # ------------------------------------------------------------------ #
        bit_title = safe_text(
            "A Single 32-bit Instruction",
            font_size=HEADING_SIZE,
            color=WHITE,
        ).move_to([0, TITLE_Y, 0])

        self.play(Write(bit_title))

        bit_row, field_groups, field_labels = self._build_bit_row()
        bit_row_group = VGroup(bit_row, field_labels)
        bit_row_group.move_to([0, 0.8, 0])

        self.play(
            LaggedStart(
                *[Create(sq) for sq in bit_row],
                lag_ratio=0.04,
                run_time=1.6,
            )
        )
        self.play(
            LaggedStart(
                *[Write(lbl) for lbl in field_labels],
                lag_ratio=0.15,
            )
        )
        self.wait(HOLD_SHORT)

        # -- Mutation type annotation --
        type1_note = safe_text(
            "Type 1: Mutate rs1 / rs2 / rd / funct only",
            font_size=LABEL_SIZE,
            color=CHIP_BLUE,
            max_width=11.0,
        ).move_to([0, -0.15, 0])

        self.play(FadeIn(type1_note, shift=UP * 0.2))
        self.wait(HOLD_SHORT)

        # Flash mutable fields (all except opcode = index 0)
        mutable_bits = self._get_mutable_bits(bit_row, field_groups)
        self.play(
            LaggedStart(
                *[
                    Succession(
                        Flash(sq, color=MUTATION_YELLOW, flash_radius=0.2, line_length=0.1),
                        sq.animate.set_fill(MUTATION_YELLOW, opacity=0.85),
                    )
                    for sq in mutable_bits
                ],
                lag_ratio=0.03,
                run_time=1.8,
            )
        )
        self.wait(HOLD_SHORT)

        # Reset mutable bit colors back
        self.play(
            *[sq.animate.set_fill(CHIP_BLUE, opacity=0.7) for sq in mutable_bits],
            run_time=0.6,
        )

        self.play(FadeOut(type1_note))

        # -- Type 2: all bits mutate, opcode changes --
        type2_note = safe_text(
            "Type 2: ALL bits change -- opcode becomes unknown",
            font_size=LABEL_SIZE,
            color=BUG_RED,
            max_width=11.0,
        ).move_to([0, -0.15, 0])

        self.play(FadeIn(type2_note, shift=UP * 0.2))
        self.wait(HOLD_SHORT)

        all_bits = list(bit_row)
        self.play(
            LaggedStart(
                *[
                    sq.animate.set_fill(BUG_RED, opacity=0.85)
                    for sq in all_bits
                ],
                lag_ratio=0.02,
                run_time=1.2,
            )
        )

        # Swap opcode label to "???"
        opcode_label = field_labels[0]
        opcode_unknown = safe_text("???", font_size=LABEL_SIZE, color=BUG_RED, max_width=1.8)
        opcode_unknown.move_to(opcode_label.get_center())

        self.play(ReplacementTransform(opcode_label, opcode_unknown))
        self.wait(HOLD_MEDIUM)

        self.play(
            FadeOut(bit_title),
            FadeOut(bit_row),
            FadeOut(opcode_unknown),
            *[FadeOut(lbl) for lbl in field_labels[1:]],
            FadeOut(type2_note),
        )

        # ------------------------------------------------------------------ #
        # Phase 3: Mutation gallery (2x2 grid)                               #
        # ------------------------------------------------------------------ #
        gallery_title = safe_text(
            "Mutation Strategies",
            font_size=HEADING_SIZE,
            color=WHITE,
        ).move_to([0, TITLE_Y, 0])

        self.play(Write(gallery_title))

        cards = self._build_mutation_gallery()
        cards.move_to([0, 0.0, 0])

        self.play(
            LaggedStart(
                *[FadeIn(c, shift=UP * 0.15) for c in cards],
                lag_ratio=0.25,
            )
        )
        self.wait(HOLD_MEDIUM)

        note = bottom_note(
            "Type 2 mutations test what happens with instructions NOT in the ISA spec"
        )
        self.play(FadeIn(note))
        self.wait(HOLD_LONG)

        # ------------------------------------------------------------------ #
        # Final cleanup                                                       #
        # ------------------------------------------------------------------ #
        self.play(
            FadeOut(gallery_title),
            FadeOut(cards),
            FadeOut(note),
        )

    # ---------------------------------------------------------------------- #
    # Phase 1 helpers                                                         #
    # ---------------------------------------------------------------------- #

    def _build_program_view(
        self,
    ) -> tuple[VGroup, Rectangle, Rectangle, VGroup, VGroup, VGroup, VGroup]:
        """Build the program rectangle split into CI (dimmed) and TI (highlighted).

        Returns
        -------
        prog_group : VGroup
            All elements composing the program view.
        ci_rect : Rectangle
        ti_rect : Rectangle
        ci_label : VGroup
        ci_sub : VGroup
        ti_label : VGroup
        ti_sub : VGroup
        """
        prog_width = 4.2
        ci_height = 2.2
        ti_height = 2.8
        corner_r = 0.15

        # CI section (top, dimmed)
        ci_rect = RoundedRectangle(
            width=prog_width,
            height=ci_height,
            corner_radius=corner_r,
            color=DIM_GRAY,
            fill_color=DIM_GRAY,
            fill_opacity=0.18,
            stroke_width=2,
        )

        ci_label = safe_text(
            "Configuration Instructions (CIs)",
            font_size=LABEL_SIZE,
            color=LABEL_GRAY,
            max_width=prog_width - 0.4,
        )
        ci_label.move_to(ci_rect.get_center() + UP * 0.3)

        ci_sub = safe_text(
            "baremetal setup -- never mutated",
            font_size=SMALL_SIZE,
            color=DIM_GRAY,
            max_width=prog_width - 0.4,
        )
        ci_sub.move_to(ci_rect.get_center() - UP * 0.3)

        # TI section (bottom, highlighted)
        ti_rect = RoundedRectangle(
            width=prog_width,
            height=ti_height,
            corner_radius=corner_r,
            color=CHIP_BLUE,
            fill_color=CHIP_BLUE,
            fill_opacity=0.22,
            stroke_width=2.5,
        )

        ti_label = safe_text(
            "20 Test Instructions (TIs)",
            font_size=LABEL_SIZE,
            color=CHIP_BLUE,
            max_width=prog_width - 0.4,
        )
        ti_label.move_to(ti_rect.get_center() + UP * 0.4)

        ti_sub = safe_text(
            "fuzzing payload",
            font_size=SMALL_SIZE,
            color=MUTATION_YELLOW,
            max_width=prog_width - 0.4,
        )
        ti_sub.move_to(ti_rect.get_center() - UP * 0.35)

        # Stack vertically: CI on top, TI below
        prog_stack = VGroup(
            VGroup(ci_rect, ci_label, ci_sub),
            VGroup(ti_rect, ti_label, ti_sub),
        )
        prog_stack.arrange(DOWN, buff=0.0)

        prog_group = VGroup(
            ci_rect, ci_label, ci_sub,
            ti_rect, ti_label, ti_sub,
        )

        return prog_group, ci_rect, ti_rect, ci_label, ci_sub, ti_label, ti_sub

    # ---------------------------------------------------------------------- #
    # Phase 2 helpers                                                         #
    # ---------------------------------------------------------------------- #

    def _build_bit_row(
        self,
    ) -> tuple[VGroup, list[tuple[int, int]], VGroup]:
        """Build a row of 32 colored squares grouped by field.

        Returns
        -------
        bit_row : VGroup
            All 32 squares left-to-right.
        field_groups : list of (start, end) index pairs per field.
        field_labels : VGroup
            One label per field centered under its group.
        """
        bit_size = 0.28
        bit_gap = 0.03
        total_bits = 32

        # Build squares
        squares = []
        bit_colors: list[str] = []
        for field_name, n_bits, color in self.FIELDS:
            for _ in range(n_bits):
                bit_colors.append(color)

        for color in bit_colors:
            sq = Square(
                side_length=bit_size,
                color=color,
                fill_color=color,
                fill_opacity=0.7,
                stroke_width=1.5,
            )
            squares.append(sq)

        bit_row = VGroup(*squares)
        bit_row.arrange(RIGHT, buff=bit_gap)

        # Constrain total width to safe zone
        if bit_row.width > 12.5:
            bit_row.scale_to_fit_width(12.5)

        # Field boundary indices
        field_groups: list[tuple[int, int]] = []
        idx = 0
        for _, n_bits, _ in self.FIELDS:
            field_groups.append((idx, idx + n_bits))
            idx += n_bits

        # Labels centered under each field group
        label_items = []
        for i, (field_name, n_bits, color) in enumerate(self.FIELDS):
            start, end = field_groups[i]
            group_squares = VGroup(*squares[start:end])
            lbl = safe_text(field_name, font_size=SMALL_SIZE, color=color, max_width=2.2)
            lbl.next_to(group_squares, DOWN, buff=0.18)
            # Center label under field span
            lbl.move_to(
                [group_squares.get_center()[0], lbl.get_center()[1], 0]
            )
            label_items.append(lbl)

        field_labels = VGroup(*label_items)

        return bit_row, field_groups, field_labels

    def _get_mutable_bits(
        self,
        bit_row: VGroup,
        field_groups: list[tuple[int, int]],
    ) -> list:
        """Return all squares that are NOT part of the opcode field (index 0).

        Parameters
        ----------
        bit_row : VGroup
            All 32 squares.
        field_groups : list of (start, end) tuples per field.

        Returns
        -------
        list
            Squares belonging to rs1, rs2, rd, funct fields.
        """
        opcode_end = field_groups[0][1]
        squares = list(bit_row)
        return squares[opcode_end:]

    # ---------------------------------------------------------------------- #
    # Phase 3 helpers                                                         #
    # ---------------------------------------------------------------------- #

    def _build_mutation_gallery(self) -> VGroup:
        """Build a 2x2 grid of labeled mutation strategy cards.

        Returns
        -------
        VGroup
            Arranged 2x2 grid of four cards.
        """
        card_bitflip = self._make_gallery_card(
            label="Bitflip",
            icon=self._icon_bitflip(),
            color=MUTATION_YELLOW,
        )
        card_arith = self._make_gallery_card(
            label="Arithmetic",
            icon=self._icon_arithmetic(),
            color=COVERAGE_TEAL,
        )
        card_clone = self._make_gallery_card(
            label="Clone",
            icon=self._icon_clone(),
            color=GOLDEN_GREEN,
        )
        card_opcode = self._make_gallery_card(
            label="Opcode Replace",
            icon=self._icon_opcode(),
            color=BUG_RED,
        )

        row1 = VGroup(card_bitflip, card_arith)
        row1.arrange(RIGHT, buff=0.7)
        row2 = VGroup(card_clone, card_opcode)
        row2.arrange(RIGHT, buff=0.7)

        grid = VGroup(row1, row2)
        grid.arrange(DOWN, buff=0.6)

        if grid.width > 12.0:
            grid.scale_to_fit_width(12.0)

        return grid

    @staticmethod
    def _make_gallery_card(label: str, icon: VMobject, color: str) -> VGroup:
        """Rounded card with centered icon and label below.

        Parameters
        ----------
        label : str
        icon : VMobject
        color : str

        Returns
        -------
        VGroup
        """
        rect = RoundedRectangle(
            width=2.8,
            height=2.0,
            corner_radius=0.18,
            color=color,
            fill_color=color,
            fill_opacity=DIM_OPACITY,
            stroke_width=2,
        )
        icon.set_height(0.8)
        icon.move_to(rect.get_center() + UP * 0.25)

        lbl = safe_text(label, font_size=LABEL_SIZE, color=color, max_width=2.4)
        lbl.move_to(rect.get_bottom() + UP * 0.42)

        return VGroup(rect, icon, lbl)

    @staticmethod
    def _icon_bitflip() -> VGroup:
        """Single square with a vertical arrow crossing it (bit toggle)."""
        sq = Square(
            side_length=0.45,
            color=MUTATION_YELLOW,
            fill_color=MUTATION_YELLOW,
            fill_opacity=0.7,
            stroke_width=2,
        )
        zero = Text("0", font_size=LABEL_SIZE, color=WHITE)
        zero.move_to(sq)
        arrow = Arrow(
            sq.get_top() + UP * 0.1,
            sq.get_bottom() + DOWN * 0.1,
            buff=0.0,
            color=WHITE,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.25,
        )
        return VGroup(sq, zero, arrow)

    @staticmethod
    def _icon_arithmetic() -> VGroup:
        """A byte box with '+1' label beside it."""
        box = Rectangle(
            width=0.5,
            height=0.45,
            color=COVERAGE_TEAL,
            fill_color=COVERAGE_TEAL,
            fill_opacity=0.7,
            stroke_width=2,
        )
        byte_lbl = Text("0x3A", font_size=SMALL_SIZE, color=WHITE)
        byte_lbl.move_to(box)
        delta = Text("+1", font_size=LABEL_SIZE, color=COVERAGE_TEAL)
        delta.next_to(box, RIGHT, buff=0.15)
        return VGroup(box, byte_lbl, delta)

    @staticmethod
    def _icon_clone() -> VGroup:
        """Two overlapping rectangles (instruction duplicated)."""
        r1 = Rectangle(
            width=0.55,
            height=0.38,
            color=GOLDEN_GREEN,
            fill_color=GOLDEN_GREEN,
            fill_opacity=0.6,
            stroke_width=2,
        )
        r2 = r1.copy().shift(RIGHT * 0.18 + DOWN * 0.18)
        arrow = CurvedArrow(
            r1.get_right() + UP * 0.05,
            r2.get_right() + DOWN * 0.05,
            angle=-TAU / 5,
            color=GOLDEN_GREEN,
            stroke_width=2,
        )
        return VGroup(r1, r2, arrow)

    @staticmethod
    def _icon_opcode() -> VGroup:
        """Opcode field box with text replaced by '???'."""
        box = Rectangle(
            width=0.9,
            height=0.42,
            color=BUG_RED,
            fill_color=BUG_RED,
            fill_opacity=0.6,
            stroke_width=2,
        )
        lbl_add = Text("ADD", font_size=SMALL_SIZE, color=WHITE)
        lbl_add.move_to(box)
        lbl_unk = Text("???", font_size=SMALL_SIZE, color=BUG_RED)
        lbl_unk.next_to(box, RIGHT, buff=0.12)
        arrow = Arrow(
            box.get_right(),
            lbl_unk.get_left(),
            buff=0.05,
            color=BUG_RED,
            stroke_width=2,
            max_tip_length_to_length_ratio=0.3,
        )
        return VGroup(box, lbl_add, arrow, lbl_unk)
