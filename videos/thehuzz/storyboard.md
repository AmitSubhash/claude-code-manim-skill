# TheHuzz: Storyboard (Scene Plans)

Paper: TheHuzz: Instruction Fuzzing of Processors Using Golden-Reference Models for Finding Software-Exploitable Vulnerabilities
Authors: Rahul Kande, Addison Crump, Garrett Persyn, Patrick Jauernig, Ahmad-Reza Sadeghi, Aakash Tyagi, Jeyavijayan Rajendran
Venue: USENIX Security 2022

---

## Scene 1: HookScene (~30s)
Template: FULL_CENTER
Content:
- CENTER: Stylized processor chip (rounded rectangle with pins). Glitch effect reveals cracks/bugs.
- Animated counter: "11 bugs found / 5 CVEs / 2 exploits demonstrated"
- Transform chip into question: "How do you find bugs in silicon that can't be patched?"
Visual anchors: Processor chip icon
Cleanup: FadeOut all before Scene 2
Equations: None
Data: 11 bugs, 5 CVEs, 2 exploits, 4 processors tested

Narration concept: "In 2022, researchers at Texas A&M found 11 bugs in four real-world processors -- including five that were serious enough to receive CVE numbers. Two of those bugs could be exploited from software to gain arbitrary code execution or escalate privileges. This is how they did it."

---

## Scene 2: WhyHardwareBugsScene (~60s)
Template: DUAL_PANEL
Content:
- TITLE: "Software Bugs vs Hardware Bugs"
- LEFT panel: "Software Bug" -- icon of code file, red bug icon, then green patch icon overlaid. Arrow: "Deploy patch -> Fixed in hours". Timeline shows: bug found -> patch deployed -> resolved.
- RIGHT panel: "Hardware Bug" -- icon of chip, red bug icon, then NO patch. Stamped "PERMANENT". Show billions of affected chips spreading out. Timeline: bug found -> stuck forever.
- BOTTOM: "Intel Pentium FDIV: $475M recall. Spectre/Meltdown: unfixable in deployed processors."
Visual anchors: Left and right panels
Cleanup: FadeOut all
Equations: None
Data: $475M (Pentium FDIV), billions of chips

---

## Scene 3: VerificationGapScene (~90s)
Template: GRID_CARDS (3 columns, then coverage map)
Content:
- TITLE: "The Verification Gap"
- Phase 1: Three cards side by side:
  - Card 1: "Formal Verification" -- state space icon, counter showing 10^58 states, red X "State explosion"
  - Card 2: "Manual Review" -- magnifying glass, "48% bugs found", red X "Misses half"
  - Card 3: "Prior Fuzzers" -- RFUZZ/DifuzzRTL, red X "Limited coverage metrics"
- Phase 2: FadeOut cards. Show "coverage map" -- a grid of dots where explored=bright, unexplored=dark. Prior fuzzers leave ~60% dark. Highlight the dark regions.
- BOTTOM: "Large regions of hardware behavior remain unexplored"
- Transition bridge: "What if we had an answer key?"
Visual anchors: Coverage map grid
Cleanup: FadeOut all
Equations: None
Data: 10^58 states, 48% detection rate, ~40% coverage gap

---

## Scene 4: GoldenModelScene (~90s)
Template: DUAL_PANEL (morphs to comparison view)
Content:
- TITLE: "The Golden Reference Model"
- Phase 1 (Aha moment): "Every processor has a software simulator that defines correct behavior"
  - Show ISA Specification document (rectangle with text)
  - Arrow splits into two paths: "RTL Design (DUT)" and "Software Simulator (GRM)"
- Phase 2 (Comparison):
  - LEFT: "Design Under Test" -- chip icon, takes instruction stream input, produces register output
  - RIGHT: "Golden Model (Spike)" -- software icon, takes same instruction stream, produces register output
  - Arrow from both outputs to central comparator
  - Match -> green check. Mismatch -> red alert "BUG DETECTED"
- Phase 3: Show concrete examples: "Spike (RISC-V)", "or1ksim (OpenRISC)", "Intel Archsim (x86)"
- BOTTOM: "Like having the teacher's answer key for every possible test"
Visual anchors: DUT and GRM boxes, comparator
Cleanup: Keep DUT/GRM/Comparator for transition to Scene 5
Equations: None
Data: Spike, or1ksim, Intel Archsim, ARM Fast Models

---

## Scene 5: ArchitectureOverviewScene (~90s)
Template: BUILD_UP (progressive pipeline construction)
Content:
- TITLE: "TheHuzz Architecture"
- Build the pipeline left-to-right:
  1. "Seed Generator" box (left) -- labeled_box, BLUE
  2. Arrow -> "Stimulus Generator" box -- labeled_box, TEAL
  3. Fork: Arrow up to "RTL Simulation (DUT)" -- labeled_box, RED
  4. Fork: Arrow down to "Golden Model" -- labeled_box, GREEN
  5. Both arrows converge -> "Comparator" -- labeled_box, YELLOW
  6. Arrow -> "Bug Report" -- labeled_box, ORANGE
  7. Feedback arrow curves from DUT back to Stimulus Generator, labeled "Coverage Feedback"
  8. "Optimizer" box attached to feedback loop -- labeled_box, PURPLE
- Each box appears with Create() + Write() for label
- After full pipeline built, brief glow/pulse on the feedback loop
- BOTTOM: "Coverage-guided fuzzing with differential testing"
Visual anchors: Full pipeline (this becomes the persistent header in later scenes)
Cleanup: Scale down to 0.4x, move to top for Scene 6+
Equations: None
Data: None

---

## Scene 6: MutationScene (~90s)
Template: TOP_PERSISTENT_BOTTOM_CONTENT
Content:
- TOP (persistent): Scaled-down pipeline from Scene 5, "Stimulus Generator" highlighted
- TITLE: "Seed Generation and Mutation"
- Phase 1 -- Show a test program structure:
  - Rectangle representing a program
  - Top section: "Configuration Instructions (CIs)" grayed out, labeled "baremetal setup"
  - Bottom section: "20 Test Instructions (TIs)" highlighted in blue, labeled "fuzzing payload"
- Phase 2 -- Zoom into one instruction (32-bit binary):
  - Show bit fields: [opcode | rs1 | rs2 | rd | funct]
  - Type 1 mutation: Only data bits flip (rs1, rs2, rd change color)
  - Type 2 mutation: Opcode bits also flip -- instruction morphs from "ADD" label to "???" (illegal)
- Phase 3 -- Show mutation gallery (grid of 4 examples):
  - Bitflip: single bit toggles
  - Arithmetic: byte value shifts +/- small amount
  - Clone: instruction duplicated
  - Opcode overwrite: entire opcode field replaced
- BOTTOM: "Type 2 mutations test what happens with instructions NOT in the ISA spec"
Visual anchors: Binary instruction representation
Cleanup: FadeOut content, keep persistent pipeline
Equations: None
Data: 32-bit instruction, 12 mutation types, 20 TIs per test

---

## Scene 7: CoverageMetricsScene (~90s)
Template: TOP_PERSISTENT_BOTTOM_CONTENT (then DUAL_PANEL comparison)
Content:
- TOP (persistent): Scaled pipeline, coverage feedback arrow highlighted
- TITLE: "Six Coverage Metrics"
- Phase 1 -- Gate-level circuit diagram (simplified from paper's Fig 2):
  - Draw: Input DFFs (left) -> Logic gates (AND, OR, NOT) -> MUXes -> State DFF -> Output DFFs
  - Keep it clean: ~7 elements, colored by type
- Phase 2 -- Light up each metric one by one:
  - Statement: RTL code lines glow (overlay code snippet to the right)
  - Branch: Fork paths glow, both true/false
  - Condition: Individual sub-conditions in a compound expression highlight
  - Expression: Combinational logic gates (AND/OR block) glow
  - Toggle: DFF animation showing 0->1->z transitions
  - FSM: State diagram overlay with transition arrows
- Phase 3 -- DUAL_PANEL comparison:
  - LEFT: "DifuzzRTL sees..." -- only 1 MUX + 2 control registers lit, rest dark
  - RIGHT: "TheHuzz sees..." -- ALL elements lit up
  - Percentage labels: "~30% coverage" vs "~90% coverage"
- BOTTOM: "More coverage types = more bugs found"
Visual anchors: Gate-level circuit
Cleanup: FadeOut all
Equations: None
Data: 6 metrics, DifuzzRTL detects 1 MUX + 2 CRs, TheHuzz covers all

---

## Scene 8: OptimizationScene (~60s)
Template: FULL_CENTER
Content:
- TITLE: "Optimization: Finding the Best Tests"
- Phase 1 -- Coverage point grid:
  - ~40 dots arranged in a grid (coverage points)
  - Each instruction-mutation pair shown as a colored circle covering some dots
  - Show 3-4 overlapping circles, each covering different dot subsets
- Phase 2 -- Set cover animation:
  - "Goal: cover ALL dots with fewest circles"
  - Greedy selection: first circle covers 12 dots (pops in), second covers 8 new dots, third covers 6
  - Dots change from gray to bright as covered
  - Counter: "3 pairs cover 26 of 40 points"
- Phase 3 -- Show weights output:
  - Table: Instruction types with weight bars (ADD: high, FENCE: high, NOP: low)
  - "Weights fed back to guide future test generation"
- BOTTOM: "IBM CPLEX solves the set-cover optimization"
Visual anchors: Dot grid
Cleanup: FadeOut all
Equations: min |Q| s.t. Q \subseteq I \times M, \bigcup_{(i,m) \in Q} C_{i,m} \supseteq C_d
Data: Set cover optimization

---

## Scene 9: BugDetectionScene (~60s)
Template: DUAL_PANEL
Content:
- TITLE: "Bug Detection: Trace Comparison"
- LEFT: "RTL Trace (DUT)" -- scrolling list of instruction results
  - "ADD r1, r2, r3 -> r3 = 7" (green check)
  - "SUB r4, r5, r6 -> r6 = 3" (green check)
  - "SUB r7, r8, r9 -> carry = 0" (RED HIGHLIGHT)
- RIGHT: "Golden Model Trace (Spike)" -- same scrolling list
  - "ADD r1, r2, r3 -> r3 = 7" (green check)
  - "SUB r4, r5, r6 -> r6 = 3" (green check)
  - "SUB r7, r8, r9 -> carry = 1" (RED HIGHLIGHT)
- Phase 2: Zoom into the mismatch row
  - "DUT says carry = 0, Golden Model says carry = 1"
  - "BUG B5: Carry flag not updated correctly for subtract"
  - "CVE-2021-41612 -- Can corrupt cryptographic computations"
- BOTTOM: "Found in only 20 instructions"
Visual anchors: Trace comparison alignment
Cleanup: FadeOut all
Equations: None
Data: carry=0 vs carry=1, B5, CVE-2021-41612, 20 instructions

---

## Scene 10: ResultsScene (~60s)
Template: CHART_FOCUS (then GRID_CARDS)
Content:
- TITLE: "Results"
- Phase 1 -- Coverage chart (recreation of paper's Fig 5):
  - Axes: x = "Instructions (thousands)", y = "Coverage Points"
  - Three lines: Random (gray), DifuzzRTL (blue dashed), TheHuzz (red solid)
  - Animate lines drawing from left to right
  - TheHuzz reaches same coverage 3.33x faster
  - After 1M instructions, TheHuzz still climbing while others plateau
- Phase 2 -- Bug summary grid:
  - 4 processor cards: Ariane (4 bugs), mor1kx (3 bugs), or1200 (3 bugs), Rocket (1 bug)
  - "8 new + 3 known = 11 total"
  - "5 CVEs filed"
  - "2 full exploits demonstrated"
- BOTTOM: "3.33x faster than DifuzzRTL, 1.98x faster than random regression"
Visual anchors: Coverage chart
Cleanup: FadeOut all
Equations: None
Data: 3.33x, 1.98x, 11 bugs, 5 CVEs, coverage values from paper

---

## Scene 11: ExploitScene (~90s)
Template: BUILD_UP (step-by-step exploit chain)
Content:
- TITLE: "Exploit: Arbitrary Code Execution via FENCE.I"
- Persistent top label: "Ariane Processor (RISC-V)"
- Step-by-step build with numbered stages:
  1. Show Instruction Cache (box) and Main Memory (box), connected by bus
  2. JIT compiler loads legitimate code into cache (green data flows in)
  3. Attacker overwrites memory region with malicious payload (red data replaces green in memory)
  4. FENCE.I instruction issued (should flush cache to reload from memory)
  5. SPLIT SCREEN:
     - LEFT: "Spike (correct)" -- cache flushed, reloaded from memory (red = malicious code loads)
     - RIGHT: "Ariane (buggy)" -- FENCE.I rejected as illegal, cache NOT flushed (green = stale code remains)
  6. Ariane executes stale cache = attacker's pre-planted code
  7. "Stack overflow -> Arbitrary code execution"
- BOTTOM: "TheHuzz detected this via the Spike vs Ariane mismatch on FENCE.I"
Visual anchors: Cache and memory boxes
Cleanup: FadeOut all
Equations: None
Data: FENCE.I, Ariane, Spike, cache coherence

---

## Scene 12: TakeawayScene (~30s)
Template: FULL_CENTER
Content:
- Phase 1: Pipeline from Scene 5 fades back in at full size
- Phase 2: Key numbers appear overlaid:
  - "11 bugs" near Comparator
  - "5 CVEs" near Bug Report
  - "3.33x faster" near Feedback loop
  - "2 exploits" near top
- Phase 3: Pipeline fades, single takeaway text:
  - "Golden reference models turn hardware verification\ninto a searchable problem."
- Phase 4: Citation:
  - "Kande et al., USENIX Security 2022"
  - "TheHuzz: Instruction Fuzzing of Processors Using\nGolden-Reference Models"
Visual anchors: Pipeline + stats
Cleanup: FadeOut all (end)
Equations: None
Data: 11, 5, 3.33x, 2

---

## Scene Duration Summary
| Scene | Duration | Template |
|-------|----------|----------|
| 1. Hook | 30s | FULL_CENTER |
| 2. Why Hardware Bugs | 60s | DUAL_PANEL |
| 3. Verification Gap | 90s | GRID_CARDS |
| 4. Golden Model | 90s | DUAL_PANEL |
| 5. Architecture | 90s | BUILD_UP |
| 6. Mutation | 90s | TOP_PERSISTENT |
| 7. Coverage Metrics | 90s | TOP_PERSISTENT |
| 8. Optimization | 60s | FULL_CENTER |
| 9. Bug Detection | 60s | DUAL_PANEL |
| 10. Results | 60s | CHART_FOCUS |
| 11. Exploit | 90s | BUILD_UP |
| 12. Takeaway | 30s | FULL_CENTER |
| **TOTAL** | **~13.5 min** | |
