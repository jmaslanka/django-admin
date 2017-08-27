import json

from django.apps import apps
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.views import View
from django.views.generic.list import ListView

from myadmin.models import AdminPanel
from myadmin.forms import create_form


class AdminPanelView(PermissionRequiredMixin, View):
    """
    View for custom admin panel.
    """
    permission_required = 'myadmin.access_panel'
    raise_exception = True
    template_name = 'myadmin/admin.html'
    models = apps.get_models()
    admin_panel = AdminPanel.objects.first()
    paginate_by = 6

    def get_existing_models(self):
        if self.admin_panel.models_text:
            existing_models = json.loads(self.admin_panel.models_text)
        else:
            return list()

        result = []
        str_models = list(map(str, self.models))
        for obj in existing_models:
            result.append(self.models[str_models.index(obj)])
        return result

    def get_add_models_names(self, get_objects=False):
        result = []
        if not self.admin_panel.models_text:
            if get_objects:
                return self.models
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
            obj_list = list(obj.objects.all())
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
        return render(request, self.template_name, context=context)

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


class ModelListView(PermissionRequiredMixin, ListView):
    permission_required = 'myadmin.access_panel'
    raise_exception = True
    template_name = 'myadmin/objects_view.html'
    paginate_by = 15
    model_name = ''

    def get_queryset(self):
        model_name = self.kwargs.pop('model_name')
        self.model_name = model_name
        model = apps.get_model(model_name)
        queryset = model.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ModelListView, self).get_context_data(**kwargs)
        context['model_name'] = self.model_name
        app_, model_ = self.model_name.split('.')
        context['add_perm'] = '{}.add_{}'.format(app_.lower(), model_.lower())
        context['delete_perm'] = '{}.delete_{}'.format(
            app_.lower(), model_.lower()
        )
        context['change_perm'] = '{}.change_{}'.format(
            app_.lower(), model_.lower()
        )
        return context


class ObjectCreateView(PermissionRequiredMixin, View):
    permission_required = 'myadmin.access_panel'
    raise_exception = True
    template_name = 'myadmin/single_object_view.html'

    def get(self, request, model_name, *args, **kwargs):
        app_, model_ = model_name.split('.')
        permission_name = '{}.add_{}'.format(app_.lower(), model_.lower())
        if not request.user.has_perm(permission_name):
            raise PermissionDenied

        try:
            model = apps.get_model(model_name)
        except LookupError:
            return redirect('myadmin:panel')

        form = create_form(model)()
        return render(
            request, self.template_name,
            {'form': form, 'model_name': model_name}
        )

    def post(self, request, model_name, *args, **kwargs):
        app_, model_ = model_name.split('.')
        permission_name = '{}.add_{}'.format(app_.lower(), model_.lower())
        if not request.user.has_perm(permission_name):
            raise PermissionDenied

        try:
            model = apps.get_model(model_name)
        except LookupError:
            return redirect('myadmin:panel')
        form = create_form(model)(request.POST)

        if form.is_valid():
            form.save()
            return redirect('myadmin:objects', model_name=model_name)
        return render(
            request, self.template_name,
            {'form': form, 'model_name': model_name}
        )


class ObjectEditView(PermissionRequiredMixin, View):
    permission_required = 'myadmin.access_panel'
    raise_exception = True
    template_name = 'myadmin/single_object_view.html'

    def get(self, request, model_name, obj_pk, *args, **kwargs):
        app_, model_ = model_name.split('.')
        permission_name = '{}.change_{}'.format(app_.lower(), model_.lower())
        if not request.user.has_perm(permission_name):
            raise PermissionDenied

        try:
            model = apps.get_model(model_name)
        except LookupError:
            return redirect('myadmin:panel')
        obj = get_object_or_404(model, pk=obj_pk)
        form = create_form(model)(instance=obj)
        return render(
            request, self.template_name,
            {'form': form, 'model_name': model_name}
        )

    def post(self, request, model_name, obj_pk, *args, **kwargs):
        app_, model_ = model_name.split('.')
        permission_name = '{}.change_{}'.format(app_.lower(), model_.lower())
        if not request.user.has_perm(permission_name):
            raise PermissionDenied

        try:
            model = apps.get_model(model_name)
        except LookupError:
            return redirect('myadmin:panel')
        obj = get_object_or_404(model, pk=obj_pk)
        form = create_form(model)(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('myadmin:objects', model_name=model_name)
        return render(
            request, self.template_name,
            {'form': form, 'model_name': model_name}
        )


class ObjectDeleteView(PermissionRequiredMixin, View):
    permission_required = 'myadmin.access_panel'
    raise_exception = True

    def get(self, request, model_name, obj_pk):
        app_, model_ = model_name.split('.')
        permission_name = '{}.delete_{}'.format(app_.lower(), model_.lower())
        if not request.user.has_perm(permission_name):
            raise PermissionDenied

        try:
            model = apps.get_model(model_name)
        except LookupError:
            return redirect('myadmin:panel')
        get_object_or_404(model, pk=obj_pk).delete()
        return redirect('myadmin:objects', model_name=model_name)
