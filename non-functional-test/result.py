import configparser

# Define the properties file path
properties_file = 'deployment.properties'
properties_file1 = 'robustness.properties'
properties_file2 = 'characteristics.properties'

# Create a ConfigParser object and read the properties file
config = configparser.ConfigParser()
config.read(properties_file)
config.read(properties_file1)
config.read(properties_file2)
# Define the HTML report filename
html_report_filename = 'my_report.html'

# Open the HTML report file for writing
with open(html_report_filename, 'w') as f:

    # Write the HTML header
    f.write('<head>')
    f.write('<html><title>My Report</title>')
    f.write('<link rel="stylesheet" href="mystyle.css">')
    f.write('</head>')
    f.write('<body style="background-color: #FBF8BE;">')
    f.write('<div class="header">')
    f.write('<h3><a href="https://confluence-oss.seli.wh.rnd.internal.ericsson.com/display/IDUN/Non-Functional+Test+cases+execution+Script+-+Coverage">Test Coverage</a></h3>')
    f.write('<h3><a href="https://confluence-oss.seli.wh.rnd.internal.ericsson.com/display/IDUN/How+to+Use+Non-Functional+Test+Cases+Execution+Script">Test Configuration</a></h3>')
    f.write('</div>')
    # Write the table header
    f.write('<h1>Deployment Testing Result</h1>')
    f.write('<table border="1" bgcolor="#E7E8D1">')
    
    # Loop through the properties and write each key-value pair as a table row
    f.write(f'<tr style="background-color: #A7BEAE; font-weight: bold;"><td>TEST CASE NAME</td><td>STATUS</td></tr>')
    for key, value in config.items('Deployment'):
        f.write(f'<tr><td>{key}</td><td>{value}</td></tr>')
    
    # Write the table footer
    f.write('</table>')
        # Write the table header
    f.write('<h1>Robustness Testing Result</h1>')
    f.write('<table border="1" bgcolor="#E7E8D1">')
    
    # Loop through the properties and write each key-value pair as a table row
    f.write(f'<tr style="background-color: #A7BEAE; font-weight: bold;"><td>TEST CASE NAME</td><td>STATUS</td></tr>')
    for key, value in config.items('Robustness'):
        f.write(f'<tr><td>{key}</td><td>{value}</td></tr>')
    
    # Write the table footer
    f.write('</table>')
    
    f.write('<h1>Characteristics Testing Result</h1>')
    f.write('<table border="1" bgcolor="#E7E8D1">')
    
    # Loop through the properties and write each key-value pair as a table row
    f.write(f'<tr style="background-color: #A7BEAE; font-weight: bold;"><td>TEST CASE NAME</td><td>STATUS</td></tr>')
    for key, value in config.items('Characteristics'):
        f.write(f'<tr><td>{key}</td><td>{value}</td></tr>')
    
    # Write the table footer
    f.write('</table>')
    
    # Write the HTML footer
    f.write('</body></html>')
