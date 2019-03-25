from survey.models import Buildings, Survey, KIND_SURVEY
import django_filters


LAB= {
    ('', 'wszystkie'),
    ('True', 'bieżące'),
    ('False', 'archiwalny')
}


class SurveyFilter(django_filters.FilterSet):
    building=django_filters.ModelChoiceFilter(queryset=Buildings.objects.all(), label="dla budynku", empty_label='wszystkie')
    kind=django_filters.ChoiceFilter(choices=KIND_SURVEY, label="  wg. rodzaju", empty_label='wszystkie')
    valid_date=django_filters.DateFromToRangeFilter()
    is_open=django_filters.ChoiceFilter(label="status", choices=LAB, empty_label=None)


    class Meta:
        model = Survey
        fields = []


