from django.shortcuts import get_object_or_404, render, redirect
from .forms import VendorForm
from accounts.forms import UserProfileForm

from accounts.models import UserProfile
from .models import Vendor
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from menu.models import Category


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)

    else:
        profile_form = UserProfileForm(instance = profile)
        vendor_form = VendorForm(instance = vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, 'vendor/vprofile.html', context)


def menu_builder(request):
    vendor = Vendor.objects.get(user=request.user)
    categories = Category.objects.filter(vendor=vendor)
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)


def fooditems_by_category(request, pk=None):
    vendor = Vendor.objects.get(user=request.user)
    category = get_object_or_404(Category, pk=None)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    
    return render(request, 'vendor/fooditems_by_category.html')