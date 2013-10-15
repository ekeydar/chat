from boto.ec2.elb import ELBConnection
import boto.ec2
import time
import json

''' 
======
README 
======
Has to be invoked from fabfile
'''

def sleep_and_tell(t):
    print 'Sleeping for %d seconds' % (t)
    time.sleep(t)

class Inst(object):
    pass

class Manager(object):
    def __init__(self):
        self.conn = self._make_conn()
        self.elb_conn = self._make_elb_conn()

    def _make_conn(self):
        return boto.ec2.connection.EC2Connection(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
    
    def _make_elb_conn(self):
        return ELBConnection(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
        
    def create_ec2s(self,prefix='sim_client_',kind='test',num=1,type='t1.micro'):
        """ return list of ids """
        print 'Going to create %d instances with prefix = %s kind = %s' % (num,prefix,kind)
        res = self.conn.run_instances(
            image_id='ami-3d4ff254',
            key_name='InplayAKey',
            instance_type=type,
            placement='us-east-1a',
            min_count=num,
            max_count=num)
        print 'Instances created. reservation = %s' % (res)
        inst_ids = [inst.id for inst in res.instances]
        sleep_and_tell(3)
        print 'Settings name for all instances'
        for (index,inst_id) in enumerate(inst_ids):
            self.conn.create_tags([inst_id],dict(Name='%s_%d' % (prefix,index)))
        print 'Settings Kind = %s for all instances' % (kind)
        self.conn.create_tags(inst_ids,dict(Kind=kind))
        print 'Instances created successfully'
        return inst_ids

    def terminate_instances(self,inst_list):
        self.conn.terminate_instances([inst.id for inst in inst_list])

    def stop_instances(self,inst_list):
        self.conn.stop_instances([inst.id for inst in inst_list])

    def start_instances(self,inst_list):
        self.conn.start_instances([inst.id for inst in inst_list])
        
    def reboot_instances(self,inst_list):
        self.conn.reboot_instances([inst.id for inst in inst_list])

    def insts_to_string(self,inst_list,title=None,one_per_line=True):
        names = ['\n   %d) %s' % (index,inst.tags.get('Name','no name')) for (index,inst) in enumerate(inst_list)]
        result = ''.join(names)
        if title:
            result = title + result
        return result

    def _res_list_to_ids(self,res_list):
        result = []
        for r in res_list:
            for inst in r.instances:
                result.append(inst.id)
        return result

    def _res_list_to_insts(self,res_list):
        result = []
        for r in res_list:
            for inst in r.instances:
                result.append(inst)
        return result

    def get_instances_by_kind(self,kind):
        filters_dict = {'tag:Kind' : kind }
        res_list = self.conn.get_all_instances(filters=filters_dict)
        return self._res_list_to_ids(res_list)

    def get_instances_by_kind_and_state(self,kind,state):
        filters_dict = {'tag:Kind' : kind,'instance-state-name':state }
        res_list = self.conn.get_all_instances(filters=filters_dict)
        return self._res_list_to_ids(res_list)

    def wait_for_public_dns(self,ids):
        no_dns = True
        while no_dns:
            sleep_and_tell(5)
            insts = self.get_instances_by_ids(ids)
            no_dns = filter(lambda inst : inst.public_dns_name == '',insts)
        
    def dump_instances(self,inst_list):
        dump_list = []
        for inst in insts_list:
            dump_list.append(inst.__dict__)
        filename = 'aws/ec2s_info.json'
        fh = open(filename,'w')
        json.dump(dump_list,fh)
        fh.close()
        print 'Dump info to %s' % (filename)

    def get_instances_by_ids(self,ids):
        res_list = self.conn.get_all_instances(instance_ids=ids)
        inst_list = self._res_list_to_insts(res_list)
        return inst_list

    def get_all_instances(self):
        res_list = self.conn.get_all_instances()
        inst_list = self._res_list_to_insts(res_list)
        result = filter(lambda inst : inst.state != 'terminated',inst_list)
        return result

    def filter_instances(self,prefix=None,kind=None,state=None):
        insts = self.get_all_instances()
        result = []
        assert prefix or kind or state,'must specify one of prefix,kind,state'
        kinds = []
        prefixes = []
        if prefix:
            prefixes=prefix.lower().split('|')
        if kind:
            kinds=kind.lower().split('|')
        for inst in insts:
            if self.to_filter(inst,prefixes,kinds,state):
                result.append(inst)
        return result
            
    def to_filter(self,inst,prefixes,kinds,state):
        cur_kind = inst.tags.get('Kind','----------').lower()
        if kinds and cur_kind not in kinds:
            return False
        cur_name = inst.tags.get('Name','----------').lower()
        if prefixes:
            if not [p for p in prefixes if cur_name.startswith(p)]:
                return False
        if state and inst.state.lower() != state.lower():
            return False
        return True
        
    def get_elb(self):
        if not self.elb_conn is None:
            elb_list = self.elb_conn.get_all_load_balancers()
            if len(elb_list) == 0:
                print 'No ELB found!'
            elif len(elb_list) == 1:
                print 'Single ELB Found!'
                return elb_list[0]
            else:
                print 'Found %d ELBs - Strange...' % (len(elb_list))
                return elb_list[0]
        return None
    
    def add_instances_to_elb(self,prefix=None,kind=None,state=None):
        insts = self.filter_instances(prefix, kind, state)
        lb = self.get_elb()
        if not lb:
            print 'Failed to add instances to elb, elb not found!'
            return False
    
        insts_ids = []
        for inst in insts:
            insts_ids.append(inst.id)
        if len(insts_ids) > 0:
            print 'Registering The following instances to ELB %s: %s' % (lb.dns_name,insts_ids)
            lb.register_instances(insts_ids)
            return True
        return False
     
    def remove_instances_from_elb(self,prefix=None,kind=None,state=None):
        insts = self.filter_instances(prefix, kind, state)
        lb = self.get_elb()
        if not lb:
            print 'Failed to remove instances to elb, elb not found!'
            return False
    
        insts_ids = []
        for inst in insts:
            insts_ids.append(inst.id)
        if len(insts_ids) > 0:
            print 'Deregistering The following instances from ELB %s: %s' % (lb.dns_name,insts_ids)
            lb.deregister_instances(insts_ids)
            return True
        return False                                   
    

