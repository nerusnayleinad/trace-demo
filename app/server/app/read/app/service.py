import mysql.connector
from mysql.connector import Error

from flask import Flask
from flask import request, redirect, url_for

import socket
import os
import sys
import requests

from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
import opencensus.trace.tracer

app = Flask(__name__)

def initialize_tracer(project_id, trace_id):
    exporter = stackdriver_exporter.StackdriverExporter(project_id=project_id)
    sampler=opencensus.trace.tracer.samplers.AlwaysOnSampler()
    span_context = opencensus.trace.tracer.SpanContext(trace_id)
    
    tracer = opencensus.trace.tracer.Tracer(
        exporter=exporter,
        sampler=sampler,
        span_context=span_context
    )

    return tracer

def connect():
    host = os.environ['HOST']
    database = os.environ['DATABASE']
    user = os.environ['USER']
    password = os.environ['PASSWORD']

    connection = mysql.connector.connect(host=host,
                                         database=database,
                                         user=user,
                                         password=password)

    return connection

def read(connection, name):
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        database = cursor.fetchone()[0]
        print("You're connected to database: ", database)

    query = "SELECT * FROM {} where name = '{}'".format(database, name)
    cursor.execute(query)
    result = cursor.fetchall()

    return result

def format(db_raw_content):
    db_content_to_print = '<span><table style="border: 1px solid black; color:white; font-size:1em;">'
    for item in db_raw_content:
        raw = ''
        for i in item:
            raw = raw + '<td style="border: 1px solid black; padding: 8px;">' + str(i) + '</td>'

        db_content_to_print = db_content_to_print + '<tr>' + raw + '</tr>'

    db_content_to_print = db_content_to_print + '</table></span>'
    return db_content_to_print

def render_page(database):
    return ('<body bgcolor="black"><span style="color:white;font-size:4em;">\n'
            'Hello from {} (hostname: {} resolvedhostname:{})\n</span></br>\n\n'
            '<span style="color:white;font-size:1.5em;">\n\n'
            'Your database content is: </br>\n</span>\n\n'
            '{}</body>\n'.format(
                    os.environ['SERVICE_NAME'],
                    socket.gethostname(),
                    socket.gethostbyname(socket.gethostname()),
                    database))

@app.route('/read/<trace_id>/<name>')
def select(trace_id, name):
    conn = connect()
    tracer = initialize_tracer(project_id, trace_id)
    app.config['TRACER'] = tracer
    tracer.start_span(name='database')
    db_content = read(conn, name)
    tracer.end_span()
    db_content_to_print = format(db_content)

    return render_page(db_content_to_print)

try:
    connection = connect()
    project_id = os.environ['PROJECT']
    
    app.run(host='127.0.0.1', port=8080, debug=True)

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")