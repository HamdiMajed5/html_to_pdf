from flask import Flask, request, send_file, jsonify
from weasyprint import HTML
import io
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/convert', methods=['POST'])
def convert_html_to_pdf():
    """
    Convert HTML to PDF
    Accepts: HTML file upload or HTML string in request body
    Returns: PDF file
    """
    try:
        # Check if HTML file was uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400

            if not file.filename.endswith('.html'):
                return jsonify({"error": "File must be HTML"}), 400

            html_content = file.read().decode('utf-8')

        # Check if HTML content was sent as form data
        elif 'html' in request.form:
            html_content = request.form['html']

        # Check if HTML content was sent as JSON
        elif request.is_json:
            data = request.get_json()
            html_content = data.get('html', '')
            if not html_content:
                return jsonify({"error": "No HTML content provided"}), 400

        else:
            return jsonify({"error": "No HTML content provided. Send as file, form data, or JSON"}), 400

        # Convert HTML to PDF
        pdf_buffer = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)

        # Return PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='document.pdf'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/convert-url', methods=['POST'])
def convert_url_to_pdf():
    """
    Convert HTML from URL to PDF
    Expects JSON: {"url": "https://example.com"}
    Returns: PDF file
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400

        data = request.get_json()
        url = data.get('url', '')

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        # Convert URL to PDF
        pdf_buffer = io.BytesIO()
        HTML(url=url).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='document.pdf'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413


if __name__ == '__main__':
    # Run on all interfaces, port 5000
    app.run(host='0.0.0.0', port=5000, debug=False)