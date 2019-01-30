#!/usr/bin/env python
# coding:utf-8

import commands
import time

APPNAME="app"
NGINX="jh_nginx"
def get_running_apps():
    cmd = "docker container ls --format '{{.ID}}\t{{.Names}}' | grep %s" %(APPNAME)
    ret = commands.getoutput(cmd)
    sp_ret =  ret.split('\n')
    ret_dict = {}
    for i in sp_ret:
        r = i.split('\t')
        if not ret_dict.has_key(r[0]):
            ret_dict[r[0]]=r[1]

    return ret_dict

def blue_green_deploy(old_container):
    old_count = len(old_container)
    #Build changed image
    build_docker_image()
 
    #Prepare the newest services
    ret=_blue_service_up(APPNAME,old_count*2)

    if ret:
        for container in old_container:
            _blue_service_down(container)
    
    return ret,"Finish"

def build_docker_image():
    print "STX---Docker pull the Image------\n"
    cmd = "docker-compose pull"
    ret = commands.getoutput(cmd)
    print ret
    print "------Docker pull the Image---ETX\n"

def _blue_service_up(appname,count):
    print "STX---Docker service's up------\n"
    cmd = "docker-compose up -d --no-recreate --scale %s=%d" %(appname,count)
    ret,output = commands.getstatusoutput(cmd)
    print output
    cmd = "docker exec -i -t %s /etc/init.d/nginx reload" %(NGINX)
    ret = commands.getoutput(cmd)
    time.sleep(5)
    print "------Docker service's up---ETX\n"
    return True

def _blue_service_down(container_id):
    print "STX---Docker service's down------\n"
    cmd = "docker container stop %s" %(container_id)
    print cmd
    commands.getoutput(cmd)
    cmd = "docker container rm %s" %(container_id)
    print cmd
    commands.getoutput(cmd)
    cmd = "docker exec -i -t %s /etc/init.d/nginx reload" %(NGINX)
    ret = commands.getoutput(cmd)
    print "------Docker service's up---ETX\n"


if __name__ == '__main__':
    ret = get_running_apps()
    for i in ret:
        print "ID : %s Name : %s\n" %(i,ret[i])
    deploy_val,output = blue_green_deploy(ret)
    ret = get_running_apps()
    for i in ret:
        print "ID : %s Name : %s\n" %(i,ret[i])

    print "Deploy : %s , Output : %s" %(deploy_val, output)
