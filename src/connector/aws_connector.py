import boto3


class AwsConnector:
    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region_name):
        self.session = self._init_session(aws_access_key_id, aws_secret_access_key, aws_region_name)

    def list_available_ip_counts_by_subnet(self, filters):
        ec2 = self.session.client('ec2')
        response = ec2.describe_subnets(
            Filters=[{
                'Name': 'vpc-id',
                'Values': [filters['vpc_id']]
            }],
        )

        ret = {}
        for subnet in response['Subnets']:
            is_match = False
            for k, v in filters['tags'].items():
                if subnet['Tags'][0]['Key'] == k and subnet['Tags'][0]['Value'] == v:
                    is_match = True

            if is_match:
                ret[subnet['SubnetId']] = subnet['AvailableIpAddressCount']

        return ret

    @staticmethod
    def _init_session(aws_access_key_id, aws_secret_access_key, region_name):
        return boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                             region_name=region_name)
