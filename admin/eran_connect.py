#!/usr/bin/python
import aws_utils as au
import sys
import os


def get_options():
    print 'Getting host list, might take several seconds...'
    m = au.Manager()
    runnings = m.filter_instances(state='running')
    options = dict()
    for inst in runnings:
        name = inst.tags.get('Name')
        options[name] = [inst.public_dns_name]
    return options

def main():

    index=1
    hosts_list=['dummy']
    options = get_options()
    for name in sorted(options.keys()):
        hosts = options[name]
        for host in hosts:
            print '%2d) %-15s : %s' % (index,name,host)
            assert len(hosts_list) == index
            hosts_list.append(host)
            index+=1

    is_ok = False  
    while not is_ok:
        select = raw_input('Enter your selection:')
        try:
            if select == 'q':
                sys.exit(0)
            select_index = int(select)
            if select_index < 1 or select_index >= len(hosts_list):
                is_ok = False
            else:
                is_ok = True
        except Exception,e:
            is_ok = False

    command = 'ssh -i ~/chat.pem ubuntu@%s' % hosts_list[select_index]
#print command
    os.system(command)

if __name__ == '__main__':
    main()

