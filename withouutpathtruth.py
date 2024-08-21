import itertools
import random
import matplotlib.pyplot as plt
import matplotlib.table as tbl
from io import BytesIO
from fpdf import FPDF
import tempfile
import os

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

# Function to generate the truth table and return PNG data in memory
def generate_truth_table_image_in_memory(expr, num_vars):
    headers = [chr(65 + i) for i in range(num_vars)]  # A, B, C, ...
    headers.append('Q')
    
    rows = []
    for values in itertools.product([0, 1], repeat=num_vars):
        values_dict = {chr(65 + i): val for i, val in enumerate(values)}
        Q = int(evaluate_expression(expr, values_dict))
        row = list(values_dict.values()) + [Q]
        rows.append(row)

    # Create a matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(8, len(rows) * 0.5 + 1))  # Adjust size for table
    ax.axis('off')
    
    # Create a table
    table = tbl.Table(ax, bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    
    # Add table cells
    for i, header in enumerate(headers):
        table.add_cell(i / len(headers), 1, width=1 / len(headers), height=1 / (len(rows) + 1),
                       text=header, loc='center', bbox=dict(facecolor='lightgrey', edgecolor='black'))
    
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            table.add_cell(j / len(headers), (len(rows) - i) / (len(rows) + 1),
                           width=1 / len(headers), height=1 / (len(rows) + 1),
                           text=str(cell), loc='center', bbox=dict(edgecolor='black'))

    ax.add_table(table)
    
    # Save the table as an image in memory
    png_io = BytesIO()
    plt.savefig(png_io, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    
    return png_io.getvalue()

# Function to generate a PDF with questions and answers in memory
def generate_pdf_in_memory(questions):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for i, (expr, png_data) in enumerate(questions, 1):
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
        
        # Save the PNG data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(png_data)
            temp_file_path = temp_file.name
        
        # Add the image to the PDF
        pdf.image(temp_file_path, x=10, w=max_width, h=max_height)  # Adjust image size to fit on the page

        # Clean up temporary file
        os.remove(temp_file_path)

    # Save PDF to memory
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    
    return pdf_output

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
        
        # Generate the truth table image and get the PNG data in memory
        png_data = generate_truth_table_image_in_memory(expr, num_vars)
        
        questions.append((expr, png_data))

    # Ask if the user wants to generate a PDF
    create_pdf = input("Do you want to create a PDF with the questions and answers? (yes/no): ").strip().lower()
    if create_pdf == 'yes':
        pdf_output = generate_pdf_in_memory(questions)

        # Save the PDF to disk
        pdf_filename = 'truth_tables.pdf'
        with open(pdf_filename, 'wb') as f:
            f.write(pdf_output.read())
        print(f"PDF generated and saved as {pdf_filename}.")

if __name__ == "__main__":
    main()
