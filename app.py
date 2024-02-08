import xml.etree.ElementTree as ET

def check_revision_numbers(file_path):
    # Set to store encountered revision numbers
    encountered_revision_numbers = set()

    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Iterate through each logentry element in the XML file
    for logentry in root.findall('logentry'):
        # Extract the revision number
        revision = logentry.get('revision')
        # Add the revision number to the set
        encountered_revision_numbers.add(int(revision))

    # Check if all revision numbers from 1 to 294148 are present
    missing_revision_numbers = set(range(1, 294149)).difference(encountered_revision_numbers)

    if not missing_revision_numbers:
        print("All revision numbers from 1 to 294148 are present in the file.")
    else:
        print("Missing revision numbers:", missing_revision_numbers)

# File path of the combined XML file
file_path = 'combined_data.xml'

# Check if all revision numbers from 1 to 294148 are present
check_revision_numbers(file_path)

