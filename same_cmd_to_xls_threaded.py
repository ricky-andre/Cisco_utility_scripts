import re
import time
import datetime
import threading
from openpyxl import Workbook
from connect_mgr import telnet_manager, ssh_manager, CONN_SUCCESS
from getDevices import get_dev_list

store_dir = "C:/Users/user_a/desktop/"
# this function reads a list of all the devices you can potentially reach, and gives
# back a dictionary of dictionaries that is made in the following way:
# - transport protocol (ssh/telnet)
# - a 'connection profile' (i.e. connect through a proxy or not, username/pwd to connect)
# - a list of device name ip addresses
# other filters can be the device name (always as a regular expression)
conn_list = get_dev_list(dir_flt='./dir_filter/')

separator = "\s\s+"
commandsList = ["show platform", "show interf description"]

# let's also store date and time on the file name !!
clock_time = time.strftime("%H %M %S")
day_time = time.strftime("a%Y m%m g%d")

target = Workbook()
sheet = target.active
row_counter = 1

def exec_cmd (tran, profile, dev):
    global row_counter
    try:
        if tran == 'ssh':
            cnt_mgr = ssh_manager(profile)
        else:
            cnt_mgr = telnet_manager(profile)
    except Exception as err:
        print('Unable to connect '+str(err)+' device '+dev)
        return
    res = 404
    mgmt_ip = conn_list[tran][profile][dev]['mgmt']
    host_tran = conn_list[tran][profile][dev]['tran']
    try:
        cnt_mgr.setTransport(host_tran)
        res = cnt_mgr.node_login(mgmt_ip, router = dev)
        if res != CONN_SUCCESS:
            print('Unable to connect to '+dev+' mgmt ip ' + mgmt_ip)
            return
    except Exception as e:
        print (' raised exception: ' + str(e))
        print('Unable to connect to '+dev+' mgmt ip ' + mgmt_ip)
        return
    
    cnt_mgr.run_cmd('terminal length 0')

    for command in commandsList:
        print(" executing \""+command+"\" on "+dev+" ...")
        try:
            lines_out = cnt_mgr.run_cmd(command).splitlines()
            # Using lock here is mandatory, since all threads access the same excel file
            # and the row_counter index. Would they access each a different sheet, maybe
            # it wouldn't be necessary. In any case it doesn't seem efficiency increases
            # that much WITHOUT using the lock.
            lock.acquire()
            if not len(separator):
                for line in lines_out:
                    sheet['A'+str(row_counter)].value = dev
                    sheet['B'+str(row_counter)].value = command
                    sheet['C'+str(row_counter)].value = line
                    row_counter += 1
            else:
                for line in lines_out:
                    sheet['A'+str(row_counter)].value = dev
                    sheet['B'+str(row_counter)].value = command
                    all_words = re.split(separator, line)
                    col_counter = 0
                    for word in all_words:
                        if len(word.strip()):
                            sheet[chr(ord('C')+col_counter)+str(row_counter)].value = word.strip()
                            col_counter += 1
                    row_counter += 1
            lock.release()
        except Exception as err:
            print (" timed out command, try to raise the timeout value! \n "+str(err))
            return
    print ("Finished commands on '" + dev + "'\n")
    cnt_mgr.node_logout()
    cnt_mgr.close()

MAX_ACTIVE_THREADS = 20
# Every PC or similar device can't launch an infinite number of ssh/telnet sessions,
# limiting the number avoids problems and writing to the disk empty files, without
# slowing down the whole process too much.
start = datetime.datetime.now()
lock = threading.Lock()
t_list = []
for transport in conn_list:
    for conn_profile in conn_list[transport]:
        for device in conn_list[transport][conn_profile]:
            while threading.active_count() >= MAX_ACTIVE_THREADS:
                print('Opened too many threads, sleeping for a while ...')
                time.sleep(5)
            t = threading.Thread(target = exec_cmd, args=(transport, conn_profile, device))
            t.setDaemon(True)
            now = datetime.datetime.now()
            print('Launching thread for '+device+' time %d:%d:%d' % (now.hour, now.minute, now.second))
            t.start()
            t_list.append(t)

# wait for all processes to finish
for j in t_list:
    j.join()

print("Total time:" , datetime.datetime.now()-start)
if len(conn_list):
    target.save(store_dir+"Cmd_out__"+day_time+"__"+clock_time+".xlsx")
    target.close()
