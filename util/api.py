from flask import Flask
import yaml

app = Flask(__name__)
@app.route('/')
def home():
    return '<p><a href=config/otel>Opentelemtry configuration</a></p>' \
           '<p><a href=config/cloudwatch>Cloudwatch configuration</a></p>'


# expose opentelemtry configuration
@app.route('/config/otel')
def get_otel_config():
    with open('../configuration/otel.yml', 'r') as otel_file:
        otel_yaml = yaml.safe_load(otel_file)
        return f'<pre style="word-wrap: break-word; white-space: pre-wrap;">{yaml.dump(otel_yaml)}</pre> '

# expose cloudwatch exporter configuration
@app.route('/config/cloudwatch')
def get_cw_config():
    with open('../configuration/cloudwatch.yml',
              'r') as cloudwatch_file:
        cloudwatch_yaml = yaml.safe_load(cloudwatch_file)
        return f'<pre style="word-wrap: break-word; white-space: pre-wrap;">{yaml.dump(cloudwatch_yaml)}</pre> '
