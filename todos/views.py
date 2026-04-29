# from django.shortcuts import redirect, get_object_or_404
# from django.views.generic import ListView, CreateView, DeleteView
# from django.urls import reverse_lazy
# from django.contrib.auth.mixins import LoginRequiredMixin
# from .models import Todo
# from .forms import TodoForm
# from django.views.generic import UpdateView

# class TodoListView(LoginRequiredMixin, ListView):
#     model = Todo
#     template_name = 'todos/todo_list.html'
#     context_object_name = 'todos'
#     def get_queryset(self):
#         return Todo.objects.filter(user=self.request.user)

# class TodoUpdateView(LoginRequiredMixin, UpdateView):
#     model = Todo
#     form_class = TodoForm
#     template_name = 'todos/todo_form.html'
#     success_url = reverse_lazy('todo_list')

# class TodoCreateView(LoginRequiredMixin, CreateView):
#     model = Todo
#     form_class = TodoForm
#     template_name = 'todos/todo_form.html'
#     success_url = reverse_lazy('todo_list')
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         return super().form_valid(form)

# class TodoDeleteView(LoginRequiredMixin, DeleteView):
#     model = Todo
#     template_name = 'todos/todo_confirm_delete.html'
#     success_url = reverse_lazy('todo_list')

# def toggle_todo(request, pk):
#     todo = get_object_or_404(Todo, pk=pk)
#     todo.completed = not todo.completed
#     todo.save()
#     return redirect('todo_list')

from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
import json
import calendar
from .models import Todo
from .forms import TodoForm

class TodoListView(LoginRequiredMixin, ListView):
    model = Todo
    template_name = 'todos/todo_list.html'
    context_object_name = 'todos'

    def get_queryset(self):
        # Only show tasks belonging to the logged-in user
        return Todo.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todos = self.get_queryset()
        total_tasks = todos.count()
        completed_tasks = todos.filter(completed=True).count()
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        due_map = {}
        for todo in todos:
            if todo.due_date:
                local_due = timezone.localtime(todo.due_date)
                date_key = local_due.strftime('%Y-%m-%d')
                due_map.setdefault(date_key, []).append({
                    'title': todo.title,
                    'completed': todo.completed,
                })

        now = timezone.localtime()
        weeks = []
        _, last_day = calendar.monthrange(now.year, now.month)
        for index, start_day in enumerate(range(1, last_day + 1, 7), start=1):
            end_day = min(start_day + 6, last_day)
            week_tasks = []
            for todo in todos:
                if not todo.due_date:
                    continue
                local_due = timezone.localtime(todo.due_date)
                if (
                    local_due.year == now.year and
                    local_due.month == now.month and
                    start_day <= local_due.day <= end_day
                ):
                    week_tasks.append(todo)
            completed_week_tasks = sum(1 for todo in week_tasks if todo.completed)
            total_week_tasks = len(week_tasks)
            weeks.append({
                'label': f'W{index}',
                'range': f'{start_day}-{end_day}',
                'completed': completed_week_tasks,
                'total': total_week_tasks,
                'percent': round((completed_week_tasks / total_week_tasks * 100) if total_week_tasks else 0),
            })

        context['progress'] = round(progress, 1)
        context['due_map_json'] = json.dumps(due_map)
        context['weekly_progress_json'] = json.dumps(weeks)
        return context

class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todo_list')

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todo_list')
    
    def form_valid(self, form):
        # Automatically assign the logged-in user to the new task
        form.instance.user = self.request.user
        return super().form_valid(form)

class TodoCalendarView(LoginRequiredMixin, ListView):
    model = Todo
    template_name = 'todos/calendar.html'
    context_object_name = 'todos'

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user).order_by('due_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        due_map = {}
        for todo in context['todos']:
            if todo.due_date:
                date_key = timezone.localtime(todo.due_date).strftime('%Y-%m-%d')
                due_map.setdefault(date_key, []).append(todo.title)
        context['due_map_json'] = json.dumps(due_map)
        return context

class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Todo
    template_name = 'todos/todo_confirm_delete.html'
    success_url = reverse_lazy('todo_list')

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

@login_required
def toggle_todo(request, pk):
    # This remains a functional view for a quick state toggle
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.completed = not todo.completed
    todo.save()
    return redirect('todo_list')
