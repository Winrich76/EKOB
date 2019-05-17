from calendar import monthrange
import datetime

from django.http import HttpResponse


def validity_date(date_s, valid):
    date_s = date_s - datetime.timedelta(days=1)
    month = date_s.month
    year = date_s.year
    day = date_s.day
    year_delta = int(valid / 12)

    month += valid % 12
    if month > 12:
        month -= 12
        year_delta += 1

    year += year_delta
    max_day = monthrange(year, month)[1]

    if day > max_day: day = max_day

    new_date_survey = datetime.datetime(year, month, day)

    return new_date_survey



def length_valid(i_kind):
    if 1 <= i_kind < 10: return 6
    if 10 <= i_kind < 20: return 12
    if 20 <= i_kind < 30: return 24
    if 50 <= i_kind < 60: return 60



def check_open_survey(Object, building, kind, date_new_survey):
    open_surveys = Object.objects.filter(building=building, kind=kind, is_open=True)
    for survey in open_surveys.filter(survey_date__lte=date_new_survey):
        survey.is_open = False
        survey.save()
    if open_surveys.filter(survey_date__gte=date_new_survey):
        return False
    else:
        return True


def read_pdf(pdf, path_dic):
    file_path = path_dic + pdf
    try:
        with open(file_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename=' + file_path
        return response
    except FileNotFoundError:
        return HttpResponse('Plik {} nie istnieje'.format(pdf))