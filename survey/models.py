import os

from django.db import models


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
    ("Inne",(
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
        os.remove(self.pdf.path)
        return super(Survey, self).delete()



class Execution(models.Model):
    date = models.DateField()
    description = models.TextField()
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)


class PdfFile(models.Model):
    name = models.CharField(max_length=255)
    pdf = models.FileField(upload_to='pdf')


