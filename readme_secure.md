# secure-CRT

SecureCRT is a simple commercial software to manage connection to devices, for networking guys to routers and switches. 

C:\path_to_SecureCRT\Sessions

All the information to connect to the hosts are placed in the 'Sessions' directory, and can be organized in folders and subfolders, to 
help better searching the target devices, for example:

- customer-1\routers
- customer-1\switches
- customer-2\core
- customer-2\access\switches
- customer-2\CE

In every file, a 'login script' can be configured to log in to the device. In this way a proxy could be potentially used, and
to connect to the target device, a parameter (the target's ip address) can be passed to the login script, so that the SAME
login script can be shared between mulitple devices. This approach is useful to centralize data like username and passwords,
and avoid reconfiguring all sessions in case they change for any reason.

SecureCRT session files have all '.ini' extension. You can manually create a TEMPLATE ".ini" file with your preferred
configurations (like a black background, green color for characters, a specific font style and size and so on), and
you can save it in the sessions directory:

"Customer-1.ini"                 <P>
"Customer-2.ini"                 <P>

The above templates can be used to automatically generate all the session files. You can reference a login script file by
adding the following line to the template:

S:"Script Filename V2"=${VDS_CONFIG_PATH}\Sessions\login_script.vbs                 <P>
S:"Script Arguments"=10.20.8.21                 <P>

In the vbs script, you will reference the argument with:
ip = crt.Arguments(0)

This is for example the case of a proxy that has to be used before connecting to the target devices: the hostname in the
template file will be that of the proxy, while the target ip address will be used in the vbs script, such as the username
and password to connect to the routers/switches. A vbs script example is the following:

ip = crt.Arguments(0)                 <P>
crt.Screen.Send chr(13)             (send 'newline')                 <P>
crt.Screen.Send chr(13)                 <P>

crt.Screen.WaitForString "Login:"                 <P>
crt.Screen.Send "randreetta" & chr(13)                 <P>
crt.Screen.WaitForString "Password:>"                 <P>
crt.Screen.Send "Riccardo01" & chr(13)                 <P>
crt.Screen.WaitForString "<proxy_prompt>"                 <P>
crt.Screen.Send "telnet " & ip & chr(13)                (target ip address)                 <P>
crt.Screen.WaitForString "sername: "                 <P>
crt.Screen.Send "<username>" & chr(13)                 <P>
crt.Screen.WaitForString "assword: "                 <P>
crt.Screen.Send "<password>" & chr(13)                 <P>
crt.Screen.WaitForString ">"                 <P>
crt.Screen.Send "enable" & chr(13)                 <P>
crt.Screen.WaitForString "assword: "                 <P>
crt.Screen.Send "<password>" & chr(13)                 <P>


In case you directly perform telnet/ssh to the target machines, you will need to remove the "Hostname" parameter 
from the ".ini" template file:

S:"Hostname"=172.30.94.170

... and it will need to be written by the python script, '.ini' file by '.ini' file. This could be the case when
connecting through a vpn, so that you use an "oob" network and you don't go through a proxy.

In this way, starting from a list of files or a list of customer's databases, you can generate automatically hundreds
or thousands of secureCRT ".ini" session files, to connect to target deevices, customizing also the login scripts and 
  centralizing the management of username and passwords.
