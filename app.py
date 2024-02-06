from flask import Flask, request, render_template_string
import subprocess
import html
from datetime import datetime

app = Flask(__name__)

# HTML template for the search form and results display
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VOICE Number Search</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .entry { margin-bottom: 20px; }
        .entry p { margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Search SVN Log by VOICE Number</h1>
    <form action="/search" method="get">
        <label for="voice_number">Enter VOICE Number:</label>
        <input type="text" id="voice_number" name="voice_number" required>
        <button type="submit">Search</button>
    </form>
    {% if entries %}
        <h2>Results for VOICE-{{ voice_number }}</h2>
        {% for entry in entries %}
            <div class='entry'>
                <p><strong>Revision:</strong> {{ entry['revision'] }}</p>
                <p><strong>Author:</strong> {{ entry['author'] }}</p>
                <p><strong>Date:</strong> {{ entry['date'] }}</p>
                <p><a href="{{ entry['link'] }}" target="_blank">Revision Link</a></p>
                <p><strong>Message:</strong> {{ entry['msg'] }}</p>
            </div>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    # Display the search form
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['GET'])
def search():
    voice_number = request.args.get('voice_number', '')
    svn_command = ['svn', 'log', '--xml', '-r', '{2021-11-10}:HEAD', 'https://subversion.polycom.com/SVN/RepoSPIP']
    svn_result = subprocess.run(svn_command, capture_output=True, text=True, encoding='utf-8')

    if svn_result.returncode == 0:
        svn_output = svn_result.stdout
        # Parse the XML output and filter the entries by voice_number
        entries = parse_svn_output(svn_output, voice_number)
        return render_template_string(HTML_TEMPLATE, entries=entries, voice_number=voice_number)
    else:
        # Handle errors
        return "Error running SVN command"

import xml.etree.ElementTree as ET

def parse_svn_output(xml_output, voice_number):
    # Parse the XML output
    root = ET.fromstring(xml_output)
    
    # List to store entries
    entries = []

    # Iterate through each logentry element
    for logentry in root.findall('logentry'):
        revision = logentry.get('revision')
        author = logentry.find('author').text
        date_str = logentry.find('date').text
        
        # Parse the date string into a datetime object
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        
        # Format the date as a readable string
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
        msg = logentry.find('msg').text

        # Check if the message contains the VOICE number
        if f"VOICE-{voice_number}" in msg:
            # Create a dictionary for the entry
            entry = {
                'revision': revision,
                'author': author,
                'date': formatted_date,
                'msg': msg,
                'link': f'https://svnmsp-subversion.polycom.com/viewvc/RepoSPIP?revision={revision}&view=revision'
            }
            # Append the entry to the list
            entries.append(entry)
    
    return entries


if __name__ == '__main__':
    app.run(debug=True)
