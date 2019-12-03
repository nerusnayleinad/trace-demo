from flask import Flask
from flask import request
import requests
import os

from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
import opencensus.trace.tracer

app = Flask(__name__)

def initialize_tracer(project_id):
    exporter = stackdriver_exporter.StackdriverExporter(project_id=project_id)
    sampler=opencensus.trace.tracer.samplers.AlwaysOnSampler()
    
    tracer = opencensus.trace.tracer.Tracer(
        exporter=exporter,
        sampler=sampler
    )

    return tracer

@app.route('/dump')
def dump():
    tracer = app.config['TRACER']
    tracer.start_span(name='dump')
    url = "http://db-dump/dump/" + trace_id
    result = requests.get(url)
    tracer.end_span()
    
    return result.content

@app.route('/read/<name>')
def read(name):
    tracer = app.config['TRACER']
    tracer.start_span(name='read')
    url = "http://db-read/read/" + trace_id + "/" + name
    result = requests.get(url)
    tracer.end_span()
    
    return result.content

@app.route('/write')
def write():
    tracer = app.config['TRACER']
    tracer.start_span(name='write')
    url = "http://db-write/write/" + trace_id
    result = requests.get(url)
    tracer.end_span()
    
    return result.content

if __name__ == "__main__":
    project_id = os.environ['PROJECT']
    tracer = initialize_tracer(project_id)
    app.config['TRACER'] = tracer
    trace_id = tracer.span_context.trace_id
    
    app.run(host='0.0.0.0', port=8080, debug=True)