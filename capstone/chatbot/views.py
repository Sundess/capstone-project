import os
import subprocess
from django.http import HttpResponse, HttpResponseRedirect
from .models import export_data_to_json


def streamlit_view(request):
    print('Here')
    export_data_to_json()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    streamlit_script_path = os.path.join(base_dir, 'chatbot', 'streamlit.py')

    if not os.path.exists(streamlit_script_path):
        return HttpResponse("Error: Streamlit script not found at the specified path.")

    # Use a custom port to avoid conflicts
    streamlit_port = 8505
    streamlit_url = f'http://localhost:{streamlit_port}/'

    try:
        process = subprocess.Popen(
            ['streamlit', 'run', streamlit_script_path,
                '--server.port', str(streamlit_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate(timeout=5)
        print(f"Streamlit script path: {streamlit_script_path}")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
    except subprocess.SubprocessError as e:
        print(f"Subprocess error: {e}")
    except Exception as e:
        print(f"General error: {e}")

    return HttpResponseRedirect(streamlit_url)
