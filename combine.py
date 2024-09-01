import random
import os
from fpdf import FPDF
from PIL import Image
import cairosvg
import schemdraw
import schemdraw.logic as logic
from schemdraw.parsing import logicparse
from datetime import datetime

# Define possible gates
gates = ['and', 'or', 'nand', 'nor', 'xor', 'xnor', 'not']

def random_expression(variables, num_gates):
    """Generate a random logic expression with a given number of gates and variables."""
    if num_gates == 0:
        return random.choice(variables)
    
    gate = random.choice(gates)
    expr = '('
    
    if gate == 'not':
        expr += f'{gate} {random_expression(variables, num_gates - 1)}'
    else:
        expr += f'{random_expression(variables, num_gates - 1)} {gate} {random_expression(variables, num_gates - 1)}'
    
    expr += ')'
    return expr

def create_and_save_diagram(expression, file_path):
    """Create a logic circuit diagram from the expression and save it as SVG."""
    try:
        d = logicparse(expression, outlabel=r'$\text{Output}$')
        d.save(file_path)
    except Exception as e:
        print(f"Error creating diagram for expression '{expression}': {e}")

def convert_svg_to_png(svg_path):
    """Convert SVG file to PNG format with increased resolution."""
    png_path = svg_path.replace('.svg', '.png')
    # Increase scale to improve quality
    cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2.0)  # Scale factor increased to 2.0
    return png_path

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
    
    svg_path = f'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\image\\{gate_type}_Gate.svg'
    d.save(svg_path)
    
    options = ['0', '1']
    correct_answer = str(output)
    random.shuffle(options)
    
    options_text = "Options:\n"
    for i, option in enumerate(options):
        options_text += f"{i+1}. {option}\n"
    
    question = f"What is the output of the {gate_type} gate with inputs {', '.join(map(str, input_values))}?"
    if gate_type == 'NOT':
        question = f"What is the output of the {gate_type} gate with input {input_values[0]}?"
    
    return question, svg_path, options_text, correct_answer

def create_pdf(questions_data):
    """Create a PDF with questions, options, SVG images (converted to PNG), and correct answers."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for i, (question, svg_paths, options_text, correct_answer) in enumerate(questions_data):
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add question
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 10, f'Question {i + 1}:', ln=True)
        
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, question)
        
        pdf.ln(5)
        
        # Add options
        pdf.multi_cell(0, 10, options_text)
        
        pdf.ln(5)
        
        # Add images (converted from SVG to PNG)
        for svg_path in svg_paths:
            png_path = convert_svg_to_png(svg_path)
            page_width = pdf.w - 2 * pdf.l_margin
            pdf.image(png_path, x=pdf.l_margin, w=page_width)
            pdf.ln(5)
        
        # Add correct answer
        pdf.cell(0, 10, f'Correct Answer: {correct_answer}', ln=True)
        pdf.ln(10)
    
    pdf_output_path = f'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\pdf\\logic_questions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    pdf.output(pdf_output_path)
    print(f"PDF created successfully at {pdf_output_path}")

def main():
    num_questions = int(input("How many questions would you like to generate? (Max 50) "))
    if num_questions > 50:
        num_questions = 50
    
    num_variables = int(input("Enter the number of variables (e.g., 3 for a, b, c): "))
    variables = [chr(ord('a') + i) for i in range(num_variables)]
    
    questions_data = []
    
    for _ in range(num_questions):
        if random.choice([True, False]):
            if random.random() < 0.5:
                base_expr = random_expression(variables, random.randint(1, 3))
                expr1 = base_expr
                expr2 = base_expr
            else:
                base_expr = random_expression(variables, random.randint(1, 3))
                expr1 = base_expr
                expr2 = random_expression(variables, random.randint(1, 3))
            
            svg_path1 = f'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\image\\random_logic_circuit_{random.randint(1, 10000)}_1.svg'
            svg_path2 = f'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\image\\random_logic_circuit_{random.randint(1, 10000)}_2.svg'
            
            create_and_save_diagram(expr1, svg_path1)
            create_and_save_diagram(expr2, svg_path2)
            
            question = f"Are these two circuits equivalent?\nExpression 1: {expr1}\nExpression 2: {expr2}"
            options_text = "Options:\n1. Yes\n2. No"
            correct_answer = 'yes' if expr1 == expr2 else 'no'
            
            questions_data.append((question, [svg_path1, svg_path2], options_text, correct_answer))
        else:
            question, svg_path, options, correct_answer = generate_simple_gate_operation_question()
            questions_data.append((question, [svg_path], options, correct_answer))
    
    create_pdf(questions_data)

if __name__ == "__main__":
    main()
