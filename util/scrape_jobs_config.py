import os
SCRAPE_INTERVAL = f'{os.environ["SCRAPE_INTERVAL"]}s'
aws = {
    'job_name': 'logzio-cloudwatch-metrics',
    'scrape_interval': SCRAPE_INTERVAL,
    'scrape_timeout': SCRAPE_INTERVAL,
    'static_configs': [{
        'targets': ['cloudwatch-exporter:9106']
    }]
}

azure = {

}
