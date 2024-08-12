import itertools
import random
import os
import schemdraw
from schemdraw.logic import table
from fpdf import FPDF
import time

# Directory to save truth table PDFs and images
pdf_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\pdf'
image_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\Truthtable'

# Ensure the directories exist
os.makedirs(pdf_directory, exist_ok=True)
os.makedirs(image_directory, exist_ok=True)

# List of predefined logical expressions using only `and` and `not` with two variables (A, B)
expressions_two_vars = [
    ('Q1', 'A and not B'),
    ('Q2', 'not A and B'),
    ('Q3', 'A and B'),
    ('Q4', 'not A and not B'),
    ('Q5', 'not (A and B)'),
    ('Q6', 'not (A and not B)'),
    ('Q7', 'A and not (B)'),
    ('Q8', 'not (A and B)'),
    ('Q9', 'A and not (not B)'),
    ('Q10', 'not (A and not (B))'),
]

# List of predefined logical expressions using only `and` and `not` with three variables (A, B, C)
expressions_three_vars = [
    ('Q1', 'A and not B and C'),
    ('Q2', 'not A and B and C'),
    ('Q3', 'A and B and not C'),
    ('Q4', 'not A and not B and C'),
    ('Q5', 'not (A and B) and C'),
    ('Q6', 'not (A and not B) and C'),
    ('Q7', 'A and not (B and C)'),
    ('Q8', 'not (A and B) and not C'),
    ('Q9', 'A and not (B and not C)'),
    ('Q10', 'not (A and not (B and C))'),
    ('Q11', 'A and B and C'),
    ('Q12', 'not (A and B and C)'),
    ('Q13', 'A and not (B and C)'),
    ('Q14', 'not A and not (B and C)'),
    ('Q15', 'A and not (B and not C)'),
    ('Q16', 'not (A and not (B and not C))'),
    ('Q17', 'A and not (not B and C)'),
    ('Q18', 'not (A and not B) and C'),
    ('Q19', 'A and B and not C'),
    ('Q20', 'not (A and B) and not C'),
]

# Function to evaluate logical expressions
def evaluate_expression(expr, *args):
    expr = expr.replace('and', ' and ').replace('not', ' not ')
    return eval(expr, dict(zip('ABC', args)))

# Function to generate the truth table
def generate_truth_table_image(expr, save_path, num_vars):
    headers = '| ' + ' | '.join('A' if i == 0 else ('B' if i == 1 else 'C') for i in range(num_vars)) + ' | Q |\n'
    separator = '| ' + ' | '.join('---' for _ in range(num_vars)) + ' | --- |\n'
    table_str = headers + separator
    
    for values in itertools.product([0, 1], repeat=num_vars):
        Q = evaluate_expression(expr, *values)
        table_str += '| ' + ' | '.join(str(v) for v in values) + f' | {int(Q)} |\n'
    
    # Generate the truth table image using schemdraw
    colfmt = '|' + 'c|' * (num_vars + 1)
    tbl_schem = table.Table(table=table_str.strip(), colfmt=colfmt)
    d = schemdraw.Drawing()
    d += tbl_schem
    d.save(save_path)
    print(f"Truth table saved as {save_path}")

# Function to generate a PDF with questions and answers
def generate_pdf(questions, answers):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for i, question in enumerate(questions, 1):
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add the question
        question_text = f"Question {i}: What is the truth table for the expression: {question[1]}?"
        pdf.cell(0, 10, txt=question_text, ln=True, align='L')

        # Add label and image
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt="Answer:", ln=True, align='L')

        # Calculate the image size to fit the page
        max_width = pdf.w - 20  # Max width of image (page width - margins)
        max_height = pdf.h - pdf.get_y() - 30  # Max height of image (page height - current position - margin)
        
        pdf.image(answers[i-1], x=10, w=max_width, h=max_height)  # Adjust image size to fit on the page
        
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
    answers = []

    for i in range(num_questions):
        # Randomly select an expression from either module
        if random.choice([True, False]):
            expr = random.choice(expressions_two_vars)
            num_vars = 2
        else:
            expr = random.choice(expressions_three_vars)
            num_vars = 3

        questions.append(expr)

        # Display the question to the user
        print(f"Question {i+1}: What is the truth table for this expression: {expr[1]} ?")
        input("Press Enter to see the correct answer...")

        # Generate and save the truth table image
        save_path = os.path.join(image_directory, f'truth_table_{i+1}.png')
        generate_truth_table_image(expr[1], save_path, num_vars)
        answers.append(save_path)

    # Ask if the user wants to generate a PDF
    create_pdf = input("Do you want to create a PDF with the questions and answers? (yes/no): ").strip().lower()
    if create_pdf == 'yes':
        generate_pdf(questions, answers)

if __name__ == "__main__":
    main()
