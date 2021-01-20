import unittest
import yaml
import builder
import util.input_validator as iv
from util.data import aws_namespaces as ns_list


class TestBuilder(unittest.TestCase):
    def test_init_configuration(self):
        # Fail FileNotFoundError
        self.assertRaises(FileNotFoundError,
                          builder._init_configuration, '../wrong/path', builder.CW_RAW_CONFIG, builder.OTEL_CONFIG,
                          builder.OTEL_RAW_CONFIG)
        self.assertRaises(FileNotFoundError,
                          builder._init_configuration, builder.CW_CONFIG, '../wrong/path', builder.OTEL_CONFIG,
                          '../wrong/path')
        self.assertRaises(TypeError,
                          builder._init_configuration, None, builder.CW_RAW_CONFIG, 6,
                          builder.OTEL_RAW_CONFIG)
        self.assertRaises(TypeError,
                          builder._init_configuration, 54.5, '../wrong/path', builder.OTEL_CONFIG,
                          builder.OTEL_RAW_CONFIG)
        # Success
        try:
            builder._init_configuration(builder.CW_CONFIG, builder.CW_RAW_CONFIG, builder.OTEL_CONFIG,
                                        builder.OTEL_RAW_CONFIG)
        except (TypeError, FileNotFoundError) as e:
            self.fail(f'Unexpected error {e}')

    def test_update_otel_config(self):
        # Fail FileNotFoundError
        self.assertRaises(FileNotFoundError,
                          builder._update_otel_config, builder.LOGZIO_TOKEN, builder.REGION, builder.P8S_LOGZIO_NAME,
                          './wrong/path')
        # Success
        try:
            builder._update_otel_config(builder.LOGZIO_TOKEN, builder.REGION, builder.P8S_LOGZIO_NAME,
                                        builder.OTEL_CONFIG)
        except Exception as e:
            self.fail(f'Unexpected error {e}')

    def test_load_aws_custom_config(self):
        # Fail FileNotFoundError
        self.assertRaises(FileNotFoundError,
                          builder._load_aws_custom_config, builder.CW_CONFIG, '/wrong/path')
        # Fail ParserError
        self.assertRaises(yaml.parser.ParserError,
                          builder._load_aws_custom_config, builder.CW_CONFIG, './tests_resources/invalid.yaml')
        # Success
        try:
            builder._load_aws_custom_config(builder.CW_CONFIG, './tests_resources/valid.yaml')
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')

    def test_dump_and_close_file(self):
        test_file = open('./tests_resources/empty.yaml', 'r+')
        valid_yaml = yaml.safe_load(open('./tests_resources/valid.yaml', 'r+'))
        yaml.dump({}, test_file)
        # Success
        try:
            builder._dump_and_close_file(valid_yaml, test_file)
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')
        test_file.close()

    def test_add_cloudwatch_namesapce(self):
        # Fail FileNotFoundError
        self.assertRaises(FileNotFoundError,
                          builder._add_cloudwatch_namesapce, 'AWS/EC2', './wrong/path')
        # Success
        try:
            for ns in ns_list:
                builder._add_cloudwatch_namesapce(ns, builder.CW_CONFIG)
        except Exception as e:
            self.fail(f'Unexpected error {e}')

    def test_get_listener_url(self):
        if not builder.CUSTOM_LISTENER:
            # Equal
            valid_ns = ["au", "ca", "eu", "nl", "uk", "wa"]
            for ns in valid_ns:
                self.assertEqual(builder._get_listener_url(ns), f'https://listener-{ns}.logz.io:8053')
            self.assertEqual(builder._get_listener_url('us'), 'https://listener.logz.io:8053')
        else:
            # Equal
            self.assertEqual(builder._get_listener_url('us'), builder.CUSTOM_LISTENER)
            self.assertEqual(builder._get_listener_url('ca'), builder.CUSTOM_LISTENER)
            self.assertEqual(builder._get_listener_url('usa'), builder.CUSTOM_LISTENER)


class TestInput(unittest.TestCase):

    def test_is_valid_logzio_token(self):
        # Fail Type
        non_valid_types = [-2, None, 4j, ['string', 'string']]
        for t in non_valid_types:
            self.assertRaises(TypeError, iv.is_valid_logzio_token, t)
        # Fail Value
        non_valid_vals = ['12', 'quwyekclshyrflclhf', 'rDRJEidvpIbecUwshyCn4kuUjbymiHev']
        for v in non_valid_vals:
            self.assertRaises(ValueError, iv.is_valid_logzio_token, v)
        # Success
        try:
            iv.is_valid_logzio_token('rDRJEidvpIbecUwshyCnGkuUjbymiHev')
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')

    def test_is_valid_logzio_region_code(self):
        # Fail Type
        non_valid_types = [-2, None, 4j, ['string', 'string']]
        for t in non_valid_types:
            self.assertRaises(TypeError, iv.is_valid_logzio_region_code, t)
        # Fail Value
        non_valid_vals = ['12', 'usa', 'au,ca']
        for v in non_valid_vals:
            self.assertRaises(ValueError, iv.is_valid_logzio_region_code, v)
        # Success
        try:
            iv.is_valid_logzio_region_code('ca')
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')
        try:
            iv.is_valid_logzio_region_code('us')
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')

    def test_is_valid_scrape_interval(self):
        # Fail type
        non_valid_types = ['12', None, False, ['string', 'string']]
        for t in non_valid_types:
            self.assertRaises(TypeError, iv.is_valid_scrape_interval, t)
        # Fail Value
        non_valid_vals = [-60, 55, 10, 306, 4j]
        for v in non_valid_vals:
            self.assertRaises(ValueError, iv.is_valid_scrape_interval, v)
        # Success
        try:
            iv.is_valid_scrape_interval(360000)
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')
        try:
            iv.is_valid_scrape_interval(60)
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')

    def test_is_valid_aws_namespaces(self):
        # Fail Type
        non_valid_types = [-2, None, 4j, ['string', 'string']]
        for t in non_valid_types:
            self.assertRaises(TypeError, iv.is_valid_aws_namespaces, t)
        # Fail Value
        self.assertRaises(ValueError, iv.is_valid_aws_namespaces, '')
        self.assertRaises(ValueError, iv.is_valid_aws_namespaces, 'AWS/ec2,  aws/RDS, AWS/lambda, AWS/fdfdf')
        # Success
        self.assertTupleEqual(iv.is_valid_aws_namespaces('AWS/RDS,AWS/Lambda,AWS/CloudFront'),
                              (['AWS/CloudFront', 'AWS/Lambda', 'AWS/RDS'], []))
        self.assertTupleEqual(iv.is_valid_aws_namespaces('AWS/RDS,AWS/nosuch,AWS/Lambda,AWS/CloudFront'),
                              (['AWS/CloudFront', 'AWS/Lambda', 'AWS/RDS'], ['AWS/nosuch']))
        self.assertTupleEqual(iv.is_valid_aws_namespaces('AWS/RDS,AWS/Lambda,AWS/Cloudfront'),
                              (['AWS/Lambda', 'AWS/RDS'], ['AWS/Cloudfront']))
        self.assertTupleEqual(iv.is_valid_aws_namespaces('AWS/RDS, AWS/RDS,  AWS/Lambda,AWS/Lambda,AWS/Cloudfront'),
                              (['AWS/Lambda', 'AWS/RDS'], ['AWS/Cloudfront']))

    def test_is_valid_p8s_logzio_name(self):
        # Fail Type
        non_valid_types = [-2, None, 4j, ['string', 'string']]
        for t in non_valid_types:
            self.assertRaises(TypeError, iv.is_valid_p8s_logzio_name, t)
        # Success
        try:
            iv.is_valid_p8s_logzio_name('dev5')
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')

    def test_is_valid_custom_listener(self):
        # Fail Type
        non_valid_types = [-2, None, 4j, ['string', 'string']]
        for t in non_valid_types:
            self.assertRaises(TypeError, iv.is_valid_custom_listener, t)
        # Fail Value
        non_valid_vals = ['12', 'www.custom.listener:3000', 'custom.listener:3000', 'htt://custom.listener:3000',
                          'https://custom.listener:', 'https://custom.']
        for v in non_valid_vals:
            self.assertRaises(ValueError, iv.is_valid_custom_listener, v)
        # Success
        try:
            iv.is_valid_custom_listener('http://custom.listener:3000')
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')
        try:
            iv.is_valid_custom_listener('https://localhost:9200')
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')


if __name__ == '__main__':
    unittest.main()
