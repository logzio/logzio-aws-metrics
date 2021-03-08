from util import input_validator, scrape_jobs_config, api
import os
import logging
import yaml

# Environment variables
SCRAPE_INTERVAL = int(os.environ["SCRAPE_INTERVAL"])
LOGZIO_LISTENER_ADDRESS = "https://listener.logz.io:8053"
REGION = os.environ['LOGZIO_REGION']
LOGZIO_TOKEN = os.environ['LOGZIO_TOKEN']
AWS_REGION = os.environ['AWS_DEFAULT_REGION']
AWS_NAMESPACES = os.environ['AWS_NAMESPACES']
CUSTOM_CONFIG_PATH = os.environ['CUSTOM_CONFIG_PATH']
P8S_LOGZIO_NAME = os.environ['P8S_LOGZIO_NAME']
CUSTOM_LISTENER = os.environ['CUSTOM_LISTENER']
# configuration files path
CW_CONFIG = './configuration/cloudwatch.yml'
CW_RAW_CONFIG = './configuration_raw/cloudwatch_raw.yml'
CUSTOM_CW_PATH = './configuration/custom/cloudwatch.yml'
OTEL_CONFIG = './configuration/otel.yml'
OTEL_RAW_CONFIG = './configuration_raw/otel_raw.yml'

# Logging config
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def _create_logger():
    try:
        user_level = os.environ["LOGZIO_LOG_LEVEL"].upper()
        level = user_level if user_level in LOG_LEVELS else DEFAULT_LOG_LEVEL
    except KeyError:
        level = DEFAULT_LOG_LEVEL

    logging.basicConfig(format='%(asctime)s\t\t%(levelname)s\t[%(name)s]\t%(filename)s:%(lineno)d\t%(message)s',
                        level=level)
    return logging.getLogger(__name__)


logger = _create_logger()


# Validate inputs
def validate_input():
    input_validator.is_valid_logzio_token(LOGZIO_TOKEN)
    input_validator.is_valid_aws_region(AWS_REGION)
    input_validator.is_valid_p8s_logzio_name(P8S_LOGZIO_NAME)
    if CUSTOM_LISTENER:
        input_validator.is_valid_custom_listener(CUSTOM_LISTENER)
    input_validator.is_valid_logzio_region_code(REGION)
    input_validator.is_valid_scrape_interval(SCRAPE_INTERVAL)
    namespaces, removed_namespaces = input_validator.is_valid_aws_namespaces(AWS_NAMESPACES)
    return namespaces, removed_namespaces


def _get_listener_url(region):
    if CUSTOM_LISTENER:
        logger.info(f'Adding custom listener to opentelemtry configuration: {CUSTOM_LISTENER}')
        return CUSTOM_LISTENER
    else:
        logzio_listener = LOGZIO_LISTENER_ADDRESS.replace("listener.", "listener{}.".format(_get_region_code(region)))
        logger.info(f'Adding listener to opentelemtry configuration: {logzio_listener}')
        return logzio_listener


def _get_region_code(region):
    if region != "us" and region != "":
        return "-{}".format(region)
    return ""


# close yaml file
def _dump_and_close_file(module_yaml, module_file):
    yaml.preserve_quotes = True
    module_file.seek(0)
    yaml.dump(module_yaml, module_file)
    module_file.truncate()
    module_file.close()


# Updating opentelemrty configuration with remotewrite endpoint, token and scrape jobs
def _update_otel_config(token, region, p8s_name, otel_config):
    logger.info('Adding opentelemtry collector configuration')
    with open(otel_config, 'r+') as module_file:
        module_yaml = yaml.safe_load(module_file)
        module_yaml['exporters']['prometheusremotewrite']['endpoint'] = _get_listener_url(region)
        module_yaml['exporters']['prometheusremotewrite']['headers'][
            'Authorization'] = f'Bearer {token}'
        module_yaml['receivers']['prometheus']['config']['global']['external_labels'][
            'p8s_logzio_name'] = p8s_name
        if scrape_jobs_config.aws not in module_yaml['receivers']['prometheus']['config']['scrape_configs']:
            module_yaml['receivers']['prometheus']['config']['scrape_configs'].append(scrape_jobs_config.aws)
            module_yaml['receivers']['prometheus']['config']['scrape_configs']['static_configs']['labels']['p8s_logzio_name'] = p8s_name
        _dump_and_close_file(module_yaml, module_file)
        logger.info('Opentelemtry collector configuration ready')


# Ading region and scrape interval to cloudwatch exporter configuration
def _add_aws_global_settings(cw_config, aws_region, scrape_interval):
    with open(cw_config, 'r+') as module_file:
        module_yaml = yaml.safe_load(module_file)
        module_yaml['region'] = aws_region
        module_yaml['period_seconds'] = int(scrape_interval)
        _dump_and_close_file(module_yaml, module_file)


# Add metrics to scrape based on AWS_NAMESPACES environment variable
def _add_cloudwatch_namesapce(namespace, cw_config):
    namespace = namespace.split('AWS/')[-1]
    with open(cw_config, 'r+') as cloudwatch_file:
        cloudwatch_yaml = yaml.safe_load(cloudwatch_file)
        with open('./cw_namespaces/{}.yml'.format(namespace), 'r+') as namespace_file:
            namespace_yaml = yaml.safe_load(namespace_file)
            if namespace_yaml not in cloudwatch_yaml['metrics']:
                cloudwatch_yaml['metrics'].extend(namespace_yaml)
        _dump_and_close_file(cloudwatch_yaml, cloudwatch_file)
        logger.info(f'AWS/{namespace} was added to cloudwatch exporter configuration')


def _add_cloudwatch_config(namespaces, cw_config, aws_region, scrape_interval):
    logger.info('Adding cloudwatch exporter configuration')
    _add_aws_global_settings(cw_config, aws_region, scrape_interval)
    for namespace in namespaces:
        _add_cloudwatch_namesapce(namespace, cw_config)
    logger.info('Cloudwatch exporter configuration ready')


# Add custom cloudwatch exporter configuration
def _load_aws_custom_config(cw_config, cw_custom_path):
    with open(cw_custom_path, 'r+') as custom_config_file:
        custom_config_yaml = yaml.safe_load(custom_config_file)
        with open(cw_config, 'w') as cloudwatch_file:
            _dump_and_close_file(custom_config_yaml, cloudwatch_file)
            logger.info('Custom configuration was assigned to cloudwatch exporter')


# Clean volume existing configuration
def _init_configuration(cw_config, cw_raw_config, otel_config, otel_raw_config):
    with open(cw_config, 'r+') as cloudwatch_file:
        with open(cw_raw_config, 'r+') as raw_file:
            raw_yaml = yaml.safe_load(raw_file)
        _dump_and_close_file(raw_yaml, cloudwatch_file)
    with open(otel_config, 'r+') as otel_file:
        with open(otel_raw_config, 'r+') as raw_file:
            raw_yaml = yaml.safe_load(raw_file)
        _dump_and_close_file(raw_yaml, otel_file)


# Expose api endpoints using flask
def _expose_configuration():
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    api.app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    api.app.run(host='0.0.0.0', port=5001)


if __name__ == '__main__':
    AWS_NAMESPACES, removed_namespaces = validate_input()
    logger.warning(f'{removed_namespaces} namespaces are unsupported')
    _init_configuration(CW_CONFIG, CW_RAW_CONFIG, OTEL_CONFIG, OTEL_RAW_CONFIG)
    _update_otel_config(LOGZIO_TOKEN, REGION, P8S_LOGZIO_NAME, OTEL_CONFIG)
    if CUSTOM_CONFIG_PATH:
        _load_aws_custom_config(CW_CONFIG, CUSTOM_CONFIG_PATH)
    else:
        _add_cloudwatch_config(AWS_NAMESPACES, CW_CONFIG, AWS_REGION, SCRAPE_INTERVAL)
    _expose_configuration()
