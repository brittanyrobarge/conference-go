from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Conference, Location, State
from common.json import ModelEncoder
import json
from .acls import get_location_image, get_weather

class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]

class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "picture_url"
    ]

    def get_extra_data(self, o):
        return { "state": o.state.abbreviation }

class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders = {
        "location": LocationListEncoder(),
    }
class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = ["name"]

@require_http_methods(["GET", "POST"])
def api_list_conferences(request):
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse(
            {"conferences": conferences},
            encoder=ConferenceListEncoder,
            )
    else:
        content = json.loads(request.body)
    try:
        location = Location.objects.get(id=content["location"])
        content["location"] = location
    except Location.DoesNotExist:
        return JsonResponse(
            {"message": "Invalid location id"},
            status=400,
        )

    conference = Conference.objects.create(**content)
    return JsonResponse(
        conference,
        encoder=ConferenceDetailEncoder,
        safe=False,
    )

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_conference(request, id):
    if request.method == "GET":
        conference = Conference.objects.get(id=id)
        weather = get_weather(conference.location)
        return JsonResponse(
            {
            "weather": weather,
            "conference":conference,
            },
            encoder=ConferenceDetailEncoder, safe=False
        )
    elif request.method == "DELETE":
        count, _ = Conference.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        if "location" in content:
            try:
                location = Location.objects.get(id=content["location"])
                content["location"] = location
            except Location.DoesNotExist:
                return JsonResponse(
                    {"message": "Invalid location id"},
                    status=400,
                )


    # new code
    Conference.objects.filter(id=id).update(**content)

    # copied from get detail
    Conference = Conference.objects.get(id=id)
    return JsonResponse(
        conference,
        encoder=ConferenceDetailEncoder,
        safe=False,
    )

@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse(
            {"locations": list(locations)},
            encoder=LocationListEncoder,
        )
    else:
        content = json.loads(request.body)
        try:
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )
        if "picture_url" not in content or not content["picture_url"]:
            content["picture_url"] = get_location_image(content["city"],content["state"])

    location = Location.objects.create(**content)
    return JsonResponse(
        location,
        encoder=LocationDetailEncoder,
        safe=False,
    )

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, id):
    if request.method == "GET":
        location = Location.objects.get(id=id)
        if location.picture_url is None:
            location.picture_url = get_location_image(location.city,location.state.name)
            location.save()
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False
        )
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )

    # new code
    Location.objects.filter(id=id).update(**content)

    # copied from get detail
    location = Location.objects.get(id=id)
    return JsonResponse(
        location,
        encoder=LocationDetailEncoder,
        safe=False,
    )
