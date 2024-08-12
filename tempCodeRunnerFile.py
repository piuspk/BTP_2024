import itertools
import random
import os
import schemdraw
from schemdraw.logic import table
from fpdf import FPDF
import time

# Directory to save truth table PDFs
pdf_directory = r'C:\Users\Lenovo\OneDrive\Desktop\logicgates\pdf'

# Ensure the directory exists
os.makedirs(pdf_directory, exist_ok=True)

# List of predefined logical expressions using only `and` and `not` with three variables (A, B, C)
expressions = [
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
def evaluate_expression(expr, A, B, C):
    return eval(expr.replace('and', ' and ').replace('not', ' not '))

# Function to generate the truth table
def generate_truth_table_image(expr, save_path):
    table_str = "| A | B | C | Q |\n"
    table_str += "|---|---|---|---|\n"
    
    for values in itertools.product([0, 1], repeat=3):
        A, B, C = values
        Q = evaluate_expression(expr, A, B, C)
        table_str += f"| {A} | {B} | {C} | {int(Q)} |\n"
    
    # Generate the truth table image using schemdraw
    colfmt = 'c|c|c|c'
    tbl_schem = table.Table(table=table_str.strip(), colfmt=colfmt)
    d = schemdraw.Drawing()
    d += tbl_schem
    d.save(save_path)
    print(f"Truth table saved as {save_path}")

# Function to generate a PDF with questions and answers
def generate_pdf(questions, answers):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for i, question in enumerate(questions, 1):
        pdf.cell(200, 10, txt=f"Question {i}: What is the truth table for the expression:", ln=True, align='L')
        pdf.multi_cell(200, 10, txt=f"{question[1]}", align='L')
        pdf.ln(5)
        pdf.image(answers[i-1], x=10, w=pdf.w - 20, h=80)  # Adjusting the image height to fit on the page
        pdf.ln(10)
        pdf.add_page()  # Ensure each Q&A pair starts on a new page

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
        # Randomly select an expression
        expr = random.choice(expressions)
        questions.append(expr)

        # Display the question to the user
        print(f"Question {i+1}: What is the truth table for this expression: {expr[1]} ?")
        input("Press Enter to see the correct answer...")

        # Generate and save the truth table image
        save_path = os.path.join(pdf_directory, f'truth_table_{i+1}.png')
        generate_truth_table_image(expr[1], save_path)
        answers.append(save_path)

    # Ask if the user wants to generate a PDF
    create_pdf = input("Do you want to create a PDF with the questions and answers? (yes/no): ").strip().lower()
    if create_pdf == 'yes':
        generate_pdf(questions, answers)

if __name__ == "__main__":
    main()
