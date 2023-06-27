from prometheus_client import push_to_gateway
from schema import Schema, Optional
from connector.aws_connector import AwsConnector
import yaml
import base64
import logging

logging.basicConfig(level=logging.INFO)


class SubnetIpCounterManager:
    def __init__(self):
        self.config = self._get_config()
        self.aws_connector = AwsConnector(self.config['credentials']['aws_access_key_id'],
                                          self.config['credentials']['aws_secret_access_key'],
                                          self.config['credentials'].get('aws_region_name', 'ap-northeast-2'))

    def collect_subnet_available_ips(self, gauge):
        filters = self.config['filters']
        list_ip_count_by_subnet = self.aws_connector.list_available_ip_counts_by_subnet(filters)

        for subnet_id, ip_count in list_ip_count_by_subnet.items():
            vpc_id = self.config['filters']['vpc_id']
            gauge.labels(
                collect_from='subnet_ip_collector',
                vpc_id=vpc_id,
                subnet_id=subnet_id
            ).set(ip_count)

        return True

    def push_gateway(self, registry):
        endpoint = self.config['push_gateway_endpoint']
        try:
            push_to_gateway(endpoint, job='subnet_available_ip_count', registry=registry)
            logging.info("Successfully pushed metrics to push gateway at {}".format(endpoint))
        except Exception as e:
            raise Exception("Error while pushing metrics to push gateway: {}".format(e))

    @staticmethod
    def _get_config():
        try:
            with open("./conf/config.yaml", 'r') as yml_file:
                cfg = yaml.load(yml_file, Loader=yaml.FullLoader)
                SubnetIpCounterManager._validate_config(cfg)
                SubnetIpCounterManager._decode_credentials(cfg)
                return cfg
        except Exception as e:
            raise Exception("Error while reading config.yml file: {}".format(e))

    @staticmethod
    def _validate_config(cfg):
        schema = Schema({
            'credentials': {
                'aws_access_key_id': str,
                'aws_secret_access_key': str,
                Optional('aws_region_name'): str
            },
            'push_gateway_endpoint': str,
            'filters': {
                'vpc_id': str,
                'tags': dict
            },
        })
        try:
            schema.validate(cfg)
        except Exception as e:
            raise Exception("Invalid configuration: {}".format(e))

    @staticmethod
    def _decode_credentials(cfg):
        decrypted_aws_access_key_id = base64.b64decode(cfg['credentials']['aws_access_key_id'])\
            .decode('utf-8').replace("\n", "")
        decrypted_aws_secret_access_key = base64.b64decode(cfg['credentials']['aws_secret_access_key'])\
            .decode('utf-8').replace("\n", "")

        cfg['credentials']['aws_access_key_id'] = decrypted_aws_access_key_id
        cfg['credentials']['aws_secret_access_key'] = decrypted_aws_secret_access_key

