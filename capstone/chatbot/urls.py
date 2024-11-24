from django.urls import path
from . import views

urlpatterns = [
    # path("", views.chat_endpoint, name="chat_endpoint"),
    path('launch_streamlit/', views.streamlit_view, name='launch_streamlit'),

]
