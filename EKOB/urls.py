"""EKOB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from survey.views import AddSurveyView, AddContractorView, ShowSurveysView, UpdateSurvey, SurveyDelete, \
    ShowContractorsView, AddExecutionView, AddPdfFileView, ShowPdfFilesView, ReadPdf, StartView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', StartView.as_view()),
    path('addsurvey/', AddSurveyView.as_view(), name='new_survey'),
    path('addcontractor/', AddContractorView.as_view(), name='new_contractor'),
    path('surveys/', ShowSurveysView.as_view(), name='list_surveys'),
    path('surveys/<int:survey_id>/', UpdateSurvey.as_view()),
    path('surveys/delete/<int:survey_id>/', SurveyDelete.as_view()),
    path('surveys/execution/<int:survey_id>/', AddExecutionView.as_view()),
    path('surveys/pdf/<str:pdf>/', ReadPdf.as_view(), name='show_pdf'),
    path('contractors/', ShowContractorsView.as_view(), name='list_contractors'),



    path('addfile/', AddPdfFileView.as_view()),
    path('pdf/', ShowPdfFilesView.as_view()),





]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
