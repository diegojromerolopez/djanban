from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from djangotrellostats.apps.members.models import Member


# View the slideshow
@login_required
def view(request):
    member = request.user.member
    boards = member.boards.exclude(last_fetch_datetime=None).order_by("-last_activity_datetime")
    replacements = {"member": member, "boards": boards, "members": Member.objects.filter(boards__in=boards)}
    return render(request, "slideshow/view.html", replacements)

