from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Delete expired sessions'

    def handle(self, *args, **kwargs):
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        expired_sessions.delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted expired sessions'))
