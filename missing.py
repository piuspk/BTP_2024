import itertools
import random
import os
import schemdraw
from schemdraw.logic import table
from fpdf import FPDF
import time
from cairosvg import svg2png  # Use this to convert SVG to PNG in-memory
from io import BytesIO  # For handling in-memory file-like objects

# Directories to save truth table PDFs and images
pdf_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\pdf'
image_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\Truthtable'

# Ensure the directories exist
os.makedirs(pdf_directory, exist_ok=True)
os.makedirs(image_directory, exist_ok=True)

# Possible operators for generating random expressions
operators = ['and', 'or', 'not']

# Function to generate a random logical expression
def generate_random_expression(num_vars):
    variables = [chr(65 + i) for i in range(num_vars)]  # A, B, C, D, E...
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

# Function to generate the truth table with 50% missing entries
def generate_truth_table_image(expr, save_path, num_vars, complete=False):
    headers = [chr(65 + i) for i in range(num_vars)]  # A, B, C, D, E...
    headers.append('Q')
    
    table_str = " | ".join(headers) + "\n"
    table_str += "|".join(["---"] * (num_vars + 1)) + "\n"
    
    all_rows = []
    
    for values in itertools.product([0, 1], repeat=num_vars):
        values_dict = {chr(65 + i): val for i, val in enumerate(values)}
        Q = int(evaluate_expression(expr, values_dict))
        all_rows.append((values_dict, Q))
    
    num_rows = len(all_rows)
    missing_indices = set(random.sample(range(num_rows), num_rows // 2))  # 50% missing entries
    
    for i, (values_dict, Q) in enumerate(all_rows):
        if complete or i not in missing_indices:  # 50% chance to include the correct answer
            table_str += " | ".join(str(values_dict[header]) for header in headers[:-1]) + f" | {Q}\n"
        else:
            table_str += " | ".join(str(values_dict[header]) for header in headers[:-1]) + " | ?\n"  # Leave missing entries
    
    # Generate the truth table image using schemdraw and save as SVG
    colfmt = 'c|' * (num_vars + 1)
    tbl_schem = table.Table(table=table_str.strip(), colfmt=colfmt)
    d = schemdraw.Drawing()
    d += tbl_schem
    d.save(save_path)
    print(f"Truth table saved as {save_path}")

# Function to convert SVG to PNG in-memory and return a BytesIO object
def convert_svg_to_png(svg_content):
    png_io = BytesIO()
    svg2png(bytestring=svg_content, write_to=png_io)
    png_io.seek(0)  # Reset the pointer to the beginning of the BytesIO object
    return png_io

# Function to generate a PDF with questions and answers
def generate_pdf(questions, answers, complete_answers):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)

    for i, question in enumerate(questions, 1):
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add the question text
        question_text = f"Question {i}: Fill in the missing entries for the expression: {question[1]}"
        pdf.multi_cell(0, 10, txt=question_text, align='L')

        # Add the incomplete truth table image, ensuring it fits on a single page
        with open(answers[i-1], 'rb') as svg_file:
            svg_content = svg_file.read()
            png_data = convert_svg_to_png(svg_content)
            # Save the PNG temporarily
            png_temp_path = f'tmp_image_{i}.png'
            with open(png_temp_path, 'wb') as f:
                f.write(png_data.read())
            img_width = pdf.w - 20
            img_height = pdf.h - pdf.get_y() - 20
            pdf.image(png_temp_path, x=10, y=pdf.get_y(), w=img_width, h=img_height)
            os.remove(png_temp_path)  # Delete the temporary PNG file

        # Add the answer on the next page
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Answer:", ln=True, align='L')

        # Add the complete truth table image, ensuring it fits on a single page
        with open(complete_answers[i-1], 'rb') as svg_file:
            svg_content = svg_file.read()
            png_data = convert_svg_to_png(svg_content)
            # Save the PNG temporarily
            png_temp_path = f'tmp_image_complete_{i}.png'
            with open(png_temp_path, 'wb') as f:
                f.write(png_data.read())
            img_width = pdf.w - 20
            img_height = pdf.h - pdf.get_y() - 20
            pdf.image(png_temp_path, x=10, y=pdf.get_y(), w=img_width, h=img_height)
            os.remove(png_temp_path)  # Delete the temporary PNG file

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
    incomplete_answers = []
    complete_answers = []

    for i in range(num_questions):
        # Randomly select the number of variables for this question (2 to 5)
        num_vars = random.choice([2, 3, 4, 5])

        # Randomly generate an expression with the selected number of variables
        expr = ('Q' + str(i+1), generate_random_expression(num_vars))
        questions.append(expr)

        # Display the question to the user
        print(f"Question {i+1}: Fill in the missing entries for this expression: {expr[1]}")
        input("Press Enter to see the correct answer...")

        # Generate and save the incomplete truth table image in SVG format
        svg_save_path = os.path.join(image_directory, f'truth_table_incomplete_{i+1}.svg')
        generate_truth_table_image(expr[1], svg_save_path, num_vars, complete=False)
        incomplete_answers.append(svg_save_path)

        # Generate and save the complete truth table image in SVG format
        svg_save_path_complete = os.path.join(image_directory, f'truth_table_complete_{i+1}.svg')
        generate_truth_table_image(expr[1], svg_save_path_complete, num_vars, complete=True)
        complete_answers.append(svg_save_path_complete)

    # Ask if the user wants to generate a PDF
    create_pdf = input("Do you want to create a PDF with the questions and answers? (yes/no): ").strip().lower()
    if create_pdf == 'yes':
        generate_pdf(questions, incomplete_answers, complete_answers)

if __name__ == "__main__":
    main()
