import boto
import boto.ec2
import time

def setup_aws():
    """make connection to us-east-1, set up an instance, 
       and associate Elastic IPs to it
    """
    conn = boto.ec2.connect_to_region(
        'us-east-1',aws_access_key_id = '<my_aws_access_key_id>', 
	aws_secret_access_key = '<my_aws_secret_access_key>')
    key_pair = conn.create_key_pair('mykey')
    key_pair.save('keys')
    security = conn.create_security_group('csc326-group23','group23')
    security.authorize('icmp', -1, -1, '0.0.0.0/0')
    security.authorize('tcp', 22, 22, '0.0.0.0/0')
    security.authorize('tcp', 80, 80, '0.0.0.0/0')
    reservation = conn.run_instances(
        'ami-9aaa1cf2', key_name = 'mykey', instance_type = 't2.micro', 
        security_groups = ['csc326-group23'])

    # give aws enough time to initialize the instance, otherwise allocate_address will return error
    time.sleep(20)
    address = conn.allocate_address()
    address.associate(reservation.instances[0].id)

if __name__ == "__main__":
    setup_aws()
