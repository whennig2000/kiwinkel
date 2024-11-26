from flask import Flask, render_template, request, jsonify
import subprocess
import random
import os

app = Flask(__name__)

FAQ_FOLDER = 'faqs'

if not os.path.exists(FAQ_FOLDER):
    os.makedirs(FAQ_FOLDER)

FAQ_FILES = []

PRINCIPLES_FOLDER = 'principles'

PRINCIPLES_FILES = []

greetings = [
    "Welcome Data-Pioneer!",
    "Hi, nice to datalad get to know you!",
    "Hello there, good data to you!",
    "FBI OPEN UP YOUR FILES!",
    "DataLad us become friends!",
    "Come over to the DataLad side ..."
]

# read faq
def load_faqs():
    faqs = []
    for faq_file in FAQ_FILES:
        file_path = os.path.join(FAQ_FOLDER, faq_file)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    question = lines[0].strip()
                    answer = lines[1].strip()
                    faqs.append({'question': question, 'answer': answer})
    return faqs

# display faq
@app.route('/get_faqs', methods=['GET'])
def get_faqs():
    for e in os.listdir(FAQ_FOLDER):
        if e not in FAQ_FILES:
            FAQ_FILES.append(e)
    faqs = load_faqs()
    return jsonify(faqs)

def load_principles():
    principles = []
    for principles_file in PRINCIPLES_FILES:
        file_path = os.path.join(PRINCIPLES_FOLDER, principles_file)
        if os.path.exists(file_path):
            principles.append(file_path)
    return jsonify(principles)

# display principles
@app.route('/get_principles', methods=['GET'])
def get_principles():
    for e in os.listdir(PRINCIPLES_FOLDER):
        if e not in PRINCIPLES_FILES:
            PRINCIPLES_FILES.append(e)
    ps = load_principles()
    # print(ps)
    return ps

# add question to faq
@app.route('/submit_question', methods=['POST'])
def submit_question():
    data = request.get_json()
    new_question = data.get('question')

    if not new_question:
        return jsonify({"error": "No question submitted."}), 400

    # create new txt file
    new_faq_file = os.path.join(FAQ_FOLDER, f"faq_{len(FAQ_FILES) + 1}.txt")
    with open(new_faq_file, 'w', encoding='utf-8') as f:
        f.write(f"{new_question}\nThis question has not yet been answered.\n")  # default answer
    
    FAQ_FILES.append(f"faq_{len(FAQ_FILES)}.txt")  # append to faqs
    return jsonify({"success": "Your question has been saved successfully."}), 200

# function to run datalad commands
def run_datalad_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def get_datalad_files():
    datalad_dir = os.path.join(os.getcwd(), 'datalad-resources')
    result = subprocess.run(
        ['ls', datalad_dir],
        capture_output=True, text=True, check=True
    )
    file_list = result.stdout.strip().split('\n')
    return file_list

@app.route('/')
def index():
    # select random welcome message
    greeting = random.choice(greetings)
    # get datalad resources
    files = get_datalad_files()
    return render_template('index.html', greeting=greeting, files=files)

@app.route('/datalad-command', methods=['POST'])
def datalad_command():
    command = request.json.get('command')
    output = run_datalad_command(command.split())
    return jsonify({"output": output})

@app.route('/generate_command', methods=['POST'])
def generate_command():
    # get data from frontend
    action = request.form.get('action')
    options = request.form.getlist('options')

    # create datalad command
    command = f"datalad {action} " + " ".join(options)

    # execute command
    dataset_path = request.form.get('dataset_path')
    if dataset_path:
        try:
            subprocess.run(command, cwd=dataset_path, check=True, shell=True)
            return jsonify({"command": command, "status": "success"})
        except subprocess.CalledProcessError as e:
            return jsonify({"command": command, "status": "error", "message": str(e)})

    return jsonify({"command": command, "status": "ready"})

if __name__ == '__main__':
    app.run(debug=True)
