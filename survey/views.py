import os

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
import datetime
from django.http import FileResponse

from survey.filters import SurveyFilter
from survey.forms import AddSurveyForm, AddContractorsForm, AddExecutionForm, PdfModelForm
from survey.functions import validity_date, length_valid, check_open_survey
from survey.models import Buildings, Survey, Contractors, Execution, PdfFile


class AddSurveyView(View):
    def get(self, request):
        form = AddSurveyForm()
        request.session["contr"] = True
        return render(request, "add_survey.html", {"form": form})


    def post(self, request):
        form = AddSurveyForm(request.POST, request.FILES)
        del(request.session["contr"])
        if form.is_valid():
            building = form.cleaned_data['building']
            kind = form.cleaned_data['kind']
            description = form.cleaned_data['description']
            contractor = form.cleaned_data['contractor']
            survey_date = form.cleaned_data['survey_date']
            pdf = form.cleaned_data['pdf']

            check_open_survey(Survey, building, kind)

            valid_date = validity_date(survey_date, length_valid(int(kind)))
            Survey.objects.create(building=building, kind=kind, survey_date=survey_date, \
                                  description=description, valid_date=valid_date, is_open=True, \
                                  contractor=contractor, pdf=pdf)

            return HttpResponseRedirect('/surveys')

        return render(request, 'add_elements_surfey.html', {"form": form})



class AddBuildingView(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class AddContractorView(View):
    h2_ctx = 'Wprowadź nowego wykonawcę'
    def get(self, request):
        form=AddContractorsForm()
        return render(request, "add_elements_surfey.html", {"form": form, 'h2_ctx':self.h2_ctx})

    def post(self, request):
        form = AddContractorsForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone=form.cleaned_data['phone']
            mail=form.cleaned_data['mail']
            industry=form.cleaned_data['industry']
            Contractors.objects.create(name=name, phone=phone, mail=mail, industry=industry)
            if request.session.get("contr"):
                return HttpResponseRedirect('/addsurvey')
            else:
                return HttpResponseRedirect('/contractors')
        else:
            return render(request, "add_elements_surfey.html", {"form": form, 'h2_ctx':self.h2_ctx})

class AddExecutionView(View):


    def get(self, request, survey_id):
        initial_survey=Survey.objects.get(id=survey_id)
        form=AddExecutionForm(initial={"survey": initial_survey})
        h2_ctx = 'Wprowadź wykonanie zaleceń do przegladu: {}'.format(initial_survey)
        return render(request, "add_elements_surfey.html", {"form": form, 'h2_ctx':h2_ctx})

    def post(self, request, survey_id):
        form=AddExecutionForm(request.POST)
        initial_survey = Survey.objects.get(id=survey_id)
        h2_ctx = 'Wprowadź wykonanie zaleceń do przegladu: {}'.format(initial_survey)

        if form.is_valid():
            date=form.cleaned_data['date']
            description=form.cleaned_data['description']
            survey=form.cleaned_data['survey']
            Execution.objects.create(date=date, description=description, survey=survey)
            return HttpResponseRedirect('/surveys')
        else:
            return render(request, "add_elements_surfey.html", {"form": form, 'h2_ctx':h2_ctx})



class ShowSurveysView(View):
    def get(self, request):
        survey_filter = SurveyFilter(request.GET, queryset=Survey.objects.all().order_by('-survey_date'))
        page=request.GET.get('page',1)
        paginator=Paginator(survey_filter.qs, 10)

        try:
            survey_f = paginator.page(page)
        except PageNotAnInteger:
            survey_f = paginator.page(1)
        except EmptyPage:
            survey_f = paginator.page(paginator.num_pages)

        today = datetime.datetime.today()
        executions=Execution.objects.all()

        return render(request, "surveys.html", {'filter': survey_filter, "paginator":survey_f, "today": today,  'execution':executions})




class ShowContractorsView(View):
    def get(self, request):
        contractors=Contractors.objects.all()
        return render(request, 'contractors.html', {"contractors":contractors})





class UpdateSurvey(UpdateView):
    model=Survey
    fields = ['building', 'kind', 'description', 'survey_date', 'valid_date', 'is_open', 'contractor', 'pdf']
    template_name_suffix= '_update_form'
    pk_url_kwarg = 'survey_id'

    def get_success_url(self):
        return "/surveys/"



class SurveyDelete(DeleteView):
    model=Survey
    pk_url_kwarg = 'survey_id'

    def get_success_url(self):
        return "/surveys/"



class AddPdfFileView(View):
    def get(self, request):
        form = PdfModelForm()
        return render(request, 'test.html', {'form': form})

    def post(self, request):
        form = PdfModelForm(request.POST, request.FILES)

        if form.is_valid():
           name=form.cleaned_data['name']
           pdf=form.cleaned_data['pdf']
           PdfFile.objects.create(name=name, pdf=pdf)

           return HttpResponse('wczytano plik {} pdf {}'.format(name, pdf))
        else:
            return render(request, 'test.html', {'form': form})

class ShowPdfFilesView(View):
    def get(self, request):
        pdf_files = PdfFile.objects.all()
        return render(request, 'test1.html', {'files': pdf_files})


class ReadPdf(View):
    def get(self, request, pdf):
        file_path = "media/pdf/"+pdf
        with open(file_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename='+file_path
        return response

class StartView(View):
    def get(self, request):
        return render(request, "index.html", {})


