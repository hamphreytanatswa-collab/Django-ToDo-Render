from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def time_left(self):
        if not self.due_date:
            return 'No due date'

        now = timezone.localtime()
        due = timezone.localtime(self.due_date)
        diff = due - now

        if diff.total_seconds() < 0:
            return 'Overdue'

        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        parts = []
        if days:
            parts.append(f'{days}d')
        if hours:
            parts.append(f'{hours}h')
        if minutes:
            parts.append(f'{minutes}m')

        return 'Less than a minute' if not parts else ' '.join(parts) + ' left'

    class Meta:
        ordering = ['-created_at']