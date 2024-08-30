import itertools
import random
import os
import schemdraw
from schemdraw.logic import table
from fpdf import FPDF
import time
from cairosvg import svg2png
from io import BytesIO

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
    missing_values = []

    for values in itertools.product([0, 1], repeat=num_vars):
        values_dict = {chr(65 + i): val for i, val in enumerate(values)}
        Q = int(evaluate_expression(expr, values_dict))
        all_rows.append((values_dict, Q))
    
    num_rows = len(all_rows)
    missing_indices = set(random.sample(range(num_rows), num_rows // 2))  # 50% missing entries
    
    for i, (values_dict, Q) in enumerate(all_rows):
        if complete or i not in missing_indices:  # Include the correct answer if complete
            table_str += " | ".join(str(values_dict[header]) for header in headers[:-1]) + f" | {Q}\n"
        else:
            table_str += " | ".join(str(values_dict[header]) for header in headers[:-1]) + " | ?\n"  # Leave missing entries
            missing_values.append(Q)
    
    # Generate the truth table image using schemdraw and save as SVG
    colfmt = 'c|' * (num_vars + 1)
    tbl_schem = table.Table(table=table_str.strip(), colfmt=colfmt)
    d = schemdraw.Drawing()
    d += tbl_schem
    d.save(save_path)
    print(f"Truth table saved as {save_path}")

    return missing_values  # Return missing values for generating options

# Function to convert SVG to PNG in-memory and return a BytesIO object
def convert_svg_to_png(svg_content):
    png_io = BytesIO()
    svg2png(bytestring=svg_content, write_to=png_io)
    png_io.seek(0)  # Reset the pointer to the beginning of the BytesIO object
    return png_io

# Function to generate the four options for the missing entries
def generate_options(correct_missing_values):
    options = [correct_missing_values]

    # Generate three incorrect options
    while len(options) < 4:
        incorrect_option = [random.choice([0, 1]) for _ in range(len(correct_missing_values))]
        if incorrect_option != correct_missing_values and incorrect_option not in options:
            options.append(incorrect_option)

    random.shuffle(options)  # Shuffle options so the correct one isn't always first
    return options

# Function to generate a PDF with questions, options, and answers
def generate_pdf(questions, answers, complete_answers, options_list):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)

    # Add title and time to the first page
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Quiz", ln=True, align='C')

    total_time = len(questions)  # Assuming 1 minute per question
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Total Time: {total_time} minutes", ln=True, align='C')

    pdf.ln(10)  # Add a line break

    # Add questions
    for i, question in enumerate(questions, 1):
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add the question text
        question_text = f"Question {i}: Fill in the missing entries for the expression: {question[1]}"
        pdf.multi_cell(0, 10, txt=question_text, align='L')

        # Add the options for the missing entries
        options_text = "Options:\n"
        for j, option in enumerate(options_list[i-1]):
            options_text += f"{j+1}: {' '.join(map(str, option))}\n"
        pdf.multi_cell(0, 10, txt=options_text, align='L')

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

    # Start answers on a new page
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Answers", ln=True, align='C')
    pdf.ln(10)

    for i, question in enumerate(questions, 1):
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Answer to Question {i}:", ln=True, align='L')

        # Identify and add the correct option
        correct_option_index = None
        correct_missing_values = questions[i-1][2]  # Get correct missing values directly from the question

        for idx, opt in enumerate(options_list[i-1]):
            if opt == correct_missing_values:
                correct_option_index = idx + 1
                break

        correct_option_text = f"Correct Option: {correct_option_index}: {' '.join(map(str, correct_missing_values))}"
        pdf.multi_cell(0, 10, txt=correct_option_text, align='L')

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
    num_questions = int(input("How many questions would you like? "))

    questions = []
    incomplete_answers = []
    complete_answers = []
    options_list = []

    for i in range(num_questions):
        num_vars = random.choice([2, 3, 4, 5])  # Choose random number of variables between 2 and 5
        expr = generate_random_expression(num_vars)

        # Generate and save the incomplete truth table
        incomplete_table_path = os.path.join(image_directory, f'incomplete_truth_table_{i+1}.svg')
        correct_missing_values = generate_truth_table_image(expr, incomplete_table_path, num_vars)
        incomplete_answers.append(incomplete_table_path)

        # Generate and save the complete truth table
        complete_table_path = os.path.join(image_directory, f'complete_truth_table_{i+1}.svg')
        generate_truth_table_image(expr, complete_table_path, num_vars, complete=True)
        complete_answers.append(complete_table_path)

        # Generate four options including the correct missing values
        options = generate_options(correct_missing_values)
        options_list.append(options)

        questions.append((incomplete_table_path, expr, correct_missing_values))

    generate_pdf(questions, incomplete_answers, complete_answers, options_list)

if __name__ == "__main__":
    main()
