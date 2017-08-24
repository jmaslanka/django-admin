import json

from django.apps import apps
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.views import View

from myadmin.models import AdminPanel


class AdminPanelView(View):
    """
    View for custom admin panel.
    """
    template = 'myadmin/admin.html'
    models = apps.get_models()
    admin_panel = AdminPanel.objects.first()
    paginate_by = 8

    def get_existing_models(self):
        if self.admin_panel.models_text:
            existing_models = json.loads(self.admin_panel.models_text)
        else:
            return list()

        result = []
        for obj in existing_models:
            str_models = list(map(str, self.models))
            result.append(self.models[str_models.index(obj)])
        return result

    def get_add_models_names(self, get_objects=False):
        result = []
        if not self.admin_panel.models_text:
            return [(obj._meta.app_label, obj.__name__) for obj in self.models]
        existing = json.loads(self.admin_panel.models_text)
        for obj in self.models:
            if str(obj) not in existing:
                if get_objects:
                    result.append(obj)
                else:
                    result.append((obj._meta.app_label, obj.__name__))
        return result

    def get_remove_models_names(self):
        existing = self.get_existing_models()
        return [(obj._meta.app_label, obj.__name__) for obj in existing]

    def create_models_data(self, request):
        models = []
        existing_models = self.get_existing_models()

        for obj in existing_models:
            obj_name = '{}.{}'.format(obj._meta.app_label, obj.__name__)
            obj_list = obj.objects.all()
            paginator = Paginator(obj_list, self.paginate_by)

            page = request.GET.get(obj_name)
            try:
                model_objects = paginator.page(page)
            except PageNotAnInteger:
                model_objects = paginator.page(1)
            except EmptyPage:
                model_objects = paginator.page(paginator.num_pages)

            models.append([obj_name, model_objects])
        return models

    def get(self, request, *args, **kwargs):
        context = {
            'models_view': self.create_models_data(request),
            'models_select': self.get_add_models_names(),
            'models_remove': self.get_remove_models_names()
        }
        return render(request, self.template, context=context)

    def post(self, request, *args, **kwargs):
        if 'add' in request.POST:
            model_indexes = request.POST.getlist('select_models')
            models = []
            for index in map(int, model_indexes):
                obj = self.get_add_models_names(get_objects=True)[index]
                models.append(str(obj))
            if not self.admin_panel.models_text:
                self.admin_panel.models_text = json.dumps(models)
            else:
                self.admin_panel.models_text = json.dumps(
                    json.loads(self.admin_panel.models_text) + models
                )
            self.admin_panel.save()
        elif 'remove' in request.POST:
            model_indexes = request.POST.getlist('remove_models')
            if not model_indexes:
                return self.get(request, *args, **kwargs)
            models = []
            existing = self.get_existing_models()
            for index in map(int, model_indexes):
                obj = existing[index]
                models.append(obj)
            for obj in models:
                existing.remove(obj)
            self.admin_panel.models_text = json.dumps(list(map(str, existing)))
            self.admin_panel.save()
        return self.get(request, *args, **kwargs)
