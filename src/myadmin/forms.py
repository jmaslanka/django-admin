from django import forms


def create_form(custom_model, *args, **kwargs):
    class EditForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(EditForm, self).__init__(*args, **kwargs)

        class Meta:
            model = custom_model
            exclude = []
    return EditForm
