def text_message(surveys, today):
    surveys_message = [[survey.building, survey.get_kind_display(), survey.valid_date] for survey in surveys]
    text = "Zlecam następujące przeglądy:\n"
    for survey_message in surveys_message:
        if survey_message[2] < today: survey_message[2] = "pilne !!!"
        text += ("przegląd: {}, dla budynku: {}, w terminie do: {} \n".format(survey_message[1], survey_message[0],
                                                                              survey_message[2]))

    text += 'z poważaniem'
    return text



def delete_message(surveys):
    message={
        'title':'Do wykonawcy przypisane są następujące przeglądy:',
                'info':['Zostaną skasowane razem z wykonawcą.',
                        'Jeśli chcesz je zachować, kliknij anuluj i zmień przypisanego do nich wykonawcę.']
    }
    if not surveys:
        message['title']='Brak w bazie przeglądów tego wykonawcy.'
        message['info']=[]
    return message