import boto
import boto.ec2
import time
import paramiko
import subprocess

def setup_aws():
    """connect to us-east-1, set up an instance,
       associate Elastic IPs to it, copy files
       to instance, and start server
    """

    # extract access info from crendential file
    f = open("credentials.csv", "r")
    line = f.readline()
    aws_access_key_id = line.split(",")[0].strip()
    aws_secret_access_key = line.split(",")[1].strip()

    # setup connection and start instance
    conn = boto.ec2.connect_to_region(
        'us-east-1',aws_access_key_id = aws_access_key_id,
	aws_secret_access_key = aws_secret_access_key)
    key_pair = conn.create_key_pair('scriptkey')
    key_pair.save("")
    security = conn.create_security_group('csc326-group23','group23')
    security.authorize('icmp', -1, -1, '0.0.0.0/0')
    security.authorize('tcp', 22, 22, '0.0.0.0/0')
    security.authorize('tcp', 80, 80, '0.0.0.0/0')
    reservation = conn.run_instances(
        'ami-9aaa1cf2', key_name = 'scriptkey', instance_type = 't2.micro',
        security_groups = ['csc326-group23'])

    # wait until the instance is running
    while reservation.instances[0].update() != 'running':
        time.sleep(5)

    # set up elastic ip
    address = conn.allocate_address()
    address.associate(reservation.instances[0].id)
    ip = address.public_ip
    print ip

    # get dns of the instance
    dns = conn.get_all_instances(instance_ids = [reservation.instances[0].id])[0].instances[0].public_dns_name
    print dns

    # wait for server to be stable/reachable
    while True:
        istatus=conn.get_all_instance_status(instance_ids = [reservation.instances[0].id])
        print istatus[0].system_status.details["reachability"]
        if istatus[0].system_status.details["reachability"] == "passed":
           break
        time.sleep(5)

    # copy the required files in tar.gz format to the instance
    subprocess.check_call(["scp", "-i", "scriptkey.pem", "-o", "StrictHostKeyChecking=no", "-r", "csc326-project.tar.gz", "ubuntu@"+str(ip)+":~/"])

    # set up ssh connection
    k = paramiko.RSAKey.from_private_key_file("scriptkey.pem") # must be in your current dir
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    c.connect( hostname = str(ip), username = "ubuntu", pkey = k )

    # the commands are the following: update apt-get, install pip, install python-dev and libev-dev for the bjoern library used for server,
    # decompress the file copied earlier, install the libraries listed in requirements.txt, run frontend.py in the background
    commands = [ "sudo apt-get update > /dev/null", "sudo apt-get install --yes python-pip > /dev/null", "sudo apt-get install --yes python-dev > /dev/null", "sudo apt-get install --yes libev-dev > /dev/null", "tar -xf csc326-project.tar.gz", "sudo pip install -r requirements.txt", "sudo nohup python frontend.py " + ip + " > /dev/null 2> frontend.err < /dev/null &"] # these commands will exec in series

    # excuting the commands and print the outputs
    for command in commands:
        print "Executing {}".format( command )
        stdin , stdout, stderr = c.exec_command(command) # this command is executed on the *remote* server
        print stdout.read()
        print( "Errors")
        print stderr.read()

    c.close()

if __name__ == "__main__":
    #setup_aws()