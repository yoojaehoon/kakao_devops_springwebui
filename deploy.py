#!/usr/bin/env python
# coding:utf-8

import commands
import time

import argparse
from output import printData

APPNAME="app"
NGINX="jh_nginx"

def get_running_nginx():
    cmd = "docker container ls --format '{{.ID}}\t{{.Names}}' | grep %s" %(NGINX)
    ret = commands.getoutput(cmd)
    if ret == "":
        return "running nginx container is zero"
    sp_ret =  ret.split('\n')
    ret_dict = {}
    for i in sp_ret:
        r = i.split('\t')
        if not ret_dict.has_key(r[0]):
            ret_dict['id']=r[0]
            ret_dict['name']=r[1]
            #ret_dict[r[0]]=r[1]

    return ret_dict

def get_running_apps():
    cmd = "docker container ls --format '{{.ID}}\t{{.Names}}' | grep %s" %(APPNAME)
    ret = commands.getoutput(cmd)
    if ret == "":
        return "running nginx container is zero"
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

def service_down_by_id(container_id):
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
    title = "KAKAO_PAY_Devops docker manager"

    parser = argparse.ArgumentParser(description=title, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(metavar='<subcommand>', dest='subcommand')

    parser.add_argument('-o', '--output', help='Output format.', choices=['table','minimal'], default='table')

    parser_start = subparsers.add_parser('start', help="Start the docker containers.")
    parser_start.add_argument("--app", type=int,required=False)
    parser_start.add_argument("-o","--output", choices=['table','minimal'], default='table')
    parser_stop = subparsers.add_parser('stop', help="Stop the docker containers.")
    parser_stop.add_argument("--container", type=str,required=False)
    
    parser_restart = subparsers.add_parser('restart', help="Restart the docker containers.")
    parser_deploy = subparsers.add_parser('deploy', help="Deploy the docker containers.")
    parser_status = subparsers.add_parser('status', help="Status the docker containers.")

    args = parser.parse_args()

    if args.subcommand == "start":
        cmd = "docker-compose up -d"
        if args.app > 0 and args.app < 10:
            cmd = "docker-compose up -d --scale %s=%d" %(APPNAME,args.app)

        result= commands.getoutput(cmd)
        printData(result)
        printData(get_running_nginx(),args.output,minimal_key='id')
        printData(get_running_apps())

    elif args.subcommand == "stop":
        if args.container == None:
            cmd = "docker-compose down"
            result= commands.getoutput(cmd)
            printData(result)
            printData(get_running_nginx())
            printData(get_running_apps())
        else:
            ret = get_running_apps()
            if len(ret) == 1:
                print ("At least 1 %s service is must running" %(APPNAME))
            else:
                service_down_by_id(args.container)
            printData(get_running_apps())

    elif args.subcommand == "restart":
        print "BEFORE"
        printData(get_running_nginx())
        printData(get_running_apps())
        cmd = "docker-compose down"
        commands.getstatusoutput(cmd)
        print "Restarting the containers %s , %s" %(APPNAME,NGINX)
        time.sleep(5)
        cmd = "docker-compose up -d"
        commands.getstatusoutput(cmd)
        print "AFTER"
        printData(get_running_nginx())
        printData(get_running_apps())

    elif args.subcommand == "deploy":
        ret = get_running_apps()
        for i in ret:
            print "ID : %s Name : %s\n" %(i,ret[i])
        deploy_val,output = blue_green_deploy(ret)
        ret = get_running_apps()
        for i in ret:
            print "ID : %s Name : %s\n" %(i,ret[i])

        print "Deploy : %s , Output : %s" %(deploy_val, output)
    elif args.subcommand == "status":

        print "------NGINX Status------"
        printData(get_running_nginx())
        print "------APP Status--------"
        printData(get_running_apps())
    else:
        print "unknown command"

