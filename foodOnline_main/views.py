from django.shortcuts import render
# from django.http import HttpResponse
from django.http import HttpResponse, JsonResponse

from vendor.models import Vendor
from menu.models import  City_lat_lon

def home(request):
    # [:8] limits the number of records returned
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        'vendors': vendors,
    }
    return render(request, 'home.html', context)

""" def autocomplete(request):
    if 'term' in request.GET:
        qs = City_lat_lon.objects.filter(City__istartwith=request.GET.get('term'))
        titles = list()
        for city_lat_lon in qs:
            titles.append(City_lat_lon.city)
        return JsonResponse(titles, safe=False)
    return render(request, 'home.html') """