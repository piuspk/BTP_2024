import itertools
import os
import random
import time
from fpdf import FPDF

# Directory to save the PDF
pdf_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\pdf'

# Ensure the directory exists
os.makedirs(pdf_directory, exist_ok=True)

# Function to generate random logical expression with variables A, B, C, D, E
def generate_random_expression(num_vars):
    operators = ['and', 'or', 'nand', 'nor', 'xor', 'xnor']
    vars = ['A', 'B', 'C', 'D', 'E'][:num_vars]
    
    expression = f'{random.choice(vars)} {random.choice(operators)} {random.choice(vars)}'
    
    # Optionally add more complexity
    if random.choice([True, False]):
        expression = f'({expression}) {random.choice(operators)} {random.choice(vars)}'
        
    return expression

# Function to generate the truth table for a given expression
def generate_truth_table(expression, num_vars):
    headers = ['A', 'B', 'C', 'D', 'E'][:num_vars] + ['Result']
    table = []

    for values in itertools.product([0, 1], repeat=num_vars):
        # Prepare the local variables
        local_vars = {f'{chr(65+i)}': values[i] for i in range(num_vars)}
        try:
            result = eval(expression, {}, local_vars)
            table.append(values + (int(result),))
        except Exception as e:
            print(f"Error evaluating expression '{expression}': {e}")

    return table, headers

# Function to compare two truth tables
def are_tables_equivalent(table1, table2):
    return table1 == table2

# Function to generate a PDF with the questions and options
def generate_pdf(questions, answers, correct_answers):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)

    # Page settings
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for i, (expr1, expr2) in enumerate(questions):
        pdf.set_font("Arial", size=12)
        question_text = (
            f"Question {i + 1}: Are the following expressions equivalent?\n\n"
            f"1. {expr1}\n"
            f"2. {expr2}\n"
        )
        pdf.multi_cell(0, 10, txt=question_text)

        # Add options
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        options = ["(a) Yes", "(b) No"]
        for option in options:
            pdf.cell(0, 10, txt=option, ln=True)

        # Add the correct answer (for internal use, not shown in the PDF)
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=f"Correct Answer: {'Yes' if correct_answers[i] else 'No'}", ln=True)

    # Save PDF with a unique name
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    pdf_name = os.path.join(pdf_directory, f'expression_equivalence_{timestamp}.pdf')
    pdf.output(pdf_name)
    print(f"PDF saved as {pdf_name}")

# Main function
def main():
    # Ask how many questions
    num_questions = int(input("Enter the number of questions: "))
    
    questions = []
    correct_answers = []

    for _ in range(num_questions):
        num_vars = random.choice([2, 3, 4, 5])
        
        # Generate two different expressions with the same number of variables
        expr1 = generate_random_expression(num_vars)
        expr2 = generate_random_expression(num_vars)

        # Generate and compare truth tables
        table1, _ = generate_truth_table(expr1, num_vars)
        table2, _ = generate_truth_table(expr2, num_vars)
        
        equivalent = are_tables_equivalent(table1, table2)

        questions.append((expr1, expr2))
        correct_answers.append(equivalent)

    # Generate PDF
    generate_pdf(questions, questions, correct_answers)

if __name__ == "__main__":
    main()
