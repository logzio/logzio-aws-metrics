from flask import Flask
from ruamel.yaml import YAML

app = Flask(__name__)


@app.route('/')
def home():
    return '<p><a href=config/otel>Opentelemtry config</a></p>' \
           '<p><a href=config/cloudwatch>Cloudwatch config</a></p>'

# expose opentelemtry configuration
@app.route('/config/otel')
def get_otel_config():
    with open('../configuration/otel.yml', 'r') as otel_file:
        yaml = YAML()
        return yaml.load(otel_file)

# expose cloudwatch exporter configuration
@app.route('/config/cloudwatch')
def get_cw_config():
    with open('../configuration/cloudwatch.yml', 'r') as otel_file:
        yaml = YAML()
        return yaml.load(otel_file)
