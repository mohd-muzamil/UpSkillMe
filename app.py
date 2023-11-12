from flask import Flask, render_template, request, jsonify
import random
import string
from werkzeug.utils import secure_filename  # Add this import for secure filename handling
from PyPDF2 import PdfReader
import re
import pandas as pd
import os
from langchain.llms import OpenAI
from langchain import PromptTemplate
from langchain import LLMChain
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain import LLMChain
from langchain.chains import LLMChain

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'  # Update this with the actual path
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
RESUME_NAME = 'Profile.pdf'  # Update this with the actual path
JOSB_NAME = 'jobs.csv'  # Update this with the actual path
SKILLS_NAME = 'skills.csv'  # Update this with the actual path
GAPS_NAME = 'gaps.csv'  # Update this with the actual path
# path to save AI results
CHATGPTRESULTS_FOLDER = './chatgpt'  # Update this with the actual path

########################################
os.environ['OPENAI_API_KEY'] = "API_Key_here"
llm = OpenAI(temperature=0.9)  # model_name="text-davinci-003"
template = """Question: {question}

Let's think step by step.

Answer: """

prompt = PromptTemplate(template=template, input_variables=["question"])

llm_chain = LLMChain(prompt=prompt, llm=llm)

# question = "Can Barack Obama have a conversation with George Washington?"

# print(llm_chain.run(question))

def read_pdf(file):
    pdf_text = ""
    with open(file, 'rb') as f:
        pdf = PdfReader(f)
        for page in pdf.pages:
            pdf_text += page.extract_text()
    return pdf_text

def my_skills(text):
  llm_chain = LLMChain(prompt=prompt, llm=llm)

  question = "Based on my following paragraph of my CV, what are my skills. make a bullet point summary" + text

  my_skills = llm_chain.run(question)
  # print(type(my_skills))
  # my_skills = my_skills.replace('•', '').replace('-', '').strip()
  # print(my_skills)
  result_string = '\n'.join(line for line in my_skills.splitlines() if line.strip())
  lines = result_string.splitlines()

  # Create a DataFrame from the list of lines
  df = pd.DataFrame({'skills': lines})
  df = df.drop(0)
  df = df.reset_index(drop=True)
  # print(df)
  return df , my_skills

def top_3_jobs(my_skills ):
  question = "Based on the following list of my skills can you suggest me top 3 most suaitale jobs" +\
             "____" + my_skills + "____"+\
             "addistion to that for each job give me a short explanation for that in front of a colon (:) "+\
             "addition to that mark the most fitting job to me by a 1 in front of a star(*) "
  jobs = llm_chain.run(question)

# Split the text into lines
  lines = jobs.strip().split('\n')

  # Initialize lists to store data
  titles = []
  explanations = []
  contains_star = []

  # Parse each line
  for line in lines:
      # Split the line into index, content, and star
      content = line.split('.')[1].split(':')
      titles.append( content[0].replace('*', '') )
      contains_star.append('1' if '*' in content[0] else '0')
      explanations.append(content[1])

  # Create a DataFrame
  df = pd.DataFrame({
      'Title': titles,
      'Explanation': explanations,
      'ContainsStar': contains_star
  })

  return df , jobs


def gaps(dream_job , my_skills):
  # question = "My dream job is ___" + dream_job +\
  #            "___ Based on the following list of my skills what are the gaps and skills I need to learn?"+\
  #            " Make a bullet point of them in order of the most impoertant at top. My current skills are ___" +\
  #             my_skills + " ___"+"just make sure that you are giving the information to me by the following format."+\
  #             "a title for each one , in front of that put a colon(:)  and write the rest in front of that"

  question = "My dream job is ___" + dream_job + "___"+\
             "And these are my current skills: ___" + my_skills + "____" +\
             "Based on the provided infromation make a bullet point list of mising skills that I must learn "


  gaps = llm_chain.run(question)
  result_string = '\n'.join(line for line in gaps.splitlines() if line.strip())
  lines = result_string.splitlines()

  # Create a DataFrame from the list of lines
  df = pd.DataFrame({'gaps': lines})
  # df = df.drop(0)
  # df = df.reset_index(drop=True)
  return df , gaps


def explanation_for_each_gap(gap):
  question = " please provide me an explanation of what is " +gap +" ? just in 1 line."
  explanation = llm_chain.run(question)
#   print(explanation)
  return explanation

########################################

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit on file size
app.config['RESUME_NAME'] = RESUME_NAME
app.config['JOBS_NAME'] = JOSB_NAME
app.config['SKILLS_NAME'] = SKILLS_NAME
app.config['GAPS_NAME'] = GAPS_NAME
app.config['CHATGPTRESULTS_FOLDER'] = CHATGPTRESULTS_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pre_process(text):
    # lowercase
    text=text.lower()
    #remove tags
    text=re.sub("<!--?.*?-->","",text)
    # remove special characters and digits
    text=re.sub("(\\d|\\W)+"," ",text)
    return text

def getMatchedJobsDataFrame(skills):
    jobs_df , _ = top_3_jobs(skills)
    return jobs_df

def getUpgradeSkillsDataFrame(gaps_df):
    return gaps_df
    
def getGapExplanationDataFrame(gap):
    return explanation_for_each_gap(gap)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare_resumes():
    # Get the uploaded file
    resume_file = request.files.get('resume')
    job_description_text = request.form.get('jobDescriptionText', '')
    # resume_text = request.form.get('resumeText', '')

    # Check if the file is present and has an allowed extension
    if resume_file and resume_file.filename.lower().endswith(('.pdf', '.txt')):

        # Save the file to the specified folder
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(resume_file.filename))
        resume_file.save(uploaded_file_path)

        # Read the contents of the PDF file
        resume_text_from_file = read_pdf(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(resume_file.filename)))
        # resume_text_from_file = read_pdf(resume_file.filename)
        # print(resume_text_from_file)
        resume_text_from_file = pre_process(resume_text_from_file)

        # Further processing logic...
        # Implement your keyword extraction and AI logic here
        dream_job = job_description_text
        skills_df , skills = my_skills(resume_text_from_file)
        jobs_df , _ = top_3_jobs(skills)
        gaps_df , _ = gaps(dream_job , skills)
        for gap in gaps_df['gaps']:
            explanation = explanation_for_each_gap(gap)
            gaps_df['explanation'] = explanation
        
        # jobs_df.to_csv(os.path.join(app.config['CHATGPTRESULTS_FOLDER'], app.config['JOBS_NAME']), index=False)
        jobs_df.to_csv(os.path.join('./chatgpt', app.config['JOBS_NAME']), index=False)
        # skills_df.to_csv(os.path.join(app.config['CHATGPTRESULTS_FOLDER'], app.config['SKILLS_NAME']), index=False)        
        skills_df.to_csv(os.path.join('./chatgpt', app.config['SKILLS_NAME']), index=False)
        # gaps_df.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], app.config['GAPS_NAME']), index=False)
        gaps_df.to_csv(os.path.join('./chatgpt', app.config['GAPS_NAME']), index=False)


        response_data = {
            'recommendations': jobs_df,
        }

        # Delete the temporary file after processing
        # os.remove(uploaded_file_path)

        # return jsonify(response_data)
        return None
    else:
        return jsonify({'error': 'Invalid file format. Please upload a PDF or TXT file.'}), 400


@app.route('/matchedJobs', methods=['GET'])
def getMatchedJobs():
    # Create a sample DataFrame (replace this with your actual data)
    df = pd.read_csv(os.path.join(app.config['CHATGPTRESULTS_FOLDER'], app.config['JOBS_NAME']))
    # Convert DataFrame to HTML table
    table_html = df.to_html(index=False)
    # Render HTML template with the table content
    return table_html

@app.route('/upgradeSkills', methods=['GET'])
def getUpgradeSkills():
    df = pd.read_csv(os.path.join(app.config['CHATGPTRESULTS_FOLDER'], app.config['SKILLS_NAME']))
    # Convert DataFrame to HTML table
    table_html = df.to_html(index=False)

    # Render HTML template with the table content
    return table_html

@app.route('/explainGaps', methods=['GET'])
def explainGaps():
    # Create a sample DataFrame (replace this with your actual data)
    gaps_df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], app.config['GAPS_NAME']))
    explain_gaps_df = getGapExplanationDataFrame(gaps_df['gaps'][0]).copy()
    # Convert DataFrame to HTML table
    table_html = explain_gaps_df.to_html(index=False)
    # Render HTML template with the table content
    return table_html


if __name__ == '__main__':
    app.run(debug=True)

