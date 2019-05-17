from django import forms
import datetime
from django.core.exceptions import ValidationError

from survey.models import Buildings, Contractors, KIND_SURVEY, INDUSTRY_CONTR, Survey, PdfFile, Renovations, \
    KIND_DEPOSIT

year = datetime.date.today().year


class BuildingChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class ContractorsChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class AddSurveyForm(forms.Form):
    building = BuildingChoiceField(label="budynek", queryset=Buildings.objects.all(),
                                   widget=forms.Select(attrs={'class': 'formIn'}))
    kind = forms.ChoiceField(label="typ przegladu", choices=KIND_SURVEY, widget=forms.Select(attrs={'class': 'formIn'}))
    survey_date = forms.DateField(label="data przegladu",
                                  widget=forms.SelectDateWidget(years=range((year - 5), (year + 1)),
                                                                attrs={'class': 'formIn'}))
    description = forms.CharField(label="opis",
                                  widget=forms.Textarea(attrs={'placeholder': 'Tu wpisz opis i zalecenia z przegladu'}),
                                  required=False)
    contractor = ContractorsChoiceField(label="wykonawca", queryset=Contractors.objects.all(),
                                        widget=forms.Select(attrs={'class': 'formIn'}),
                                        help_text="  wybierz wykonawcę z listy lub utwórz nowego:")
    pdf = forms.FileField(label="plik .pdf", required=False)


class AddContractorsForm(forms.Form):
    name = forms.CharField(max_length=48, widget=forms.TextInput(attrs={'class': 'formIn', 'size': '48'}),
                           label="nazwa wykonawcy")
    phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': 'formIn', 'size': '12'}),
                            label="numer telefonu", required=False)
    mail = forms.CharField(max_length=48, widget=forms.EmailInput(attrs={'class': 'formIn', 'size': '48'}),
                           label='e-mail', required=False)
    industry = forms.ChoiceField(choices=INDUSTRY_CONTR, label='branża', widget=forms.Select(attrs={'class': 'formIn'}))


class SurveyChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class AddExecutionForm(forms.Form):
    survey = SurveyChoiceField(label="Dla przeglądu:", queryset=Survey.objects.all(), widget=forms.HiddenInput)
    date = forms.DateField(label="Data:", widget=forms.SelectDateWidget(years=range((year - 5), (year + 1)),
                                                                        attrs={'class': 'formIn'}))
    description = forms.CharField(label="Opis:", widget=forms.Textarea(
        attrs={'placeholder': 'Tu wpisz prace zwiazane z usuwaniem usterek'}))

    def clean(self):
        cleaned_data = self.cleaned_data
        survey = cleaned_data.get("survey")
        date = cleaned_data.get("date")
        if not date:
            raise ValidationError("Niepoprawny format daty RRRR-MM-DD")
        today = datetime.date.today()
        if date < survey.survey_date:
            raise ValidationError("Wpisana data protokołu naprawy jest wcześniejsza niż data przeglądu")
        elif date > today:
            raise ValidationError("Data protokołu naprawy jeszcze nie nastąpiła")
        return cleaned_data


class PdfModelForm(forms.ModelForm):
    class Meta:
        model = PdfFile
        fields = ['name', 'pdf']


class LoginForm(forms.Form):
    username = forms.CharField(label="Nazwa użytkownika")
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)


class RegistrationForm(forms.Form):
    username = forms.CharField(label="Nazwa użytkownika")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    email = forms.CharField(label="adres e-mail", widget=forms.EmailInput)


SCOPE_SCHEDULE = (

    ("quarter", "kwartał"),
    ("end_of_year", "koniec roku"),
    ("only_next_year", "tylko przyszły rok")
)


class ScheduleForm(forms.Form):
    scope = forms.ChoiceField(choices=SCOPE_SCHEDULE, label="Przeglądy ważne do:")
    building = BuildingChoiceField(queryset=Buildings.objects.all(), required=False, empty_label='wszystkie',
                                   label="Budynek")


class ContractorsChoiceMailField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ("{} ----  {}".format(obj.name, obj.mail))


class SendMailForm(forms.Form):
    address = ContractorsChoiceMailField(queryset=Contractors.objects.exclude(mail=''), label="Wykonawca")
    subject = forms.CharField(label="Tytuł")
    message = forms.CharField(widget=forms.Textarea, label="Treść zlecenia")


class SurveyForm(forms.ModelForm):
    survey_date = forms.DateField(label="data przegladu",
                                  widget=forms.SelectDateWidget(years=range((year - 5), (year + 1))))
    valid_date = forms.DateField(label="ważny do", widget=forms.SelectDateWidget(years=range((year - 5), (year + 7))))

    class Meta:
        model = Survey
        fields = '__all__'


class RenovationsForm(forms.Form):
    building = BuildingChoiceField(label="budynek", queryset=Buildings.objects.all(),
                                   widget=forms.Select(attrs={'class': 'formIn'}))
    description = forms.CharField(label="Zakres robót",
                                  widget=forms.Textarea(attrs={'placeholder': 'Zakres robót'}))
    contractor = forms.CharField(max_length=256, label='Wykonawca')
    contract_number = forms.CharField(max_length=48,  label="Nr umowy")
    contract_date = forms.DateField(label="Data umowy",
                                    widget=forms.SelectDateWidget(years=range((year - 5), (year + 1)),
                                                                  attrs={'class': 'formIn'}))

    contract_pdf = forms.FileField(required=False, label="Umowa - pdf")
    building_permit_number = forms.CharField(max_length=48, label="Nr pozwolenia na budowę")
    building_permit_date = forms.DateField(label="Data pozwolenia ",
                                           widget=forms.SelectDateWidget(years=range((year - 5), (year + 1)),
                                                                         attrs={'class': 'formIn'}))
    permit_pdf = forms.FileField(required=False, label="Pozwolenie - pdf")
    start = forms.DateField(label='Data rozpoczęcia budowy',
                            widget=forms.SelectDateWidget(years=range((year - 5), (year + 1)),
                                                          attrs={'class': 'formIn'}))
    termination = forms.DateField(label='Data protokołu odbioru',
                                  widget=forms.SelectDateWidget(years=range((year - 5), (year + 1)),
                                                                attrs={'class': 'formIn'}))
    termination_pdf = forms.FileField(required=False, label="Protokół odbioru -pdf")

    guarantee = forms.DateField(label='Gwarancja', widget=forms.SelectDateWidget(years=range((year), (year + 11)),
                                                                                 attrs={'class': 'formIn'}))

    deposit = forms.FloatField(label='Kaucja')
    deposit_kind = forms.ChoiceField(choices=KIND_DEPOSIT, label="Kaucja potracona z faktury końcowej")

