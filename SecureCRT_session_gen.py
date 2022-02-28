import re
import os.path

script_dir = "S:\"Script Filename V2\"=${VDS_CONFIG_PATH}\Sessions\\"
secureCRT_dir = "C:/Users/601787621/AppData/Local/SecureCRT/Sessions/"

# put the secureCRT files in the following directories, if the directories
# do not exist, they will be created as listed
secure_CRT_dir = [secureCRT_dir+"customer-1/",
                  secureCRT_dir+"customer-2/",
                  secureCRT_dir+"customer-3/",
                  secureCRT_dir+"customer-4 vpn/core/",
                  secureCRT_dir+"customer-4 vpn/access/",
                  secureCRT_dir+"customer-4 vpn/router/"]

# read the router/switch list from the following files. Files can potentially
# be the same, router's names and classification will be performed using the
# regular expressions later defined. Files are written using the following line template:
# System Name:  <device name>       IPv4 Address: <device ip address>
rou_list_files = ['C:/Users/601787621/Documents/customer-1/customer-1 Router List.txt',
                'C:/Users/601787621/Documents/customer-2/Router List customer-2.txt',
                'C:/Users/601787621/Documents/customer-3/Router List customer-3.txt',
                'C:/Users/601787621/Documents/customer-4/Router List customer-4.txt',
                'C:/Users/601787621/Documents/customer-4/Router List customer-4.txt',
                'C:/Users/601787621/Documents/customer-4/Router List customer-4.txt']

# from the mother directory, based on the following regular expressions, put the files in the
# directories defined later. This means for example that for customer-1 routers, in case the name
# is "rou_OoB", the secureCRT files will be put inside the rou_OoB directory, which will
# result in a subfolder inside SecureCRT.
rou_list_regexp = [["router_OoB_","router_north","rou_south","sw_core","sw_access","sw_north","sw_south","sw_east",
                    "sw_west","sw_ring7","sw_ring8","sw_ring9","sw_ring10",".*"],
                   ["^(RS|stoc)","^SS",".*"],
                   ".*",
                   "^(AGG|CORE|ACCESS)",
                   "^SWI",
                   "^(ROU|ASR|CORE)"]

# based on the list of regexp of the previous array, put the files in the following sub-directories
rou_list_dirs = [["router_OoB_","router_north","rou_south","sw_core","sw_access","sw_north","sw_south","sw_east",
                    "sw_west","sw_ring7","sw_ring8","sw_ring9","sw_ring10",".*"],
                 ["router/","switch/","./"],
                 "./",
                 "./",
                 "./",
                 "./"]

# template login scripts depends on the directories, this string will be referred on the secureCRT files
login_script = [script_dir+"login_script.vbs\n",
                script_dir+"login_script_customer-2.vbs\n",
                script_dir+"login_script_customer-3.vbs\n",
                script_dir+"login_script_customer-4_vpn_nexus.vbs\n",
                script_dir+"login_script_customer-4_vpn_nexus.vbs\n",
                script_dir+"login_script_customer-4_vpn_router.vbs\n"]

# secureCRT ini template files
ini_templates = [secureCRT_dir+"CRT_customer-1_ini_template.txt",
                 secureCRT_dir+"CRT_customer-2_ini_template.txt",
                 secureCRT_dir+"CRT_customer-3_ini_template.txt",
                 secureCRT_dir+"CRT_customer-4_vpn_nexus.txt",
                 secureCRT_dir+"CRT_customer-4_vpn_nexus.txt",
                 secureCRT_dir+"CRT_customer-4_vpn_router.txt"]

script_text = []
for i in range(len(ini_templates)):
    script_text.append(open(ini_templates[i],'r').read())

for i in range(len(secure_CRT_dir)):
    if not (os.path.isdir(secure_CRT_dir[i])):
        os.mkdir(secure_CRT_dir[i])

for i in range(len(secure_CRT_dir)):
    # we open one by one the text files containing the ip addresses of ALL routers
    with open(rou_list_files[i]) as routers:
        for line in routers:
            if re.search("^#", line):
                continue
            # value contains the name of the router, and its management ip address
            value = re.search("System Name:\s+(.*?)\s+IPv4 Address:\s+(\d+\.\d+\.\d+\.\d+)", line)
            
            if (value):
                if isinstance(rou_list_regexp[i],list):
                    # in case the regular expressions are a list of values, we need to behave
                    for j in range(len(rou_list_regexp[i])):
                        if re.search(rou_list_regexp[i][j],value.group(1)):
                            # create the directory if it does not exist
                            if not (os.path.isdir(secure_CRT_dir[i]+rou_list_dirs[i][j])):
                                os.mkdir(secure_CRT_dir[i]+rou_list_dirs[i][j])
                            
                            if not (os.path.isfile(secure_CRT_dir[i]+rou_list_dirs[i][j]+value.group(1)+".ini")):
                                print(secure_CRT_dir[i]+rou_list_dirs[i][j]+value.group(1)+".ini")
                                target = open(secure_CRT_dir[i]+rou_list_dirs[i][j]+value.group(1)+".ini", 'w')
                                if (re.search("customer-4_vpn",secure_CRT_dir[i].lower())):
                                    target.write("S:\"Hostname\"="+value.group(2)+"\n"+script_text[i]+login_script[i])
                                else:
                                    target.write(script_text[i]+login_script[i]+"S:\"Script Arguments\"="+value.group(2)+"\n")
                                target.close()
                            break
                elif re.search(rou_list_regexp[i],value.group(1)):
                    if not (os.path.isfile(secure_CRT_dir[i]+value.group(1)+".ini")):
                        print(secure_CRT_dir[i]+value.group(1)+".ini")
                        target = open(secure_CRT_dir[i]+value.group(1)+".ini", 'w')
                        if (re.search("customer-4_vpn",secure_CRT_dir[i].lower())):
                            target.write("S:\"Hostname\"="+value.group(2)+"\n"+script_text[i]+login_script[i])
                        else:
                            target.write(script_text[i]+login_script[i]+"S:\"Script Arguments\"="+value.group(2)+"\n")
                        target.close()
