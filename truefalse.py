import random
import os
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import schemdraw
import schemdraw.logic as logic

def add_text_to_image(image_path, question_text):
    """Add question text to the image and save the updated image."""
    # Open the existing image
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        
        # Define position for the text
        text_position = (10, img.height - 20)
        
        # Add text to the image
        draw.text(text_position, question_text, font=font, fill="black")
        
        # Save the updated image
        updated_image_path = image_path.replace(".png", "_with_question.png")
        img.save(updated_image_path)
    
    return updated_image_path

def generate_simple_gate_operation_question():
    """Generate a question involving a simple gate operation and save the gate image."""
    # Define available gate types
    gates = ['AND', 'OR', 'NOT', 'NAND', 'NOR', 'XOR']
    
    # Select a random gate type
    gate_type = random.choice(gates)
    
    # Generate random input values
    if gate_type == 'NOT':
        input_values = [random.choice([0, 1])]
    else:
        input_values = [random.choice([0, 1]) for _ in range(2)]
    
    # Evaluate the gate operation
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
    
    # Create and save the gate image
    d = schemdraw.Drawing()
    d.config(fontsize=8)  # Set font size for the labels
    
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
    
    # Save the image
    image_path = f'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\{gate_type}_Gate.png'
    d.save(image_path)
    
    # Generate options
    options = ['0', '1']
    correct_answer = str(output)
    random.shuffle(options)
    
    # Generate options text
    options_text = "Options:\n"
    for i, option in enumerate(options):
        options_text += f"{i+1}. {option}\n"
    
    # Construct the question text
    question = f"What is the output of the {gate_type} gate with inputs {', '.join(map(str, input_values))}?"
    if gate_type == 'NOT':
        question = f"What is the output of the {gate_type} gate with input {input_values[0]}?"
    
    return question, image_path, options_text, correct_answer

def create_pdf(questions_data):
    """Create a PDF with questions, images, options, and correct answers."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for i, (question, image_path, options_text, correct_answer) in enumerate(questions_data):
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 10, f'Question {i + 1}:', ln=True)
        
        # Add question text
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, question)
        
        # Add image
        pdf.ln(10)
        pdf.image(image_path, x=10, h=pdf.h / 4)  # Adjust height to fit the page
        
        # Add options
        pdf.ln(10)
        pdf.multi_cell(0, 10, options_text)
        
        # Add correct answer
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f'Correct Answer: {correct_answer}', ln=True)
    
    # Save the PDF
    pdf_output_path = 'C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\logic_questions.pdf'
    pdf.output(pdf_output_path)

def main():
    num_questions = int(input("How many questions would you like to generate? (Max 50) "))
    if num_questions > 50:
        num_questions = 50  # Limit the number of questions to 50
    
    questions_data = []
    
    for _ in range(num_questions):
        question, image_path, options, correct_answer = generate_simple_gate_operation_question()
        questions_data.append((question, image_path, options, correct_answer))
    
    create_pdf(questions_data)
    print(f"PDF created successfully at C:\\Users\\Lenovo\\OneDrive\\Desktop\\logicgates\\logic_questions.pdf")

if __name__ == "__main__":
    main()
