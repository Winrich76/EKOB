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
    ShowContractorsView, AddExecutionView, ReadPdf, LoginView, logout_view, RegistrationView, ScheduleView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', LoginView.as_view(), name="index"),
                  path('logout/', logout_view),
                  path('registration/', RegistrationView.as_view(), name='registration'),

                  path('addsurvey/', AddSurveyView.as_view(), name='new_survey'),
                  path('addcontractor/', AddContractorView.as_view(), name='new_contractor'),
                  path('surveys/', ShowSurveysView.as_view(), name='list_surveys'),
                  path('surveys/<int:survey_id>/', UpdateSurvey.as_view()),
                  path('surveys/delete/<int:survey_id>/', SurveyDelete.as_view()),
                  path('surveys/execution/<int:survey_id>/', AddExecutionView.as_view()),
                  path('surveys/pdf/<str:pdf>/', ReadPdf.as_view(), name='show_pdf'),
                  path('contractors/', ShowContractorsView.as_view(), name='list_contractors'),
                  path('schedule/', ScheduleView.as_view()),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
