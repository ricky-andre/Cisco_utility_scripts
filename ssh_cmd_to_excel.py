import re
import time
from openpyxl import Workbook
from srg_access import ssh_manager

store_dir = "C:/path_to_excel_output/"
# The file is written with the following format:
# System Name: <device name>      IPv4 Address  <ip address>", line)
routers_list_file = 'C:/path_to_router_list_file'
mgm_ip_router = {}
routersList = []

# save the following list of commands on an excel file. Commands can be router specific
routersList = { "router_1" : ["show ip ospf 1 neighbor",
                              "show ip int brief"],
               "router_2" : ["show ip ospf 2 neighbor",
                             "show ip int brief"]}

with open(routers_list_file) as routers:
    for line in routers:
        if re.search("^#", line):
            continue
        value = re.search("System Name:\s+(.*?)\s+IPv4 Address:\s+(\d+\.\d+\.\d+\.\d+)", line)
        if (value):
            mgm_ip_router[value.group(1)]=value.group(2)

# use the telnet/ssh library in:
# https://github.com/ricky-andre/ssh_telnet_Cisco
ssh = ssh_manager('connection_profile')
print ("\nConnected to ssh proxy\n")

clock_time = time.strftime("%H %M %S")
day_time = time.strftime("a%Y m%m g%d")
# let's also store date and time on the file name !!
target = Workbook()
sheet = target.active
row_counter = 1
separator = "  "

for router in routersList:
    print ("Connecting to \""+router+"\", mgmt ip: "+mgm_ip_router[router]+" ... ")
    if not ssh.node_login(router,mgm_ip_router[router]):
        continue
    ssh.run_cmd('terminal length 0')
    for command in routersList[router]:
        print(" executing \""+command+"\" on "+router+" ...", end="")
        try:
            lines_out = ssh.run_cmd(command).splitlines()
            # let's print the output, row by row ... in the first column write the router's name,
            #  then the line. In case a separator is defined, also split the line by the separator,
            #  and put every non-empty value in a new column
            if not len(separator):
                for line in lines_out:
                    sheet['A'+str(row_counter)].value = router
                    sheet['B'+str(row_counter)].value = command
                    sheet['C'+str(row_counter)].value = line
                    row_counter += 1
            else:
                for line in lines_out:
                    sheet['A'+str(row_counter)].value = router
                    sheet['B'+str(row_counter)].value = command
                    all_words = line.split(separator)
                    col_counter=0
                    for word in all_words:
                        if len(word.strip()):
                            sheet[chr(ord('C')+col_counter)+str(row_counter)].value = word.strip()
                            col_counter += 1
                    row_counter += 1
            print (" done!")
        except:
            print (" timed out command, raise the timeout value !\n")
    
    print ("Finished commands on "+router+"\n")
    ssh.node_logout()

target.save(store_dir+"Cmd_out__"+day_time+"__"+clock_time+".xlsx")
ssh.close()
