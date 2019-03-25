from django import forms
import datetime
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

from survey.models import Buildings, Contractors, KIND_SURVEY, INDUSTRY_CONTR, Survey, PdfFile


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
    survey_date = forms.DateField(label="data przegladu", widget=forms.DateInput(attrs={'class': 'formIn'}))
    description = forms.CharField(label="opis", widget=forms.Textarea, required=False)
    contractor = ContractorsChoiceField(label="wykonawca", queryset=Contractors.objects.all(),
                                        widget=forms.Select(attrs={'class': 'formIn'}),
                                        help_text="  wybierz wykonawcę z listy lub utwórz nowego:")
    pdf=forms.FileField(label="plik .pdf", required=False)



class AddContractorsForm(forms.Form):
    name = forms.CharField(max_length=48, widget=forms.TextInput(attrs={'class': 'formIn', 'size': '48'}),
                           label="nazwa wykonawcy")
    phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': 'formIn', 'size': '12'}),
                            label="numer telefonu", required=False)
    mail = forms.CharField(max_length=24, widget=forms.EmailInput(attrs={'class': 'formIn', 'size': '24'}),
                           label='e-mail', required=False)
    industry = forms.ChoiceField(choices=INDUSTRY_CONTR, label='branża', widget=forms.Select(attrs={'class': 'formIn'}))


class SurveyChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class AddExecutionForm(forms.Form):
    survey = SurveyChoiceField(label="Dla przeglądu:", queryset=Survey.objects.all(), widget=forms.HiddenInput)
    date = forms.DateField(label="Data:", widget=forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD', 'size': '10'}))
    description = forms.CharField(label="Opis:", widget=forms.Textarea)

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
            raise ValidationError("Data protokołu naprawy jest jest później niż dzisiaj")
        return cleaned_data


class PdfModelForm(forms.ModelForm):
    class Meta:
        model = PdfFile
        fields = ['name', 'pdf']
