import os
import shutil
from calendar import monthrange

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.signals import post_delete
from django.dispatch import receiver

from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

from django.views import View
from django.views.generic import UpdateView, DeleteView
import datetime

from survey.filters import SurveyFilter
from survey.forms import AddSurveyForm, AddContractorsForm, AddExecutionForm, LoginForm, RegistrationForm, \
    ScheduleForm, SendMailForm, SurveyForm, RenovationsForm, ContractRenovationForm, ExecutRenovationForm
from survey.functions import validity_date, length_valid, check_open_survey, read_pdf
from survey.messages import text_message, delete_message
from survey.models import Buildings, Survey, Contractors, Execution, Renovations, ContractRenovation, ExecutRenovation

from weasyprint import HTML, CSS

TO_CONTRACTOR = "to_contractor"


class AddSurveyView(View):
    def get(self, request):
        form = AddSurveyForm()
        request.session[TO_CONTRACTOR] = True
        return render(request, "add_survey.html", {"form": form})

    def post(self, request):
        form = AddSurveyForm(request.POST, request.FILES)

        if form.is_valid():
            del (request.session[TO_CONTRACTOR])
            building = form.cleaned_data['building']
            kind = form.cleaned_data['kind']
            description = form.cleaned_data['description']
            contractor = form.cleaned_data['contractor']
            survey_date = form.cleaned_data['survey_date']
            pdf = form.cleaned_data['pdf']

            is_open_value = check_open_survey(Survey, building, kind, survey_date)

            valid_date = validity_date(survey_date, length_valid(int(kind)))
            Survey.objects.create(building=building, kind=kind, survey_date=survey_date,
                                  description=description, valid_date=valid_date, is_open=is_open_value,
                                  contractor=contractor, pdf=pdf)

            return HttpResponseRedirect('/surveys')
        else:
            return render(request, 'add_survey.html', {"form": form})


class AddBuildingView(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class AddContractorView(View):
    h2_ctx = 'Wprowadź nowego wykonawcę'

    def get(self, request):
        form = AddContractorsForm()
        return render(request, "add_elements_surfey.html", {"form": form, 'h2_ctx': self.h2_ctx})

    def post(self, request):
        form = AddContractorsForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            mail = form.cleaned_data['mail']
            industry = form.cleaned_data['industry']
            Contractors.objects.create(name=name, phone=phone, mail=mail, industry=industry)
            if request.session.get(TO_CONTRACTOR):
                return HttpResponseRedirect('/addsurvey')
            else:
                return HttpResponseRedirect('/contractors')
        else:
            return render(request, "add_elements_surfey.html", {"form": form, 'h2_ctx': self.h2_ctx})


class AddExecutionView(View):

    def get(self, request, survey_id):
        initial_survey = get_object_or_404(Survey, id=survey_id)
        form = AddExecutionForm(initial={"survey": initial_survey})
        h2_ctx = 'Wprowadź wykonanie zaleceń do przegladu: {}'.format(initial_survey)
        return render(request, "add_elements_surfey.html", {"form": form, 'h2_ctx': h2_ctx})

    def post(self, request, survey_id):
        form = AddExecutionForm(request.POST)
        initial_survey = Survey.objects.get(id=survey_id)
        h2_ctx = 'Wprowadź wykonanie zaleceń do przegladu: {}'.format(initial_survey)

        if form.is_valid():
            date = form.cleaned_data['date']
            description = form.cleaned_data['description']
            survey = form.cleaned_data['survey']
            Execution.objects.create(date=date, description=description, survey=survey)
            return HttpResponseRedirect('/surveys')
        else:
            return render(request, "add_elements_surfey.html", {"form": form, 'h2_ctx': h2_ctx})


class AddRenovationsView(View):
    h2_ctx = 'Wprowadź nowy remont'

    def get(self, request):
        form = RenovationsForm()
        return render(request, "add_renovation.html", {"form": form, 'h2_ctx': self.h2_ctx})

    def post(self, request):
        form = RenovationsForm(request.POST, request.FILES)

        if form.is_valid():
            building = form.cleaned_data['building']
            description = form.cleaned_data['description']
            new_renovation = Renovations.objects.create(building=building, description=description)
            os.mkdir(os.path.join('media/renovation', str(new_renovation.id)))
            return HttpResponseRedirect('/renovations')
        else:
            return render(request, "add_renovation.html", {"form": form, 'h2_ctx': self.h2_ctx})


class AddContractRenovationView(View):

    def get(self, request, renovation_id):
        renovation = get_object_or_404(Renovations, id=renovation_id)
        h2_ctx = 'Dodaj umowę/zezwolenie dla remontu {}... w budynku {}'.format(renovation.description[:25],
                                                                                renovation.building)
        form = ContractRenovationForm(initial={"renovation": renovation_id})
        return render(request, "add_renovation.html", {'form': form, 'h2_ctx': h2_ctx})

    def post(self, request, renovation_id):
        form = ContractRenovationForm(request.POST, request.FILES)
        renovation = Renovations.objects.get(id=renovation_id)
        h2_ctx = 'Dodaj umowę/zezwolenie dla remontu {}... w budynku {}'.format(renovation.description[:25],
                                                                                renovation.building)

        if form.is_valid():
            renovation = form.cleaned_data['renovation']
            kind = form.cleaned_data['kind']
            number = form.cleaned_data['number']
            date = form.cleaned_data['date']
            description = form.cleaned_data['description']
            contract_pdf = form.cleaned_data['contract_pdf']

            ContractRenovation.objects.create(renovation_id=renovation, kind=kind, number=number, date=date,
                                              description=description, contract_pdf=contract_pdf)
            return HttpResponseRedirect('/renovations/' + str(renovation))
        else:
            return render(request, "add_renovation.html", {"form": form, 'h2_ctx': h2_ctx})


class AddExecutRenovationView(View):
    def get(self, request, renovation_id):
        if ExecutRenovation.objects.all().filter(renovation_id=renovation_id).exists():
            return HttpResponse('Realizacja dla tego remontu została już wprowadzona. możesz edytować dane')
        else:
            renovation = get_object_or_404(Renovations, id=renovation_id)
            form = ExecutRenovationForm(initial={"renovation": renovation_id})
            h2_ctx = 'Realizacja remontu {}... w budynku {}'.format(renovation.description[:25],
                                                                    renovation.building)
            return render(request, 'add_renovation.html', {'form': form, 'h2_ctx': h2_ctx})

    def post(self, request, renovation_id):
        form = ExecutRenovationForm(request.POST, request.FILES)
        renovation = Renovations.objects.get(id=renovation_id)
        h2_ctx = 'Realizacja remontu {}... w budynku {}'.format(renovation.description[:25],
                                                                renovation.building)
        if form.is_valid():
            contractor = form.cleaned_data['contractor']
            surveyor = form.cleaned_data['surveyor']
            start = form.cleaned_data['start']
            termination = form.cleaned_data['termination']
            termination_pdf = form.cleaned_data['termination_pdf']
            description = form.cleaned_data['description']
            renovation = form.cleaned_data['renovation']
            ExecutRenovation.objects.create(contractor=contractor, surveyor=surveyor, start=start,
                                            termination=termination, termination_pdf=termination_pdf,
                                            description=description, renovation_id=renovation)
            return HttpResponseRedirect('/renovations/' + str(renovation))
        else:
            return render(request, "add_renovation.html", {"form": form, 'h2_ctx': h2_ctx})


class ShowSurveysView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        survey_filter = SurveyFilter(request.GET, queryset=Survey.objects.all().order_by('-survey_date'))
        page = request.GET.get('page', 1)
        paginator = Paginator(survey_filter.qs, 10)
        try:
            survey_f = paginator.page(page)
        except PageNotAnInteger:
            survey_f = paginator.page(1)
        except EmptyPage:
            survey_f = paginator.page(paginator.num_pages)

        today = datetime.datetime.today()
        executions = Execution.objects.all()
        self.raport_to_pdf_view(request, survey_filter, today)
        return render(request, "surveys.html",
                      {'filter': survey_filter, "paginator": survey_f, "today": today, 'execution': executions})

    def raport_to_pdf_view(self, request, surveys, today):

        html_string = render_to_string('pdf_template.html', {'surveys': surveys, 'today': today})
        html = HTML(string=html_string)
        html.write_pdf(target='media/pdf_report/survey_report.pdf', stylesheets=[CSS('survey/static/css/PDFstyle.css')])


class ShowContractorsView(View):
    def get(self, request):
        contractors = Contractors.objects.all()
        return render(request, 'contractors.html', {"contractors": contractors})


class ShowRenovationsView(View):
    def get(self, request):
        renovations = Renovations.objects.all().order_by("building")
        return render(request, 'renovations.html', {"renovations": renovations})


class ShowOneRenovationView(View):

    def get(self, request, renovation_id):
        renovation = get_object_or_404(Renovations, id=renovation_id)
        try:
            contracts = ContractRenovation.objects.all().filter(renovation_id=renovation_id).order_by('date')
        except:
            contracts = False
        try:
            execution = ExecutRenovation.objects.get(renovation_id=renovation_id)
        except:
            execution = False
        return render(request, 'one_renovation.html',
                      {"renovation": renovation, 'contracts': contracts, 'execution': execution})


class ScheduleView(View):
    def get(self, request):

        building = request.GET.get('building')
        scope = request.GET.get('scope')
        form = ScheduleForm(initial={"building": building, "scope": scope})
        today = datetime.date.today()
        surveys = Survey.objects.filter(is_open=True).order_by("valid_date")

        if building or scope:
            if not building:
                building = [building.id for building in (Buildings.objects.all())]

            month = today.month
            year = today.year
            if scope == "quarter":
                month += 3
                if month > 12:
                    month -= 12
                    year += 1
                max_day = monthrange(year, month)[1]
                end_of_scope = datetime.date(year, month, max_day)

                surveys = surveys.filter(is_open="True", building__in=building,
                                         valid_date__lte=end_of_scope).order_by("valid_date")

            if scope == "end_of_year":
                end_of_scope = datetime.date(year, 12, 31)
                surveys = surveys.filter(is_open="True", building__in=building,
                                         valid_date__lte=end_of_scope).order_by("valid_date")
            if scope == "only_next_year":
                start_new_year = datetime.date((year + 1), 1, 1)
                end_of_scope = datetime.date((year + 1), 12, 31)
                surveys = surveys.filter(is_open="True", building__in=building,
                                         valid_date__lte=end_of_scope,
                                         valid_date__gte=start_new_year).order_by("valid_date")

        text = text_message(surveys, today)
        form_mail = SendMailForm(initial={'message': text, "subject": "zlecenie przeglądu"})

        return render(request, "schedule.html", {"form": form, "surveys": surveys, "form_mail": form_mail})

    def post(self, request):

        form_mail = SendMailForm(request.POST)
        surveys = Survey.objects.filter(is_open="True").order_by("valid_date")
        form = ScheduleForm()

        if form_mail.is_valid():
            subject = form_mail.cleaned_data['subject']
            message = form_mail.cleaned_data['message']
            address = form_mail.cleaned_data['address']
            send_mail(
                subject,
                message,
                'ekob_info@wp.pl',
                [address.mail],
            )
            return HttpResponseRedirect('/surveys')
        else:

            return render(request, "schedule.html",
                          {"form": form, "surveys": surveys, "form_mail": form_mail})


class UpdateSurvey(UpdateView):
    model = Survey
    fields = ['building', 'kind', 'description', 'survey_date', 'valid_date', 'is_open', 'contractor', 'pdf']
    template_name_suffix = '_update_form'
    pk_url_kwarg = 'survey_id'

    def get_success_url(self):
        return "/surveys/"

    def get_form(self, form_class=SurveyForm):
        form = super(UpdateSurvey, self).get_form(form_class)
        form.fields['description'].required = False
        form.fields['pdf'].required = False

        return form


class SurveyDeleteView(DeleteView):
    model = Survey
    pk_url_kwarg = 'survey_id'

    def get_success_url(self):
        return "/surveys/"


class ContractorDeleteView(View):
    def get(self, request, contractor_id):
        contractor = get_object_or_404(Contractors, id=contractor_id)
        surveys = Survey.objects.filter(contractor=contractor_id)
        message = delete_message(surveys)
        return render(request, "survey/contractors_confirm_delete.html",
                      {'contractor': contractor, 'surveys': surveys, 'message': message})

    def post(self, request, contractor_id):
        delete_contractor = Contractors.objects.get(id=request.POST.get('delete'))
        delete_contractor.delete()
        return HttpResponseRedirect("/contractors")

    @receiver(post_delete, sender=Survey)
    def auto_delete_file_on_delete(sender, instance, **kwargs):
        if instance.pdf:
            if os.path.isfile(instance.pdf.path):
                os.remove(instance.pdf.path)


class RenovationDeleteView(View):
    def get(self, request, renovation_id):
        renovation = get_object_or_404(Renovations, id=renovation_id)
        return render(request, "survey/renovations_confirm_delete.html", {'renovation': renovation})

    def post(self, request, renovation_id):
        if os.path.isdir('media/renovation/' + str(renovation_id)):
            shutil.rmtree('media/renovation/' + str(renovation_id))
        delete_renovations = Renovations.objects.get(id=renovation_id)
        delete_renovations.delete()
        return HttpResponseRedirect("/renovations")


# =========================== FILES SECTION =====================

class ReadPdfView(View):
    def get(self, request, pdf):
        path_dic = "media/pdf/"
        return read_pdf(pdf, path_dic)


class ReadRenovationPdfView(View):
    def get(self, request, pdf, renovation_id):
        path_dic = "media/renovation/{}/".format(renovation_id)
        return read_pdf(pdf, path_dic)


def display_survey_pdf_raport(request):
    path_dic = 'media/pdf_report/'
    pdf = 'survey_report.pdf'
    return read_pdf(pdf, path_dic)


# ==================LOGIN SECTION=======================

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "index.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/surveys')
            else:
                return render(request, 'index.html', {'form': form, 'msg': 'błędne dane logowania'})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


class RegistrationView(View):

    def get(self, request):
        form = RegistrationForm()
        return render(request, "add_elements_surfey.html", {"form": form})  # todo zmienić template

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            User.objects.create_user(username=username, password=password, email=email)
            return HttpResponseRedirect('/')
