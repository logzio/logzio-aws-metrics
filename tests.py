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
            self.assertEqual(builder._get_listener_url('us'), 'listener.logz.io')
            self.assertEqual(builder._get_listener_url('eu'), 'listener-eu.logz.io')
            self.assertEqual(builder._get_listener_url('ca'), 'listener-ca.logz.io')
            # Should fail
            self.assertNotEqual(builder._get_listener_url('a'), 'listener-a.logz.io')
            self.assertNotEqual(builder._get_listener_url('6'), 'listener-6.logz.io')
        else:
            # Equal
            self.assertEqual(builder._get_listener_url('us'), builder.CUSTOM_LISTENER)
            self.assertEqual(builder._get_listener_url('ca'), builder.CUSTOM_LISTENER)
            self.assertEqual(builder._get_listener_url('usa'), builder.CUSTOM_LISTENER)


class TestInput(unittest.TestCase):

    def test_is_valid_logzio_token(self):
        # Fail Type
        self.assertRaises(TypeError, iv.is_valid_logzio_token, -2)
        self.assertRaises(TypeError, iv.is_valid_logzio_token, None)
        self.assertRaises(TypeError, iv.is_valid_logzio_token, 4j)
        self.assertRaises(TypeError, iv.is_valid_logzio_token, ['token', 'token'])
        # Fail Value
        self.assertRaises(ValueError, iv.is_valid_logzio_token, '12')
        self.assertRaises(ValueError, iv.is_valid_logzio_token, 'quwyekclshyrflclhf')
        self.assertRaises(ValueError, iv.is_valid_logzio_token, 'rDRJEidvpIbecUwshyCn4kuUjbymiHev')
        # Success
        try:
            iv.is_valid_logzio_token('rDRJEidvpIbecUwshyCnGkuUjbymiHev')
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')

    def test_is_valid_logzio_region_code(self):
        # Fail Type
        self.assertRaises(TypeError, iv.is_valid_logzio_region_code, -2)
        self.assertRaises(TypeError, iv.is_valid_logzio_region_code, None)
        self.assertRaises(TypeError, iv.is_valid_logzio_region_code, 4j)
        self.assertRaises(TypeError, iv.is_valid_logzio_region_code, ['au', 'eu'])
        # Fail Value
        self.assertRaises(ValueError, iv.is_valid_logzio_region_code, '12')
        self.assertRaises(ValueError, iv.is_valid_logzio_region_code, 'usa')
        self.assertRaises(ValueError, iv.is_valid_logzio_region_code, 'au,ca')
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
        # Fail Value
        self.assertRaises(ValueError, iv.is_valid_scrape_interval, 55)
        self.assertRaises(ValueError, iv.is_valid_scrape_interval, 10)
        self.assertRaises(ValueError, iv.is_valid_scrape_interval, 306)
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
        self.assertRaises(TypeError, iv.is_valid_aws_namespaces, -2)
        self.assertRaises(TypeError, iv.is_valid_aws_namespaces, None)
        self.assertRaises(TypeError, iv.is_valid_aws_namespaces, 4j)
        self.assertRaises(TypeError, iv.is_valid_aws_namespaces, ['AWS/EC2', 'AWS/RDS'])
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
        self.assertRaises(TypeError, iv.is_valid_p8s_logzio_name, -2)
        self.assertRaises(TypeError, iv.is_valid_p8s_logzio_name, None)
        self.assertRaises(TypeError, iv.is_valid_p8s_logzio_name, 4j)
        self.assertRaises(TypeError, iv.is_valid_p8s_logzio_name, ['p8s', 'p8s'])
        # Success
        try:
            iv.is_valid_p8s_logzio_name('dev5')
        except (TypeError, ValueError) as e:
            self.fail(f'Unexpected error {e}')

    def test_is_valid_custom_listener(self):
        # Fail Type
        self.assertRaises(TypeError, iv.is_valid_custom_listener, -2)
        self.assertRaises(TypeError, iv.is_valid_custom_listener, None)
        self.assertRaises(TypeError, iv.is_valid_custom_listener, 4j)
        self.assertRaises(TypeError, iv.is_valid_custom_listener, ['token', 'token'])
        # Fail Value
        self.assertRaises(ValueError, iv.is_valid_custom_listener, '12')
        self.assertRaises(ValueError, iv.is_valid_custom_listener, 'www.custom.listener:3000')
        self.assertRaises(ValueError, iv.is_valid_custom_listener, 'custom.listener:3000')
        self.assertRaises(ValueError, iv.is_valid_custom_listener, 'htt://custom.listener:3000')
        self.assertRaises(ValueError, iv.is_valid_custom_listener, 'https://custom.listener:')
        self.assertRaises(ValueError, iv.is_valid_custom_listener, 'https://custom.')
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
