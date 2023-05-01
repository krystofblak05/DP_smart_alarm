import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd

#Ukládání vygenerovaného grafu do PNG pro možné zobrazení na webu

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

#Generování jednotlivých grafů

def get_temp_plot(id):
    plt.switch_backend('AGG')
    df = pd.read_csv('static/csv/' + str(id) + '.csv')
    df.plot(x='datum', y='temp')
    plt.xlabel('Čas')
    plt.ylabel('Teplota (C)')
    plt.tight_layout()
    graph = get_graph()
    return graph

def get_hum_plot(id):
    plt.switch_backend('AGG')
    df = pd.read_csv('static/csv/' + str(id) + '.csv')
    df.plot(x='datum', y='hum')
    plt.xlabel('Čas')
    plt.ylabel('Vlhkost (%)')
    plt.tight_layout()
    graph = get_graph()
    return graph

def get_noise_plot(id):
    plt.switch_backend('AGG')
    df = pd.read_csv('static/csv/' + str(id) + '.csv')
    df.plot(x='datum', y='noise')
    plt.xlabel('Čas')
    plt.ylabel('Hluk')
    plt.tight_layout()
    graph = get_graph()
    return graph

def get_light_plot(id):
    plt.switch_backend('AGG')
    df = pd.read_csv('static/csv/' + str(id) + '.csv')
    df.plot(x='datum', y='light')
    plt.xlabel('Čas')
    plt.ylabel('Světelnost')
    plt.tight_layout()
    graph = get_graph()
    return graph