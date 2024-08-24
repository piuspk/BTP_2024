import itertools
import random
import os
import schemdraw
from schemdraw.logic import table
from fpdf import FPDF
import time
import cairosvg
from PIL import Image

# Directory to save truth table PDFs and images
pdf_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\pdf'
image_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\Truthtable'

# Ensure the directories exist
os.makedirs(pdf_directory, exist_ok=True)
os.makedirs(image_directory, exist_ok=True)

# Define logic gates functions
gates = {
    'AND': lambda a, b: a and b,
    'OR': lambda a, b: a or b,
    'NAND': lambda a, b: not (a and b),
    'NOR': lambda a, b: not (a or b),
    'XOR': lambda a, b: a != b,
    'XNOR': lambda a, b: a == b
}

# Function to generate the truth table
def generate_truth_table_image(gate_name, save_path):
    num_vars = 2  # Only for 2-input gates
    headers = ['A', 'B', 'Q']
    
    table_str = " | ".join(headers) + "\n"
    table_str += "|".join(["---"] * len(headers)) + "\n"
    
    for values in itertools.product([0, 1], repeat=num_vars):
        Q = gates[gate_name](*values)
        table_str += " | ".join(map(str, values)) + f" | {int(Q)}\n"
    
    # Generate the truth table image using schemdraw
    colfmt = 'c|' * len(headers)
    tbl_schem = table.Table(table=table_str.strip(), colfmt=colfmt)
    d = schemdraw.Drawing()
    d += tbl_schem
    d.save(save_path)
    print(f"Truth table saved as {save_path}")

# Function to convert SVG to PNG
def convert_svg_to_png(svg_path, png_path):
    with open(svg_path, "rb") as svg_file:
        svg_data = svg_file.read()
    png_data = cairosvg.svg2png(bytestring=svg_data)
    with open(png_path, "wb") as png_file:
        png_file.write(png_data)

# Function to generate a PDF with questions and answers
def generate_pdf(questions, answers, correct_answers):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)

    # Page settings for fitting two questions per page
    page_height = pdf.h
    margin = 10
    content_height = page_height - 2 * margin
    
    question_height = 15
    truth_table_height = content_height // 2 - question_height - 10
    options_height = content_height // 2 - 10

    num_questions = len(questions)
    for i in range(0, num_questions, 2):
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add the first question
        q1 = i
        if q1 < num_questions:
            pdf.set_xy(margin, margin)
            question_text1 = f"Question {q1 + 1}: Which logic gate does the following truth table represent?"
            pdf.multi_cell(0, question_height, txt=question_text1, align='L')

            # Add the first truth table image
            pdf.ln(5)
            svg_path1 = answers[q1]
            png_path1 = os.path.join(image_directory, f'truth_table_{q1 + 1}.png')
            convert_svg_to_png(svg_path1, png_path1)
            
            with Image.open(png_path1) as img:
                original_width, original_height = img.size
                new_width = original_width * 0.5
                new_height = original_height * 0.5

                max_width = pdf.w - 2 * margin
                max_height = truth_table_height
                if new_width > max_width:
                    new_width = max_width
                    new_height = new_width * (original_height / original_width)
                
                if new_height > max_height:
                    new_height = max_height
                    new_width = new_height * (original_width / original_height)

            pdf.image(png_path1, x=margin, w=new_width, h=new_height)

            # Add options for the first question
            pdf.ln(5)
            pdf.set_font("Arial", size=12)
            
            options1 = list(gates.keys())
            correct_option1 = correct_answers[q1]
            random.shuffle(options1)  # Shuffle options
            options1 = options1[:4]  # Limit to 4 options
            if correct_option1 not in options1:
                options1[-1] = correct_option1  # Ensure correct option is included
            random.shuffle(options1)  # Shuffle again to randomize position

            # Add options in grid format (2x2)
            for row in range(2):
                pdf.set_y(pdf.get_y() + 5)
                for col in range(2):
                    idx = row * 2 + col
                    if idx < len(options1):
                        pdf.set_x(margin + col * 90)  # Adjust x position for grid
                        pdf.cell(45, 10, txt=f"({chr(97 + idx)}) {options1[idx]}", ln=False, align='L')

            # Add the correct answer at the end
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Correct Answer: {correct_option1}", ln=True, align='L')

        # Add the second question (if available)
        q2 = i + 1
        if q2 < num_questions:
            pdf.set_xy(margin, pdf.get_y() + options_height + 15)
            question_text2 = f"Question {q2 + 1}: Which logic gate does the following truth table represent?"
            pdf.multi_cell(0, question_height, txt=question_text2, align='L')

            # Add the second truth table image
            pdf.ln(5)
            svg_path2 = answers[q2]
            png_path2 = os.path.join(image_directory, f'truth_table_{q2 + 1}.png')
            convert_svg_to_png(svg_path2, png_path2)
            
            with Image.open(png_path2) as img:
                original_width, original_height = img.size
                new_width = original_width * 0.5
                new_height = original_height * 0.5

                max_width = pdf.w - 2 * margin
                max_height = truth_table_height
                if new_width > max_width:
                    new_width = max_width
                    new_height = new_width * (original_height / original_width)
                
                if new_height > max_height:
                    new_height = max_height
                    new_width = new_height * (original_width / original_height)

            pdf.image(png_path2, x=margin, w=new_width, h=new_height)

            # Add options for the second question
            pdf.ln(5)
            pdf.set_font("Arial", size=12)
            
            options2 = list(gates.keys())
            correct_option2 = correct_answers[q2]
            random.shuffle(options2)  # Shuffle options
            options2 = options2[:4]  # Limit to 4 options
            if correct_option2 not in options2:
                options2[-1] = correct_option2  # Ensure correct option is included
            random.shuffle(options2)  # Shuffle again to randomize position

            # Add options in grid format (2x2)
            for row in range(2):
                pdf.set_y(pdf.get_y() + 5)
                for col in range(2):
                    idx = row * 2 + col
                    if idx < len(options2):
                        pdf.set_x(margin + col * 90)  # Adjust x position for grid
                        pdf.cell(45, 10, txt=f"({chr(97 + idx)}) {options2[idx]}", ln=False, align='L')

            # Add the correct answer at the end
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Correct Answer: {correct_option2}", ln=True, align='L')

    # Save PDF with a unique name
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    pdf_name = os.path.join(pdf_directory, f'identify_gate_{timestamp}.pdf')
    pdf.output(pdf_name)
    print(f"PDF saved as {pdf_name}")

# Main program
def main():
    # Ask how many questions
    num_questions = int(input("How many questions would you like? "))

    questions = []
    answers = []
    correct_answers = []

    for i in range(num_questions):
        # Randomly choose a gate for this question
        gate_name = random.choice(list(gates.keys()))
        questions.append(gate_name)
        correct_answers.append(gate_name)

        # Display the question to the user
        print(f"Question {i + 1}: Which logic gate does the following truth table represent?")
        input("Press Enter to see the truth table...")

        # Generate and save the truth table image
        svg_path = os.path.join(image_directory, f'truth_table_{i + 1}.svg')
        generate_truth_table_image(gate_name, svg_path)
        answers.append(svg_path)

    # Ask if the user wants to generate a PDF
    create_pdf = input("Do you want to create a PDF with the questions and answers? (yes/no): ").strip().lower()
    if create_pdf == 'yes':
        generate_pdf(questions, answers, correct_answers)

if __name__ == "__main__":
    main()
