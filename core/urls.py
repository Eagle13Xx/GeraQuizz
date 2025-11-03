from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_material, name='upload_material'),

    path('quiz/<int:material_id>/', views.iniciar_quiz, name='iniciar_quiz'),

    path('quiz/<int:material_id>/submeter/', views.submeter_quiz, name='submeter_quiz'),

    path('revisao/<int:tentativa_id>/', views.revisar_tentativa, name='revisar_tentativa'),

    path('', views.home, name='home'),

    path('historico/', views.historico_quiz, name='historico_quiz'),

    path('flashcards/<int:material_id>/', views.estudar_flashcards, name='estudar_flashcards'),
]