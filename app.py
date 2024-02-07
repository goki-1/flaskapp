from flask import Flask, request, render_template_string
import subprocess
import html
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

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

    # Read entries from existing XML file
    existing_entries = read_entries_from_xml("data.xml")

    # Fetch SVN entries from Jan 11, 2024, to HEAD
    present_entries = fetch_svn_entries("2024-02-06")

    # Combine existing and present entries
    all_entries = existing_entries + present_entries

    # Filter entries by voice_number
    filtered_entries = [entry for entry in all_entries if f"VOICE-{voice_number}" in entry['msg']]

    return render_template_string(HTML_TEMPLATE, entries=filtered_entries, voice_number=voice_number)

def read_entries_from_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    entries = []

    for logentry in root.findall('logentry'):
        entry = {
            'revision': logentry.get('revision'),
            'author': logentry.find('author').text,
            'date': logentry.find('date').text,
            'msg': logentry.find('msg').text,
            'link': f"https://svnmsp-subversion.polycom.com/viewvc/RepoSPIP?revision={logentry.get('revision')}&view=revision"
        }
        entries.append(entry)

    return entries

def fetch_svn_entries(start_date):
    svn_command = ['svn', 'log', '--xml', '-r', f'{start_date}:HEAD', '--username','gusingh','--password','Gokit0302@', 'https://subversion.polycom.com/SVN/RepoSPIP']
    svn_result = subprocess.run(svn_command, capture_output=True, text=True, encoding='utf-8')

    if svn_result.returncode == 0:
        svn_output = svn_result.stdout
        return parse_svn_output(svn_output)
    else:
        return []

def parse_svn_output(xml_output):
    root = ET.fromstring(xml_output)
    entries = []

    for logentry in root.findall('logentry'):
        revision = logentry.get('revision')
        author = logentry.find('author').text
        date_str = logentry.find('date').text
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
        msg = logentry.find('msg').text

        entry = {
            'revision': revision,
            'author': author,
            'date': formatted_date,
            'msg': msg,
            'link': f"https://svnmsp-subversion.polycom.com/viewvc/RepoSPIP?revision={revision}&view=revision"
        }
        entries.append(entry)

    return entries

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
