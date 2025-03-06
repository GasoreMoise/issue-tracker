from flask import Flask, jsonify, request
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/log_test')
def test_logging():
    logging.info("Test log entry added.")
    return jsonify({"message": "Log entry created"})

@app.route('/issues', methods=['POST'])
def create_issue():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Log the incoming request
        logging.info(f"Received issue creation request: {data}")
        
        # Here you would typically create the issue
        # new_issue = Issue(customer_name=data['customer_name'], 
        #                  issue_description=data['issue_description'])
        
        return jsonify({"message": "Issue created successfully"}), 201
        
    except Exception as e:
        logging.error(f"Error creating issue: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
