from util import input_validator, scrape_jobs_config, api
import os
import logging
import yaml

# Environment variables
SCRAPE_INTERVAL = int(os.environ["SCRAPE_INTERVAL"])
SUPPORTED_MODULES = ['aws']
LOGZIO_LISTENER_ADDRESS = "https://listener.logz.io:8053"
REGION = os.environ['LOGZIO_REGION']
LOGZIO_TOKEN = os.environ['LOGZIO_TOKEN']
AWS_REGION = os.environ['AWS_DEFAULT_REGION']
AWS_NAMESPACES = os.environ['AWS_NAMESPACES']
LOGZIO_MODULES = os.environ['LOGZIO_MODULES']
CUSTOM_CONFIG_PATH = os.environ['CUSTOM_CONFIG_PATH']
P8S_LOGZIO_NAME = os.environ['P8S_LOGZIO_NAME']

# Logging config
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Validate inputs
input_validator.is_valid_logzio_token(LOGZIO_TOKEN)
input_validator.is_valid_aws_region(AWS_REGION)
LOGZIO_MODULES = input_validator.is_valid_logz_io_modules(LOGZIO_MODULES, SUPPORTED_MODULES)
input_validator.is_valid_logzio_region_code(REGION)
input_validator.is_valid_scrape_interval(SCRAPE_INTERVAL)
AWS_NAMESPACES = input_validator.is_valid_aws_namespaces(AWS_NAMESPACES)


def _create_logger():
    try:
        user_level = os.environ["LOGZIO_LOG_LEVEL"].upper()
        level = user_level if user_level in LOG_LEVELS else DEFAULT_LOG_LEVEL
    except KeyError:
        level = DEFAULT_LOG_LEVEL

    logging.basicConfig(format='%(asctime)s\t\t%(levelname)s\t[%(name)s]\t%(filename)s:%(lineno)d\t%(message)s',
                        level=level)
    return logging.getLogger(__name__)


def _get_listener_url(region):
    return LOGZIO_LISTENER_ADDRESS.replace("listener.", "listener{}.".format(_get_region_code(region)))


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
def _update_otel_config():
    logger.info('Adding opentelemtry collector configuration')
    with open('./configuration/otel.yml', 'r+') as module_file:
        module_yaml = yaml.safe_load(module_file)
        module_yaml['exporters']['prometheusremotewrite']['endpoint'] = _get_listener_url(REGION)
        module_yaml['exporters']['prometheusremotewrite']['headers'][
            'Authorization'] = f'Bearer {LOGZIO_TOKEN}'
        module_yaml['receivers']['prometheus']['config']['global']['external_labels']['p8s_logzio_name'] = P8S_LOGZIO_NAME
        for module in LOGZIO_MODULES:
            if module == 'aws':
                if scrape_jobs_config.aws not in module_yaml['receivers']['prometheus']['config']['scrape_configs']:
                    module_yaml['receivers']['prometheus']['config']['scrape_configs'].append(scrape_jobs_config.aws)
        _dump_and_close_file(module_yaml, module_file)
        logger.info('Opentelemtry collector configuration ready')

# Ading region and scrape interval to cloudwatch exporter configuration
def _add_aws_global_settings():
    with open('./configuration/cloudwatch.yml', 'r+') as module_file:
        module_yaml = yaml.safe_load(module_file)
        module_yaml['region'] = AWS_REGION
        module_yaml['period_seconds'] = int(SCRAPE_INTERVAL)
        _dump_and_close_file(module_yaml, module_file)

# Add metrics to scrape based on AWS_NAMESPACES environment variable
def _add_cloudwatch_namesapce(namespace):
    namespace = namespace.split('AWS/')[-1]
    with open('./configuration/cloudwatch.yml', 'r+') as cloudwatch_file:
        cloudwatch_yaml = yaml.safe_load(cloudwatch_file)
        with open('./cw_namespaces/{}.yml'.format(namespace), 'r+') as namespace_file:
            namespace_yaml = yaml.safe_load(namespace_file)
            if namespace_yaml not in cloudwatch_yaml['metrics']:
                cloudwatch_yaml['metrics'].extend(namespace_yaml)
        _dump_and_close_file(cloudwatch_yaml, cloudwatch_file)
        logger.info(f'AWS/{namespace} was added to cloudwatch exporter configuration')


def _add_cloudwatch_config():
    logger.info('Adding cloudwatch exporter configuration')
    _add_aws_global_settings()
    for namespace in AWS_NAMESPACES:
        _add_cloudwatch_namesapce(namespace)
    logger.info('Cloudwatch exporter configuration ready')

# Add custom cloudwatch exporter configuration
def _load_aws_custom_config():
    with open('./configuration/custom/cloudwatch.yml', 'r+') as custom_config_file:
        custom_config_yaml = yaml.safe_load(custom_config_file)
        with open('./configuration/cloudwatch.yml', 'w') as cloudwatch_file:
            _dump_and_close_file(custom_config_yaml, cloudwatch_file)
            logger.info('Custom configuration was assigned to cloudwatch exporter')

# Clean volume existing configuration
def _init_configuration():
    with open('./configuration/cloudwatch.yml', 'r+') as cloudwatch_file:
        with open('./configuration_raw/cloudwatch_raw.yml', 'r+') as raw_file:
            raw_yaml = yaml.safe_load(raw_file)
        _dump_and_close_file(raw_yaml, cloudwatch_file)
    with open('./configuration/otel.yml', 'r+') as otel_file:
        with open('./configuration_raw/otel_raw.yml', 'r+') as raw_file:
            raw_yaml = yaml.safe_load(raw_file)
        _dump_and_close_file(raw_yaml, otel_file)

# Expose api endpoints using flask
def _expose_configuration():
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    api.app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    api.app.run(host='0.0.0.0', port=5001)


logger = _create_logger()
_init_configuration()
_update_otel_config()
if CUSTOM_CONFIG_PATH:
    _load_aws_custom_config()
else:
    _add_cloudwatch_config()
_expose_configuration()
