from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

job_postings = []
resumes = []
candidates = []
skills = []
keywords = []

@app.route('/')
def root():
    return jsonify({"message": "API is running", "endpoints": [
        "/api/health",
        "/api/job-postings",
        "/api/resumes",
        "/api/resume-analysis",
        "/api/candidates",
        "/api/candidate-search"
    ]})

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/job-postings', methods=['POST'])
def create_job_posting():
    data = request.get_json() or {}
    if 'title' not in data or 'description' not in data or 'keywords' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    job_posting = {
        'id': uuid.uuid4().hex[:8],
        'title': data['title'],
        'description': data['description'],
        'keywords': data['keywords']
    }
    job_postings.append(job_posting)
    return jsonify(job_posting), 201

@app.route('/api/job-postings', methods=['GET'])
def get_job_postings():
    return jsonify(job_postings)

@app.route('/api/job-postings/<id>', methods=['GET'])
def get_job_posting(id):
    for job_posting in job_postings:
        if job_posting['id'] == id:
            return jsonify(job_posting)
    return jsonify({"error": "Job posting not found"}), 404

@app.route('/api/job-postings/<id>', methods=['PUT'])
def update_job_posting(id):
    data = request.get_json() or {}
    if 'title' not in data or 'description' not in data or 'keywords' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    for job_posting in job_postings:
        if job_posting['id'] == id:
            job_posting['title'] = data['title']
            job_posting['description'] = data['description']
            job_posting['keywords'] = data['keywords']
            return jsonify(job_posting)
    return jsonify({"error": "Job posting not found"}), 404

@app.route('/api/job-postings/<id>', methods=['DELETE'])
def delete_job_posting(id):
    for job_posting in job_postings:
        if job_posting['id'] == id:
            job_postings.remove(job_posting)
            return jsonify({"message": "Job posting deleted"})
    return jsonify({"error": "Job posting not found"}), 404

@app.route('/api/resumes', methods=['POST'])
def create_resume():
    data = request.get_json() or {}
    if 'file' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    resume = {
        'id': uuid.uuid4().hex[:8],
        'file': data['file']
    }
    resumes.append(resume)
    return jsonify(resume), 201

@app.route('/api/resumes', methods=['GET'])
def get_resumes():
    return jsonify(resumes)

@app.route('/api/resumes/<id>', methods=['GET'])
def get_resume(id):
    for resume in resumes:
        if resume['id'] == id:
            return jsonify(resume)
    return jsonify({"error": "Resume not found"}), 404

@app.route('/api/resume-analysis', methods=['POST'])
def analyze_resume():
    data = request.get_json() or {}
    if 'resume_id' not in data or 'job_posting_id' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    resume = next((r for r in resumes if r['id'] == data['resume_id']), None)
    job_posting = next((jp for jp in job_postings if jp['id'] == data['job_posting_id']), None)
    if resume is None or job_posting is None:
        return jsonify({"error": "Resume or job posting not found"}), 404
    # Analyze resume against job posting
    analysis = {
        'match_score': 0.5,  # placeholder for actual analysis
        'resume_id': resume['id'],
        'job_posting_id': job_posting['id']
    }
    return jsonify(analysis), 200

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    return jsonify(candidates)

@app.route('/api/candidate-search', methods=['POST'])
def search_candidates():
    data = request.get_json() or {}
    if 'keywords' not in data or 'skills' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    # Search for candidates using keywords and skills
    results = []
    for candidate in candidates:
        if any(keyword in candidate['keywords'] for keyword in data['keywords']) and any(skill in candidate['skills'] for skill in data['skills']):
            results.append(candidate)
    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)