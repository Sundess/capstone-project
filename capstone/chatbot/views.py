import subprocess
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect


# Create your views here.

# from django.http import JsonResponse
# from .rag_chat import load_json_to_documents, chat_with_rag


# def chat_endpoint(request):
#     if request.method == "POST":
#         query = request.POST.get("query", "List of product")
#         if not query:
#             return JsonResponse({"error": "Query cannot be empty."}, status=400)

#         # Load JSON data and documents
#         documents = load_json_to_documents('product_reviews.json')

#         # Get response from RAG
#         answer = chat_with_rag(query, documents)
#         return render(request, 'pages/chatpage.html', {"answer": answer})

#     return render(request, 'pages/chatpage.html')


def streamlit_view(request):
    # Path to your Streamlit script
    streamlit_script_path = 'streamlit.py'

    # Run Streamlit as a subprocess
    subprocess.Popen(['streamlit', 'run', streamlit_script_path])

    return HttpResponse("Streamlit app is running!")


# def streamlit_view(request):
#     # URL of the Streamlit app
#     streamlit_url = 'http://127.0.0.1:8501'  # or the deployed Streamlit URL

#     # Redirect to Streamlit app
#     return HttpResponseRedirect(streamlit_url)
