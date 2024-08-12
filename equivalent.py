import random
import os
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import schemdraw
import schemdraw.logic as logic
from schemdraw.parsing import logicparse

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

def create_pdf(questions_data):
    """Create a PDF with questions, images, options, and correct answers."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    def calculate_image_height(image_path, target_width):
        """Calculate the image height to maintain aspect ratio."""
        with Image.open(image_path) as img:
            aspect_ratio = img.height / img.width
            return target_width * aspect_ratio
    
    for i, (question, image_path1, image_path2, options_text, correct_answer) in enumerate(questions_data):
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 10, f'Question {i + 1}:', ln=True)
        
        # Add question text
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, question)
        
        # Add images with resizing to fit the page width
        pdf.ln(10)
        
        page_width = pdf.w - 2 * pdf.l_margin
        
        for image_path in [image_path1, image_path2]:
            image_width = page_width
            image_height = calculate_image_height(image_path, image_width)
            
            if image_height > pdf.h - 2 * pdf.t_margin:
                image_height = pdf.h - 2 * pdf.t_margin
                image_width = image_height / (calculate_image_height(image_path, 1) / image_width)
            
            pdf.image(image_path, x=pdf.l_margin, w=image_width, h=image_height)
            pdf.ln(10)
        
        # Add options
        pdf.ln(10)
        pdf.multi_cell(0, 10, options_text)
        
        # Add correct answer
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f'Correct Answer: {correct_answer}', ln=True)
    
    pdf_output_path = 'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\logic_questions.pdf'
    pdf.output(pdf_output_path)

def main():
    num_variables = int(input("Enter the number of variables (e.g., 3 for a, b, c): "))
    num_questions = int(input("Enter the number of questions to generate: "))
    
    variables = [chr(ord('a') + i) for i in range(num_variables)]
    
    questions_data = []
    
    for i in range(num_questions):
        if random.random() < 0.5:  # 50% chance
            base_expr = random_expression(variables, random.randint(2, 5))
            expr1 = base_expr
            expr2 = base_expr
        else:
            base_expr = random_expression(variables, random.randint(2, 5))
            expr1 = base_expr
            expr2 = random_expression(variables, random.randint(2, 5))
        
        output_path1 = f'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\random_logic_circuit_{i+1}_1.png'
        output_path2 = f'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\random_logic_circuit_{i+1}_2.png'
        
        create_and_save_diagram(expr1, output_path1)
        create_and_save_diagram(expr2, output_path2)
        
        question = f"Are these two circuits equivalent?\nExpression 1: {expr1}\nExpression 2: {expr2}"
        options_text = "Options:\n1. Yes\n2. No"
        correct_answer = 'yes' if expr1 == expr2 else 'no'
        
        questions_data.append((question, output_path1, output_path2, options_text, correct_answer))
    
    create_pdf(questions_data)
    print(f"PDF created successfully at C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\logic_questions.pdf")

if __name__ == "__main__":
    main()
