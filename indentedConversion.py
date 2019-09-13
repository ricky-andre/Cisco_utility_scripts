import re
import os.path
import csv
from xlsxwriter.workbook import Workbook

# the present script is useful to convert configuration files into a slightly different
# format, and use excel to filter Cisco file configuration, to easily retrieve the
# configurations you are interested in.
# For example the following interface configuration:

# interface GigabitEthernet1/1/3
#  description <description>
#  switchport
#  switchport trunk encapsulation dot1q
#  switchport mode trunk
#  channel-group 103 mode passive
#
#  ... will be converted into the following one:
#
#  6500 core VSS    interface GigabitEthernet1/1/3                    
#  6500 core VSS    interface GigabitEthernet1/1/3    description <description>
#  6500 core VSS    interface GigabitEthernet1/1/3    switchport                
#  6500 core VSS    interface GigabitEthernet1/1/3    switchport trunk encapsulation dot1q                
#  6500 core VSS    interface GigabitEthernet1/1/3    switchport mode trunk                
#  6500 core VSS    interface GigabitEthernet1/1/3    channel-group 103 mode passive                
#  6500 core VSS    !           
#
# of course it works with IOS, NX-OS, IOS-XR since it is only based on the way configuration files
# are saved and their indentation.

# files to be converted
start_dir = "C:/path_to_config_files_directory"
output_file = start_dir + "indentedFiles.tsv"

# regular expression to select files
file_filter = "^rou_.*\.txt$"
#file_filter = ".txt"
#file_filter = ".cfg"
tab = "\t"

print (output_file)
out_file = open(output_file, "w")
out_file.write("Node\tCommand\tCommand\tCommand\tCommand\tCommand")

for name in os.listdir(start_dir):
    file_path = start_dir+name
    if os.path.isfile(file_path):
        if re.search(file_filter,name):
            file = open(file_path,"r")
            print ("Opening file \""+name+"\"")

            value = re.search("^(.*)\..*$",name)
            first_col = value.group(1)+tab

            parents = []
            num_spaces = []
            last_spaces = 0
            spaces = 0
            last_line = ""

            # reading file line by line
            for line in file:
                if re.match("^\s+$",line):
                    out_file.write(line)
                    continue
    
                value = re.match("^(\s+)",line)
                # setting the number of spaces in the new line
                if value and len(value.group(1)):
                    spaces = len(value.group(1))
                else:
                    spaces = 0
                    
                if (spaces):
                    if (spaces>last_spaces):
                        # print ("Spaces "+str(spaces)+" last spaces "+str(last_spaces))
                        # print ("Found new child "+line+" parent "+last_line)
                        parents.append(last_line.strip())
                        num_spaces.append(spaces)
                        out_file.write(first_col+tab.join(parents)+tab+line.strip()+"\n")
                    elif (spaces==last_spaces):
                        out_file.write(first_col+tab.join(parents)+tab+line.strip()+"\n")
                    else:
                        # one other 'exception' here to be managed ... on Nexus devices we can have
                        # the following, with no use of "!" to fall back on the previous parent ...
                        while (num_spaces[len(num_spaces)-1] > spaces):
                            parents.pop()
                            num_spaces.pop()
                            out_file.write(first_col+tab.join(parents)+"\n")
                        out_file.write(first_col+tab.join(parents)+tab+line.strip()+"\n")
                            # out_file.write(first_col+tab.join(parents)+tab+line.strip()+"\n")
                elif re.search("^!",line):
                    spaces = 0
                    while (len(parents)):
                        parents.pop()
                        num_spaces.pop()
                        if not (len(parents)):
                            out_file.write(first_col+line.strip()+"\n")
                        else:
                            out_file.write(first_col+tab.join(parents)+tab+line.strip()+"\n")
                        line = "!"
                # here we are in the case of a structure with children or nephews that is
                # ended disruptively with the beginning of a new structure ...
                else:
                    # in firewall's ASA configurations, there is the possibility of having a new
                    # parent starting WITHOUT the "!" line ... you can have something like this
                    if (len(parents)):
                        while (len(parents)):
                            parents.pop()
                            num_spaces.pop()
                            out_file.write(first_col+tab.join(parents)+"\n")
                    out_file.write(first_col+line)

                last_line = line
                last_spaces = spaces

out_file.close()

# Creating the excel file ...
tsv_file = start_dir+'indentedFiles.tsv'
xlsx_file = start_dir+'indentedFiles.xlsx'

# Create an XlsxWriter workbook object and add a worksheet.
workbook = Workbook(xlsx_file)
worksheet = workbook.add_worksheet()

# Create a TSV file reader.
tsv_reader = csv.reader(open(tsv_file, 'r'), delimiter='\t')

# Read the row data from the TSV file and write it to the XLSX file.
for row_index, array_data in enumerate(tsv_reader):
    worksheet.write_row(row_index, 0, array_data)

# Close the XLSX file.
workbook.close()
