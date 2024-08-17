import itertools
import random
import os
import schemdraw
from schemdraw.logic import table
from fpdf import FPDF
import time
import cairosvg

# Directory to save truth table PDFs and images
pdf_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\pdf'
image_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\Truthtable'

# Ensure the directories exist
os.makedirs(pdf_directory, exist_ok=True)
os.makedirs(image_directory, exist_ok=True)

# Function to generate random logical expressions
def generate_random_expression(variables):
    operators = ['and', 'or']
    num_operators = random.randint(1, 3)  # Choose between 1 to 3 operators for complexity
    expression = random.choice(variables)
    
    for _ in range(num_operators):
        op = random.choice(operators)
        expr = random.choice(variables)
        if random.choice([True, False]):
            expr = f'not ({expr})'
        expression = f'({expression}) {op} ({expr})'
    
    return expression

# Function to evaluate logical expressions
def evaluate_expression(expr, A, B, C, D, E):
    return eval(expr.replace('and', ' and ').replace('or', ' or ').replace('not', ' not '))

# Function to generate the truth table
def generate_truth_table_image(expr, save_path):
    table_str = "| A | B | C | D | E | Q |\n"
    table_str += "|---|---|---|---|---|---|\n"
    
    for values in itertools.product([0, 1], repeat=5):
        A, B, C, D, E = values
        Q = evaluate_expression(expr, A, B, C, D, E)
        table_str += f"| {A} | {B} | {C} | {D} | {E} | {int(Q)} |\n"
    
    # Generate the truth table image using schemdraw
    colfmt = 'c|c|c|c|c|c'
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
    pdf.set_auto_page_break(auto=True, margin=15)

    for i, question in enumerate(questions, 1):
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add the question and expression on a single line
        question_text = f"Question {i}: Which expression corresponds to the given truth table?"
        pdf.multi_cell(0, 10, txt=question_text, align='L')
        
        # Add the truth table image
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Truth Table:", ln=True, align='L')

        # Calculate the image size to fit the page
        max_width = pdf.w - 20  # Max width of image (page width - margins)
        max_height = pdf.h - pdf.get_y() - 30  # Max height of image (page height - current position - margin)
        
        # Convert SVG to PNG
        png_path = os.path.join(image_directory, f'truth_table_{i}.png')
        convert_svg_to_png(answers[i-1], png_path)
        
        pdf.image(png_path, x=10, w=max_width, h=max_height)  # Adjust image size to fit on the page

        # Add options for expressions
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        options = [generate_random_expression(['A', 'B', 'C', 'D', 'E']) for _ in range(3)]
        correct_option = correct_answers[i-1]
        options.append(correct_option)  # Add correct option to the options list
        random.shuffle(options)  # Shuffle options

        for idx, option in enumerate(options, 1):
            pdf.cell(200, 10, txt=f"Option {idx}: {option}", ln=True, align='L')

        # Add the correct answer at the end
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Correct Answer: {correct_option}", ln=True, align='L')
        
    # Save PDF with a unique name
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    pdf_name = os.path.join(pdf_directory, f'identify_expression_{timestamp}.pdf')
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
        # Randomly generate an expression
        expr = generate_random_expression(['A', 'B', 'C', 'D', 'E'])
        questions.append(expr)
        correct_answers.append(expr)

        # Display the question to the user
        print(f"Question {i+1}: Which expression corresponds to the given truth table?")
        input("Press Enter to see the correct answer...")

        # Generate and save the truth table image
        svg_path = os.path.join(image_directory, f'truth_table_{i+1}.svg')
        generate_truth_table_image(expr, svg_path)
        answers.append(svg_path)

    # Ask if the user wants to generate a PDF
    create_pdf = input("Do you want to create a PDF with the questions and answers? (yes/no): ").strip().lower()
    if create_pdf == 'yes':
        generate_pdf(questions, answers, correct_answers)

if __name__ == "__main__":
    main()
