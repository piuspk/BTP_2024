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

# Function to generate random logical expressions with a given set of variables
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
def evaluate_expression(expr, *values):
    # Map variable names to their corresponding values
    variables = 'ABCDE'
    for i, value in enumerate(values):
        expr = expr.replace(variables[i], str(value))
    return eval(expr.replace('and', ' and ').replace('or', ' or ').replace('not', ' not '))

# Function to generate the truth table
def generate_truth_table_image(expr, save_path, num_vars):
    headers = [chr(65 + i) for i in range(num_vars)]  # Generate headers A, B, C, etc.
    headers.append('Q')
    
    table_str = " | ".join(headers) + "\n"
    table_str += "|".join(["---"] * (num_vars + 1)) + "\n"
    
    for values in itertools.product([0, 1], repeat=num_vars):
        Q = evaluate_expression(expr, *values)
        table_str += " | ".join(map(str, values)) + f" | {int(Q)}\n"
    
    # Generate the truth table image using schemdraw
    colfmt = 'c|' * (num_vars + 1)
    tbl_schem = table.Table(table=table_str.strip(), colfmt=colfmt)
    d = schemdraw.Drawing()
    d += tbl_schem
    d.save(save_path)
    print(f"Truth table saved as {save_path}")

# Function to convert SVG to PNG without reducing image quality
def convert_svg_to_png(svg_path, png_path):
    # Retain the resolution while converting to PNG
    with open(svg_path, "rb") as svg_file:
        svg_data = svg_file.read()
    png_data = cairosvg.svg2png(bytestring=svg_data, scale=2.0)  # Scaling to maintain quality
    with open(png_path, "wb") as png_file:
        png_file.write(png_data)

# Function to generate a PDF with questions and answers
def generate_pdf(questions, answers, correct_answers, original_options):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    num_questions_per_page = 2
    num_pages = (len(questions) + num_questions_per_page - 1) // num_questions_per_page

    # Standard image size for consistency
    image_width = 60  # Width of image in mm
    image_height = 80  # Height of image in mm

    for page_num in range(num_pages):
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        if page_num == 0:
            pdf.cell(0, 10, txt="Logic Gate Quiz", ln=True, align='C')
        pdf.ln(10)

        start_index = page_num * num_questions_per_page
        end_index = min(start_index + num_questions_per_page, len(questions))

        for i in range(start_index, end_index):
            question_idx = i + 1
            pdf.set_font("Arial", 'B', 14)

            question_text = f"Question {question_idx}: Which expression corresponds to the given truth table?"
            pdf.multi_cell(0, 10, txt=question_text, align='L')
            pdf.ln(5)

            # Convert SVG to PNG
            png_path = os.path.join(image_directory, f'truth_table_{question_idx}.png')
            convert_svg_to_png(answers[i], png_path)

            # Calculate position for image and text
            y_start = pdf.get_y()
            pdf.image(png_path, x=pdf.w - image_width - 20, y=y_start, w=image_width, h=image_height)

            # Add options for expressions on the left side
            pdf.set_font("Arial", 'B', 12)
            pdf.multi_cell(pdf.w - image_width - 30, 10, txt="Options", align='L')
            
            options = original_options[i]
            pdf.set_font("Arial", size=12)

            for idx, option in enumerate(options, 1):
                pdf.multi_cell(pdf.w - image_width - 30, 10, txt=f"({idx}) {option}", align='L')
                pdf.ln(1)

            # Move to the next line with additional spacing
            pdf.ln(image_height + 1)  # Adjust spacing between questions

    # Adding the answer section at the end
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="Answer Key", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    for i, correct_option in enumerate(correct_answers, 1):
        options = original_options[i-1]
        correct_option_number = options.index(correct_option) + 1
        pdf.multi_cell(0, 10, txt=f"Question {i}: ({correct_option_number}) {correct_option}", align='L')

    # Save PDF with a unique name
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    pdf_name = os.path.join(pdf_directory, f'identify_expression_{timestamp}.pdf')
    pdf.output(pdf_name)
    print(f"PDF saved as {pdf_name}")

# Main program (updated to store original options)
def main():
    # Ask how many questions
    num_questions = int(input("How many questions would you like? "))

    questions = []
    answers = []
    correct_answers = []
    original_options = []
    generated_expressions = set()  # Set to track generated expressions

    for i in range(num_questions):
        # Randomly choose the number of variables for this question (2 to 3)
        num_vars = random.choice([2, 3])

        # Generate a unique random expression
        while True:
            variables = [chr(65 + i) for i in range(num_vars)]
            expr = generate_random_expression(variables)
            if expr not in generated_expressions:
                generated_expressions.add(expr)
                break

        questions.append(expr)
        correct_answers.append(expr)

        # Generate options including the correct one
        options = [generate_random_expression(['A', 'B', 'C']) for _ in range(3)]
        options.append(expr)
        random.shuffle(options)
        original_options.append(options)  # Store the options for later use

        # Generate and save the truth table image
        svg_path = os.path.join(image_directory, f'truth_table_{i+1}.svg')
        generate_truth_table_image(expr, svg_path, num_vars)
        answers.append(svg_path)

    # Ask if the user wants to generate a PDF
    create_pdf = input("Do you want to create a PDF with the questions and answers? (yes/no): ").strip().lower()
    if create_pdf == 'yes':
        generate_pdf(questions, answers, correct_answers, original_options)

if __name__ == "__main__":
    main()
