import random
import os
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import schemdraw
import schemdraw.logic as logic
from schemdraw.parsing import logicparse
from datetime import datetime

# Define possible gates
gates = ['and', 'or', 'nand', 'nor', 'xor', 'xnor', 'not']

def random_expression(variables, num_gates):
    """Generate a random logic expression with a given number of gates and variables."""
    if num_gates == 0:  # Base case: return a single variable
        return random.choice(variables)
    
    # Randomly choose a gate and build an expression
    gate = random.choice(gates)
    expr = '('
    
    if gate in ['not']:  # Unary gate
        expr += f'{gate} {random_expression(variables, num_gates - 1)}'
    else:  # Binary gates
        expr += f'{random_expression(variables, num_gates - 1)} {gate} {random_expression(variables, num_gates - 1)}'
    
    expr += ')'
    return expr

def create_and_save_diagram(expression, file_path):
    """Create a logic circuit diagram from the expression and save it."""
    d = logicparse(expression, outlabel=r'$\text{Output}$')
    d.save(file_path)

def add_text_to_image(image_path, question_text):
    """Add question text to the image and save the updated image."""
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        
        text_position = (10, img.height - 20)
        draw.text(text_position, question_text, font=font, fill="black")
        
        updated_image_path = image_path.replace(".png", "_with_question.png")
        img.save(updated_image_path)
    
    return updated_image_path

def generate_simple_gate_operation_question():
    """Generate a question involving a simple gate operation and save the gate image."""
    gates = ['AND', 'OR', 'NOT', 'NAND', 'NOR', 'XOR']
    gate_type = random.choice(gates)
    
    if gate_type == 'NOT':
        input_values = [random.choice([0, 1])]
    else:
        input_values = [random.choice([0, 1]) for _ in range(2)]
    
    if gate_type == 'AND':
        output = int(all(input_values))
    elif gate_type == 'OR':
        output = int(any(input_values))
    elif gate_type == 'NOT':
        output = int(not input_values[0])
    elif gate_type == 'NAND':
        output = int(not all(input_values))
    elif gate_type == 'NOR':
        output = int(not any(input_values))
    elif gate_type == 'XOR':
        output = int(sum(input_values) % 2 == 1)
    
    d = schemdraw.Drawing()
    d.config(fontsize=8)
    
    if gate_type == 'AND':
        gate = logic.And(inputs=2)
        d += gate
    elif gate_type == 'OR':
        gate = logic.Or(inputs=2)
        d += gate
    elif gate_type == 'NAND':
        gate = logic.Nand(inputs=2)
        d += gate
    elif gate_type == 'NOR':
        gate = logic.Nor(inputs=2)
        d += gate
    elif gate_type == 'XOR':
        gate = logic.Xor(inputs=2)
        d += gate
    elif gate_type == 'NOT':
        gate = logic.Not()
        d += gate
    
    image_path = f'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\image\\{gate_type}_Gate.png'
    d.save(image_path)
    
    options = ['0', '1']
    correct_answer = str(output)
    random.shuffle(options)
    
    options_text = "Options:\n"
    for i, option in enumerate(options):
        options_text += f"{i+1}. {option}\n"
    
    question = f"What is the output of the {gate_type} gate with inputs {', '.join(map(str, input_values))}?"
    if gate_type == 'NOT':
        question = f"What is the output of the {gate_type} gate with input {input_values[0]}?"
    
    return question, image_path, options_text, correct_answer

def create_pdf(questions_data):
    """Create a PDF with questions, images, options, and correct answers."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    def calculate_image_height(image_path, target_width):
        """Calculate the image height to maintain aspect ratio."""
        with Image.open(image_path) as img:
            aspect_ratio = img.height / img.width
            return target_width * aspect_ratio
    
    for i, (question, image_paths, options_text, correct_answer) in enumerate(questions_data):
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 10, f'Question {i + 1}:', ln=True)
        
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, question)
        
        pdf.ln(10)
        
        page_width = pdf.w - 2 * pdf.l_margin
        
        for image_path in image_paths:
            image_width = page_width
            image_height = calculate_image_height(image_path, image_width)
            
            if image_height > pdf.h - 2 * pdf.t_margin:
                image_height = pdf.h - 2 * pdf.t_margin
                image_width = image_height / (calculate_image_height(image_path, 1) / image_width)
            
            pdf.image(image_path, x=pdf.l_margin, w=image_width, h=image_height)
            pdf.ln(10)
        
        pdf.ln(10)
        pdf.multi_cell(0, 10, options_text)
        
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f'Correct Answer: {correct_answer}', ln=True)
    
    pdf_output_path = f'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\pdf\\logic_questions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    pdf.output(pdf_output_path)

def main():
    num_questions = int(input("How many questions would you like to generate? (Max 50) "))
    if num_questions > 50:
        num_questions = 50
    
    num_variables = int(input("Enter the number of variables (e.g., 3 for a, b, c): "))
    variables = [chr(ord('a') + i) for i in range(num_variables)]
    
    questions_data = []
    user_answers = []

    for _ in range(num_questions):
        if random.choice([True, False]):
            if random.random() < 0.5:
                base_expr = random_expression(variables, random.randint(2, 5))
                expr1 = base_expr
                expr2 = base_expr
            else:
                base_expr = random_expression(variables, random.randint(2, 5))
                expr1 = base_expr
                expr2 = random_expression(variables, random.randint(2, 5))
            
            output_path1 = f'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\image\\random_logic_circuit_{random.randint(1, 10000)}_1.png'
            output_path2 = f'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\image\\random_logic_circuit_{random.randint(1, 10000)}_2.png'
            
            create_and_save_diagram(expr1, output_path1)
            create_and_save_diagram(expr2, output_path2)
            
            question = f"Are these two circuits equivalent?\nExpression 1: {expr1}\nExpression 2: {expr2}"
            options_text = "Options:\n1. Yes\n2. No"
            correct_answer = 'yes' if expr1 == expr2 else 'no'
            
            user_answer = input(f"{question}\n{options_text}\nYour answer: ")
            user_answers.append(user_answer)

            questions_data.append((question, [output_path1, output_path2], options_text, correct_answer))
        else:
            question, image_path, options, correct_answer = generate_simple_gate_operation_question()
            
            user_answer = input(f"{question}\n{options}\nYour answer: ")
            user_answers.append(user_answer)

            questions_data.append((question, [image_path], options, correct_answer))
    
    generate_pdf = input("Would you like to generate the PDF with the questions and answers? (yes/no): ")
    
    if generate_pdf.lower() == 'yes':
        create_pdf(questions_data)
        print(f"PDF created successfully at C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\pdf")
    else:
        print("PDF generation skipped.")

if __name__ == "__main__":
    main()
