import os
import shutil

from django.db import models
from django.http import HttpResponseRedirect


class Buildings(models.Model):
    name = models.CharField(max_length=48)
    description = models.TextField()

    def __str__(self):
        return self.name


INDUSTRY_CONTR = (
    (1, "Sanitarna"),
    (2, "Budowlana"),
    (3, "Ogólna")

)


class Contractors(models.Model):
    name = models.CharField(max_length=48)
    phone = models.CharField(max_length=12)
    mail = models.CharField(max_length=48)
    industry = models.IntegerField(choices=INDUSTRY_CONTR)

    def __str__(self):
        return self.name


KIND_SURVEY = (
    ("Podstawowe", (
        (10, "kominowy"),
        (14, "kominowy mech."),
        (12, "gazowy"),
        (13, "roczny budowlany"),
    )),
    ("PPOŻ", (
        (15, "ogólny ppoż"),
        (16, "sygnalizacji ppoż"),
        (17, "instal. tryskaczowej"),
    )),
    ("5 letnie", (
        (50, "5-elektryczny"),
        (51, "5-budowlany"),
    )),
    ("Inne", (
        (21, 'gazex'),
        (1, 'separator')
    )),
)


class Survey(models.Model):
    building = models.ForeignKey(Buildings, on_delete=models.CASCADE, verbose_name="Budynek:")
    kind = models.IntegerField(choices=KIND_SURVEY, verbose_name="Przegląd:")
    survey_date = models.DateField(verbose_name="Data:")
    valid_date = models.DateField(null=True, verbose_name="Ważny do:")
    description = models.TextField(null=True, verbose_name="Zalecenia:")
    is_open = models.BooleanField(null=True, verbose_name="Status")
    contractor = models.ForeignKey(Contractors, on_delete=models.CASCADE, verbose_name="Wykonawca")
    pdf = models.FileField(upload_to='pdf', null=True, verbose_name="Plik .pdf")

    @property
    def name(self):
        return "{} {}".format(self.survey_date, self.building)

    def __str__(self):
        return self.name

    def delete(self):
        if self.pdf:
            if os.path.isfile(self.pdf.path):
                os.remove(self.pdf.path)
        return super(Survey, self).delete()


class Execution(models.Model):
    date = models.DateField()
    description = models.TextField()
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)


class PdfFile(models.Model):
    name = models.CharField(max_length=255)
    pdf = models.FileField(upload_to='pdf')


class Renovations(models.Model):
    building = models.ForeignKey(Buildings, on_delete=models.CASCADE, verbose_name="Budynek:")
    description = models.TextField(verbose_name='Zakres remontu')


KIND_CONTRACT = (
    ('contract', 'Umowa'),
    ('annex', 'Aneks'),
    ('permit', 'zezwolenie')

)


def get_upload_path(instance, filename):
    return 'renovation/{}/{}'.format(instance.renovation.id, filename)


class ContractRenovation(models.Model):
    renovation = models.ForeignKey(Renovations, on_delete=models.CASCADE)
    kind = models.CharField(choices=KIND_CONTRACT, max_length=12)
    number = models.CharField(max_length=48, null=True, verbose_name="Nr umowy")
    date = models.DateField(verbose_name="Data umowy")
    description = models.TextField(verbose_name='Przedmiot umowy/pozwolenia')
    contract_pdf = models.FileField(upload_to=get_upload_path, null=True, verbose_name="Umowa - pdf")


class ExecutRenovation(models.Model):
    contractor = models.CharField(max_length=256, verbose_name='Wykonawca')
    surveyor = models.CharField(max_length=256, verbose_name='Inspector', null=True)
    start = models.DateField(verbose_name='Data rozpoczęcia budowy')
    termination = models.DateField(verbose_name='Data protokołu odbioru')
    termination_pdf = models.FileField(upload_to=get_upload_path, null=True, verbose_name="Protokół odbioru -pdf")
    description = models.TextField(null=True, verbose_name='uwagi')
    renovation = models.OneToOneField(Renovations, on_delete=models.CASCADE, primary_key=True)


def get_upload_path_picture(instance, filename):
    return 'renovation/{}/picture/{}'.format(instance.renovation.id, filename)


class PictureRenovation(models.Model):
    description = models.TextField(null=True)
    picture = models.FileField(upload_to=get_upload_path_picture)
    renovation = models.ForeignKey(Renovations, on_delete=models.CASCADE)
