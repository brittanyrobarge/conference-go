from json import JSONEncoder
from django.http import JsonResponse
from datetime import datetime
from .models import Presentation
from events.models import Conference
from common.json import ModelEncoder
from events.api_views import ConferenceListEncoder
from django.views.decorators.http import require_http_methods
import json

class PresentationEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Presentation):
            return {
                "title": o.title,
                "status": o.status.name,
                "href": o.get_api_url(),
            }
        elif isinstance(o, datetime):
            return o.isoformat()
        else:
            return super().default(o)

class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        'title',
    ]

    def get_extra_data(self, o):
        return {"status": o.status.name}


class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
        "conference",
    ]
    encoders = {
        'conference':ConferenceListEncoder(),
    }

    def get_extra_data(self, o):
        return {"status": o.status.name}

@require_http_methods(["DELETE", "GET", "PUT"])
def api_list_presentations(request, conference_id):
    if request.method == "GET":
        return JsonResponse(

            {"presentations":Presentation.objects.filter(conference=conference_id)},
            encoder=PresentationEncoder)
    else:
        content = json.loads(request.body)
        try:
            conference = conference.objects.get(
            id=conference_id
            )
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400
            )

    presentation = Presentation.objects.create(**content)
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_presentation(request, id):
    if request.method == "GET":
        presentation = Presentation.objects.get(id=id)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = presentation.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)

        Presentation.objects.filter(id=id).update(**content)

        presentation = Presentation.objects.get(id=id)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )
