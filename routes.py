from flask import Flask, request, jsonify
from models import db, Issue
import os
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure database
database_url = os.environ.get('DATABASE_URL', 'sqlite:///issues.db')
# Render uses Postgres, which needs postgresql:// instead of postgres://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize database
db.init_app(app)

# Ensure tables are created
with app.app_context():
    db.create_all()

# Create an issue
@app.route('/issues', methods=['POST'])
def create_issue():
    try:
        data = request.get_json()
        if not data:
            logging.error("No data provided in request")
            return jsonify({"error": "No data provided"}), 400

        if 'customer_name' not in data or 'issue_description' not in data:
            logging.error("Missing required fields in request")
            return jsonify({"error": "Missing required fields"}), 400

        new_issue = Issue(
            customer_name=data['customer_name'],
            issue_description=data['issue_description']
        )
        db.session.add(new_issue)
        db.session.commit()
        
        logging.info(f"Issue created successfully for customer: {data['customer_name']}")
        return jsonify({
            "message": "Issue created successfully",
            "issue_id": new_issue.id
        }), 201

    except Exception as e:
        logging.error(f"Error creating issue: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to create issue"}), 500

# Get all issues
@app.route('/issues', methods=['GET'])
def get_issues():
    issues = Issue.query.all()
    return jsonify([{"id": i.id, "customer": i.customer_name, "status": i.status, "description": i.issue_description} for i in issues])

# Update issue status
@app.route('/issues/<int:issue_id>', methods=['PUT'])
def update_issue(issue_id):
    issue = Issue.query.get(issue_id)
    if not issue:
        return jsonify({"message": "Issue not found"}), 404
    data = request.json
    issue.status = data.get('status', issue.status)
    issue.resolution_notes = data.get('resolution_notes', issue.resolution_notes)
    db.session.commit()
    return jsonify({"message": "Issue updated successfully"})

# Delete an issue
@app.route('/issues/<int:issue_id>', methods=['DELETE'])
def delete_issue(issue_id):
    issue = Issue.query.get(issue_id)
    if not issue:
        return jsonify({"message": "Issue not found"}), 404
    db.session.delete(issue)
    db.session.commit()
    return jsonify({"message": "Issue deleted successfully"})

@app.route('/docs/<issue_type>', methods=['GET'])
def get_documentation(issue_type):
    try:
        file_path = f"documentation/{issue_type}.md"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                content = file.read()
            return jsonify({"documentation": content})
        else:
            return jsonify({"message": "Documentation not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/report/issues', methods=['GET'])
def generate_report():
    total_issues = Issue.query.count()
    open_issues = Issue.query.filter_by(status="Open").count()
    resolved_issues = Issue.query.filter_by(status="Resolved").count()

    report = {
        "total_issues": total_issues,
        "open_issues": open_issues,
        "resolved_issues": resolved_issues
    }
    return jsonify(report)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
