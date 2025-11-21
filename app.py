from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Skyflow API configuration
SKYFLOW_URL = "https://a370a9658141.vault.skyflowapis-preview.com/v1/detect/deidentify/string"
SKYFLOW_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2MiOiJ1ODE3NDBkMzIxNWU0NTgzYjI2NTgxZGQ4MzU4M2ZhNiIsImF1ZCI6Imh0dHBzOi8vbWFuYWdlLnNreWZsb3dhcGlzLXByZXZpZXcuY29tIiwiZXhwIjoxNzYzODQyMTI2LCJpYXQiOjE3NjM3NTU3MjYsImlzcyI6InNhLWF1dGhAbWFuYWdlLnNreWZsb3dhcGlzLXByZXZpZXcuY29tIiwianRpIjoiZGE0MTg4YzkyZmY4NGNjNWJlMDI0ZThlYTc5NDk5MzkiLCJzdWIiOiJwOTBiZDM5YjQ5YjQ0OTg2YWI4MGIzNTMxOTcyNTBmYyJ9.T-XWBw2IVy7JHgzy7IktTP9m5Xkkxmojiz9mzumOq4Y3WROor1qSvH5p-YuheBSWa2J8f3bNHsuNEe0NHSegaVFj_rtYZvsWg9FpcIgSt9qmJyRrzgzFuzot2jYI5FvhEnnFtJkbeT5vZ7So0Jpl2nJsZorNoZjrgAd8aauOuG79wPgPuB3WwxNW_6hmHywnIFEdoo0tc1wBxseJtS_SrmhLDcdfP5r25R55KbOp_GrMm4XI1X37KIsrfl12buZxMR_DBzrx8UAnMXJu-PTQqlWDqfARHBvzDTJxNpmvreAp_zz6zVTuG8heGoSZZ5tUq1l3YnzyG6PdYBA2nt8cOQ"
VAULT_ID = "fe079a24274f448fa5fd4c471a07d08a"


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/deidentify', methods=['POST'])
def deidentify():
    """De-identify medical information using Skyflow"""
    try:
        data = request.get_json()
        medical_text = data.get('text', '')
        
        if not medical_text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Call Skyflow API
        response = requests.post(
            SKYFLOW_URL,
            headers={
                "Authorization": f"Bearer {SKYFLOW_TOKEN}"
            },
            json={
                "text": medical_text,
                "vault_id": VAULT_ID,
                "entity_types": [
                    "name",
                    "phone_number",
                    "account_number",
                    "ssn",
                    "dob",
                    "location_address_street",
                    "healthcare_number"
                ],
                "token_type": {
                    "default": "vault_token"
                }
            },
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'error': f'Skyflow API error: {response.status_code}',
                'details': response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

