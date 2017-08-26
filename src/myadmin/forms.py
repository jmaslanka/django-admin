from django import forms


def create_form(custom_model, *args, **kwargs):
    class ModelForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(ModelForm, self).__init__(*args, **kwargs)

        class Meta:
            model = custom_model
            exclude = []
    return ModelForm
