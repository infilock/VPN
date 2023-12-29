from flask import Flask, send_from_directory
import subprocess
import os.path
from os import path
import time

main_ovpn_profile = 'config/server_op1.ovpn'
main_ovpn_profile_pid = 0

server_IP = "ukw.vio17.com"

def run_main_ovpn():
    print("starting main ovpn server...")
    
    main_ovpn_process = subprocess.Popen(['openvpn', '--config', main_ovpn_profile, '--daemon', '--writepid', main_ovpn_profile+'.pid'], stdout=subprocess.PIPE)
    main_ovpn_process.wait()
    print(main_ovpn_process.returncode)
    if(main_ovpn_process.returncode != 0):
        print("error in starting ovpn ..")
        exit()
    main_ovpn_profile_pid = main_ovpn_process.pid


if(path.exists(main_ovpn_profile+'.pid')):

    with open(main_ovpn_profile+'.pid','r') as f:
        main_ovpn_profile_pid = f.read().strip()

    print("checking if the main ovpn process is running : " + main_ovpn_profile_pid)
    main_connection_process = subprocess.run(['kill', '-0', main_ovpn_profile_pid])
    print(main_connection_process.returncode)
    if(main_connection_process.returncode == 1):
        rm_res = subprocess.run(['rm', main_ovpn_profile+'.pid'])
        if(rm_res.returncode != 0):
            print(rm_res)
            print("cannot remove pid file")
            exit()
        run_main_ovpn()

else:
    run_main_ovpn()


app = Flask(__name__,static_url_path='/create')
app._static_folder = "."
app.run(host='192.168.112.1', port=80)

@app.route("/start/<name>")
def start(name):
    
    process = subprocess.Popen(['openvpn', '--config', name+'.ovpn', '--daemon', '--writepid', name+'.pid'], stdout=subprocess.PIPE)
    process.wait()

    print(process.pid)

    if(process.returncode == 0):
        return "process started : " + str(process.pid)
    else:
        return "error"


@app.route("/create/<name>")
def create(name):
    counter = 100
    if(path.exists('config/counter.txt')):
        with open('config/counter.txt','r') as f:
            counter = int(f.read().strip())
        with open('config/counter.txt','w') as f:
            f.writelines(str(counter+2))
        print("using ip : 192.168.112." + str(counter))
    else:
        with open('counter.txt','w') as f:
            f.writelines(str(counter+2))
        print("using ip : 192.168.112." + str(counter))

    server_octed = counter
    client_octed = counter + 1

    if(path.exists('config/server.template')):
        if(path.exists('config/client.template')):
            server_conf_file = 'config/'+str(name)+'.ovpn'
            client_conf_file = 'config/client_'+str(name)+'.ovpn'

            subprocess.run(['cp', 'config/server.template', server_conf_file], stdout=subprocess.PIPE)
            subprocess.run(['cp', 'config/client.template', client_conf_file], stdout=subprocess.PIPE)

            subprocess.run(['sed', '-i', 's/sIP_LAST_OCTED/'+str(server_octed)+'/g', server_conf_file], stdout=subprocess.PIPE)
            subprocess.run(['sed', '-i', 's/cIP_LAST_OCTED/'+str(client_octed)+'/g', server_conf_file], stdout=subprocess.PIPE)

            subprocess.run(['sed', '-i', 's/sIP_LAST_OCTED/'+str(server_octed)+'/g', client_conf_file], stdout=subprocess.PIPE)
            subprocess.run(['sed', '-i', 's/cIP_LAST_OCTED/'+str(client_octed)+'/g', client_conf_file], stdout=subprocess.PIPE)
            subprocess.run(['sed', '-i', 's/SERVER_ADDRESS/'+str(server_IP)+'/g', client_conf_file], stdout=subprocess.PIPE)

            print(client_conf_file)
            return app.send_static_file(client_conf_file)
        else:
            print("no such file : client.template")
            return "error c.t"
    else:
        print("no such file : server.template")
        return "error s.t"

    
