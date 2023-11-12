from flask import Flask, render_template, request, jsonify
import random
import string


app = Flask(__name__)

def extract_keywords(text_length=20):
    recommendations = [' '.join(random.choices(string.ascii_lowercase, k=random.randint(5, 15))) for _ in range(3)]
    return recommendations

def generate_skill_gap_recommendations(resume_keywords, job_description_keywords):
    recommendations = [' '.join(random.choices(string.ascii_lowercase, k=random.randint(5, 15))) for _ in range(3)]
    return recommendations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare_resumes():
    data = request.get_json()
    resume_text = data.get('resumeText', '')
    job_description_text = data.get('jobDescriptionText', '')
    print('resume_text', resume_text)
    print('job_description_text', job_description_text)
    # Implement your keyword extraction and AI logic here
    # For simplicity, let's assume these functions exist:
    resume_keywords = extract_keywords(resume_text)
    job_description_keywords = extract_keywords(job_description_text)
    skill_gap_recommendations = generate_skill_gap_recommendations(resume_keywords, job_description_keywords)

    response_data = {
        'resumeKeywords': resume_keywords,
        'jobDescriptionKeywords': job_description_keywords,
        'skillGapRecommendations': skill_gap_recommendations,
    }
    print('response_data', response_data)
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
