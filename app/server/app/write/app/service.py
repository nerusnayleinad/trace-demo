import mysql.connector
from mysql.connector import Error

from flask import Flask
from flask import request, redirect, url_for

import socket
import os
import sys
import requests
import argparse
from random import randint
import time

from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
import opencensus.trace.tracer

app = Flask(__name__)

names = [
    'Homer',
    'Bart',
    'Maggie',
    'Marge',
    'Lisa',
    'Moe',
    'Krusty',
    'Apu',
    'Ned',
    'Barney',
    'Skinner',
    'Wiggum',
    'Lenny',
    'Carl',
    'Agnes'
]

surnames = [
    'Agassi',
    'Sampras',
    'Muster',
    'Ivanisevic',
    'Becker',
    'Rafter',
    'Philippoussis',
    'Kuerten',
    'Connors',
    'Borg',
    'Lendl',
    'Henman',
    'Kafelnikov',
    'Edberg',
    'Noah'
]

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


def write(connection, table, name, surname):
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
    
    query = "INSERT INTO {} (Name, Surname) VALUES (%s, %s);".format(table)
    values = (name, surname)
    result = cursor.execute(query, values)
    connection.commit()
    
    query = "SELECT * FROM {} ORDER  BY id DESC LIMIT 1".format(table)
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

@app.route('/write/<trace_id>')
def insert(trace_id):
    conn = connect()
    tracer = initialize_tracer(project_id, trace_id)
    app.config['TRACER'] = tracer
    table = os.environ['TABLE']
    name = names[randint(0, 14)]
    surname = surnames[randint(0, 14)]
    tracer = app.config['TRACER']
    tracer.start_span(name='database')
    db_content = write(conn, table, name, surname)
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