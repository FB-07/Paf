from django.shortcuts import render
from ..models import Feedback

def admin_reports(request):

    feedbacks = Feedback.objects.all().order_by('-criado_em')

    return render(request, "admin/reports.html", {"feedbacks": feedbacks})
