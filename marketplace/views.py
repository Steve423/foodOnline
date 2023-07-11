from datetime import date, datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from pymysql import NULL
from .context_processors import get_cart_counter, get_cart_amounts
# from marketplace.models import Cart
from menu.models import Category, FoodItem, City_lat_lon

from vendor.models import OpeningHour, Vendor
from django.db.models import Prefetch
from .models import Cart
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D  # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance
import winrt.windows.devices.geolocation as wdg, asyncio

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }

    return render(request, 'marketplace/listings.html', context )

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
        'fooditems',
        queryset = FoodItem.objects.filter(is_available=True).order_by('food_title')
        )
    )
    categories = Category.objects.filter(vendor=vendor).order_by('category_name')
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')
    
    # Check current day's opening hours.
    today_date = date.today()
    today = today_date.isoweekday()
    
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)


    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None


    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
    }
    return render(request, 'marketplace/vendor_detail.html', context)

def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increase the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})

            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})            

        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})            

    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})
    
def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity >1:
                        # decrease the cart quantity
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status': 'Success', 'message': 'Decreased the cart quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})

            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})            

        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})            

    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

@login_required(login_url = 'login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # Check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart item has been deleted', 'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amounts(request)})            
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})            
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})            

async def getCoords():
        locator = wdg.Geolocator()
        pos = await locator.get_geoposition_async()
        
        return [pos.coordinate.latitude, pos.coordinate.longitude]
    
def getLoc():
    return asyncio.run(getCoords())

def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        # myGet = getLoc()
        # intLoop =0
        # for xmyGet in myGet:
        #     if intLoop == 0:
        #         myLat = xmyGet
        #     if intLoop == 1:
        #         myLng = xmyGet

        #     intLoop = intLoop +1
        # vendor_newGPS = "__Lat_=_" + str(myLat) + "_Lng_=_" + str(myLng)


        # freegeoip = "https://freegeoip.net/json"
        # geo_r = RequestContext.get(freegeoip)
        # geo_json = geo_r.json()

        # user_postition = [geo_json["latitude"], geo_json["longitude"]]

        # print("======= " + user_postition)
 
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        # 7-7-2023 Because my FREE trial for google has expired, I hard-coded the Lat & Lon for Little Rock
        # latitude = "34.7483749096"
        #longitude = "-92.3208791714"

        radius = request.GET['radius']
        keyword = request.GET['keyword']

        # get vendor ids that has the food item the user is looking for
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True).distinct()
        print(fetch_vendors_by_fooditems)
        # print(fetch_vendors_by_fooditems)
        # above gets ID for vendors , for example has "Chicken" in name

        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        # Above is new search function which has an "OR" ie "|". Below is the original search function
        # vendors = Vendor.objects.filter(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)
        # vendors = Vendor.objects.filter()
        if latitude and longitude and radius:
            # pnt = GEOSGeometry("POINT(-96.876369 29.905320)", srid=4326)
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))

            vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
            user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location",pnt)).order_by("distance")

            for v in vendors:
                v.kms = round(v.distance.km, 1)
        vendor_count = vendors.count()
        context = {
            'vendors':vendors,
            'vendor_count': vendor_count,
            'source_location': address
        }

        return render(request, 'marketplace/listings.html', context)

def auto2complete(request):
    if 'term' in request.GET:
        qs = City_lat_lon.objects.filter(City__istartwith=request.GET.get('term'))
        titles = list()
        for city_lat_lon in qs:
            titles.append(City_lat_lon.city)
        return JsonResponse(titles, safe=False)
    return render(request, 'home.html')