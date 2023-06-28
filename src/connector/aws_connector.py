import boto3


class AwsConnector:
    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region_name):
        self.session = self._init_session(aws_access_key_id, aws_secret_access_key, aws_region_name)

    def list_available_ip_counts_by_subnet(self, filters):
        ec2 = self.session.client('ec2')

        response = ec2.describe_subnets(
            Filters=self._make_filter(filters)
        )

        ret = {}
        for subnet in response['Subnets']:
            ret[subnet['SubnetId']] = subnet['AvailableIpAddressCount']

        return ret

    @staticmethod
    def _make_filter(filters):
        result = [{
            'Name': 'vpc-id',
            'Values': [filters['vpc_id']]
        }]

        if filters.get('tags') is None:
            return result

        for key, value in filters['tags'].items():
            result.append({
                'Name': f'tag:{key}',
                'Values': [value]
            })

        return result

    @staticmethod
    def _init_session(aws_access_key_id, aws_secret_access_key, region_name):
        return boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                             region_name=region_name)
