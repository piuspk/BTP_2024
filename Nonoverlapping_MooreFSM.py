from graphviz import Digraph
import random
from fpdf import FPDF
import os
import cairosvg

class NonOverlappingMooreFSMGenerator:
    def __init__(self, sequence, output_dir="FSM_pdf", image_dir="FSM_images"):
        self.sequence = sequence
        self.states = []
        self.transitions = {}
        self.outputs = {}
        self.output_dir = output_dir
        self.image_dir = image_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)
        self.build_fsm()

    def build_fsm(self):
        n = len(self.sequence)
        self.states = [f'S{i}' for i in range(n+1)]
        self.transitions = {state: {} for state in self.states}
        self.outputs = {state: '0' for state in self.states}

        # Set output for the final state
        self.outputs[self.states[-1]] = '1'

        for i in range(n):
            current_state = self.states[i]
            next_state = self.states[i+1]
            char = self.sequence[i]

            for symbol in '01':
                if symbol == char:
                    self.transitions[current_state][symbol] = next_state
                else:
                    fallback_state = self.find_fallback_state(i, symbol)
                    self.transitions[current_state][symbol] = fallback_state

        # Non-overlapping behavior: after reaching the final state, reset to the start state
        final_state = self.states[-1]
        for symbol in '01':
            self.transitions[final_state][symbol] = self.states[0]

    def find_fallback_state(self, index, symbol):
        for i in range(index, 0, -1):
            if self.sequence[:i] == self.sequence[index-i+1:index] + symbol:
                return self.states[i]
        return self.states[0]

    def remove_random_transition(self):
        state = random.choice(self.states[:-1])
        symbol = random.choice(['0', '1'])

        if symbol in self.transitions[state]:
            removed_transition = self.transitions[state].pop(symbol)
            return (state, symbol, removed_transition)
        return None

    def ask_for_completion(self):
        missing_transition = self.remove_random_transition()
        if missing_transition:
            state, symbol, correct_next_state = missing_transition
            return (state, symbol, correct_next_state)
        return None

    def print_fsm_graphviz(self, filename):
        dot = Digraph()

        for state in self.states:
            # Include the state output in the label
            dot.node(state, label=f"{state}/{self.outputs[state]}")
        
        for state, transitions in self.transitions.items():
            for symbol, next_state in transitions.items():
                dot.edge(state, next_state, label=symbol)

        filepath = os.path.join(self.image_dir, filename)

        dot.render(filepath, format="svg", cleanup=False)
        
        graph_svg_filename = f"{filepath}.svg"
        print(f"Non-Overlapping Moore FSM graph generated as {graph_svg_filename}")
        
        return graph_svg_filename

    def convert_svg_to_png(self, svg_filepath):
        png_filepath = svg_filepath.replace(".svg", ".png")
        cairosvg.svg2png(url=svg_filepath, write_to=png_filepath)
        return png_filepath

    def generate_combined_pdf(self, sequences, filename="NOL_Moore_questions.pdf"):
        pdf = FPDF()
        pdf.set_font("Arial", size=12)

        for i, sequence in enumerate(sequences):
            self.sequence = sequence
            self.build_fsm()

            missing_transition = self.ask_for_completion()

            fsm_graph_svg = self.print_fsm_graphviz(filename=sequence)
            fsm_graph_png = self.convert_svg_to_png(fsm_graph_svg)

            pdf.add_page()

            question_number = i + 1
            pdf.multi_cell(0, 10, f"Question {question_number}:")

            state, symbol, correct_next_state = missing_transition

            question_text = f"In the state diagram below, complete the missing transition for the sequence {sequence} (Assume start is S0): {state} --({symbol})--> ?"
            pdf.multi_cell(0, 10, question_text)

            if os.path.exists(fsm_graph_png):
                pdf.image(fsm_graph_png, x=60, y=pdf.get_y(), w=90)
            else:
                print(f"Error: FSM image not found at {fsm_graph_png}")
                continue

            possible_answers = [
                correct_next_state,  # Correct answer
                self.states[0],      # Some distractor
                self.states[-1],     # Another distractor
                random.choice(self.states[:-1])  # Random distractor
            ]

            random.shuffle(possible_answers)
            correct_answer_index = possible_answers.index(correct_next_state)

            for j, answer in enumerate(possible_answers):
                option_letter = chr(65 + j)
                pdf.multi_cell(0, 10, f"({option_letter}) {answer}")

            pdf.ln(10)
            pdf.multi_cell(0, 10, f"Correct Answer: ({chr(65 + correct_answer_index)}) {possible_answers[correct_answer_index]}")

        pdf_output_path = os.path.join(self.output_dir, filename)
        pdf.output(pdf_output_path)
        print(f"FSM and questions PDF generated as {pdf_output_path}")

# Example usage with multiple sequences
sequences = ["101", "1010", "1101", "011", "0101", "010"]
fsm = NonOverlappingMooreFSMGenerator(sequences[0])

fsm.generate_combined_pdf(sequences)
