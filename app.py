import xml.etree.ElementTree as ET

def combine_xml_files(input_files, output_file):
    combined_entries = {}  # Using a dictionary to store unique entries based on revision number

    for input_file in input_files:
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Iterate through each logentry element in the current XML file
        for logentry in root.findall('logentry'):
            # Extract revision number
            revision = logentry.get('revision')
            # Check if the revision number is not already in the dictionary
            if revision not in combined_entries:
                # Add the logentry to the dictionary using revision number as key
                combined_entries[revision] = logentry
                # Append the logentry to the output XML file
                output_root.append(logentry)

    # Create a new XML tree with the combined entries
    combined_tree = ET.ElementTree(output_root)
    combined_tree.write(output_file)

# Input file names
input_files = ['data.xml', 'data1.xml', 'data2.xml']
# Output file name
output_file = 'combined_data.xml'

# Create the root element for the output XML file
output_root = ET.Element("log")

# Combine XML files and remove duplicates based on revision number
combine_xml_files(input_files, output_file)

print("Combined data written to", output_file)
