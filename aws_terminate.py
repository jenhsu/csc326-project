import boto
import boto.ec2
import sys

def setup_aws():
    """connect to us-east-1, set up an instance, 
       and associate Elastic IPs to it
    """
    if len(sys.argv) != 2:
	    print "Incorrect number of arguments passed"
	    print "Correct format:\npython terminate.py <instance_id>"
	    sys.exit()

    instance_ID = sys.argv[1]
    print 'instance ID is: ', instance_ID

    f = open("credentials.csv", "r")
    line = f.readline()
    aws_access_key_id = line.split(",")[0].strip()
    aws_secret_access_key = line.split(",")[1].strip()

    conn = boto.ec2.connect_to_region(
        'us-east-1',aws_access_key_id = aws_access_key_id, 
	aws_secret_access_key = aws_secret_access_key)
    reservation = conn.get_all_instances([instance_ID])
    reservation[0].instances[0].stop()

if __name__ == "__main__":
    setup_aws()
