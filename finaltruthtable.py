import itertools
import random
import os
import schemdraw
from schemdraw.logic import table
from fpdf import FPDF
import time
from cairosvg import svg2png
from io import BytesIO

# Directory to save truth table PDFs and images
pdf_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\pdf'
image_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\Truthtable'

# Ensure the directories exist
os.makedirs(pdf_directory, exist_ok=True)
os.makedirs(image_directory, exist_ok=True)

# Possible operators for generating random expressions
operators = ['and', 'or', 'not']

# Function to generate a random logical expression
def generate_random_expression(num_vars):
    variables = [chr(65 + i) for i in range(num_vars)]  # A, B, C, ...
    expr = variables[0]
    for i in range(1, num_vars):
        op = random.choice(operators[:-1])  # Choose 'and' or 'or'
        if random.choice([True, False]):
            expr = f'{expr} {op} {variables[i]}'
        else:
            expr = f'{expr} {op} not {variables[i]}'
    if random.choice([True, False]):
        expr = f'not ({expr})'
    return expr

# Function to evaluate logical expressions
def evaluate_expression(expr, values_dict):
    # Replace variables in the expression with their corresponding values
    for var in values_dict:
        expr = expr.replace(var, str(values_dict[var]))
    return eval(expr)

# Function to generate the truth table and save it as SVG and PNG
def generate_truth_table_images(expr, save_path_svg, num_vars):
    headers = [chr(65 + i) for i in range(num_vars)]  # A, B, C, ...
    headers.append('Q')
    
    table_str = " | ".join(headers) + "\n"
    table_str += "|".join(["---"] * (num_vars + 1)) + "\n"

    for values in itertools.product([0, 1], repeat=num_vars):
        values_dict = {chr(65 + i): val for i, val in enumerate(values)}
        Q = int(evaluate_expression(expr, values_dict))
        row = " | ".join(str(values_dict[chr(65 + i)]) for i in range(num_vars))
        table_str += f"{row} | {Q}\n"

    # Generate the truth table image using schemdraw and save as SVG
    colfmt = 'c|' * (num_vars + 1)
    tbl_schem = table.Table(table=table_str.strip(), colfmt=colfmt)
    d = schemdraw.Drawing()
    d += tbl_schem
    d.save(save_path_svg)
    print(f"Truth table saved as SVG: {save_path_svg}")

    # Convert SVG to PNG and return the file path
    png_data = svg2png(url=save_path_svg)
    save_path_png = save_path_svg.replace(".svg", ".png")
    with open(save_path_png, "wb") as f:
        f.write(png_data)
    
    return save_path_png

# Function to generate a PDF with questions and answers
def generate_pdf(questions):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for i, (expr, svg_path, png_path) in enumerate(questions, 1):
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add the question and expression on a single line
        question_text = f"Question {i}: What is the truth table for the expression: {expr}"
        pdf.multi_cell(0, 10, txt=question_text, align='L')
        
        # Add label and image
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Answer:", ln=True, align='L')

        # Calculate the image size to fit the page
        max_width = pdf.w - 20  # Max width of image (page width - margins)
        max_height = pdf.h - pdf.get_y() - 30  # Max height of image (page height - current position - margin)
        
        pdf.image(png_path, x=10, w=max_width, h=max_height)  # Adjust image size to fit on the page

    # Save PDF with a unique name
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    pdf_name = os.path.join(pdf_directory, f'truth_tables_{timestamp}.pdf')
    pdf.output(pdf_name)
    print(f"PDF saved as {pdf_name}")

# Main program
def main():
    # Ask how many questions
    num_questions = int(input("How many questions would you like? "))

    questions = []

    for i in range(num_questions):
        # Randomly select the number of variables for this question
        num_vars = random.choice([2, 3, 4, 5])

        # Generate a random expression with the selected number of variables
        expr = generate_random_expression(num_vars)
        print(f"Generated expression: {expr}")
        
        # Generate and save the truth table images (SVG and PNG)
        save_path_svg = os.path.join(image_directory, f'truth_table_{i+1}.svg')
        save_path_png = generate_truth_table_images(expr, save_path_svg, num_vars)
        
        questions.append((expr, save_path_svg, save_path_png))

    # Ask if the user wants to generate a PDF
    create_pdf = input("Do you want to create a PDF with the questions and answers? (yes/no): ").strip().lower()
    if create_pdf == 'yes':
        generate_pdf(questions)

if __name__ == "__main__":
    main()
