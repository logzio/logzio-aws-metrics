import os
SCRAPE_INTERVAL = f'{os.environ["SCRAPE_INTERVAL"]}s'
aws = {
    'job_name': 'logzio-cloudwatch',
    'scrape_interval': SCRAPE_INTERVAL,
    'scrape_timeout': SCRAPE_INTERVAL,
    'static_configs': [{
        'targets': ['cloudwatch-exporter:9106']
    }]
}

azure = {

}
