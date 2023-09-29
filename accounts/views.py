from datetime import datetime
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import message
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlsafe_base64_decode

from vendor.forms import VendorForm
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from .utils import detectUser, send_verification_email, send_vendor_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test

from django.core.exceptions import PermissionDenied
from vendor.models import Vendor
from django.template.defaultfilters import slugify
from orders.models import Order
import datetime
from django.conf import settings
from .shortcuts_sh import get_object_or_none


# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('dashboard')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()

            # Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('registerUser')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == 'POST':
        # store the data and create the user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid:
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            print("__A_after_vendor_save")
            print(user)
            print(request)
            print("__A_after_print_request")
            vendor_id = vendor.id
            print("__A_vendor_id_=_" + str(vendor_id))


            # Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your account has been registered sucessfully! Please wait for the approval.')
            # 9-27-2023 adde to send email to Manager to approve Vendor.
            #  from_email = settings.DEFAULT_FROM_EMAIL
            # manager_email= settings.DEFAULT_FROM_EMAIL
            manager_email = settings.EMAIL_HOST_USER

            mail_subject = 'Please approve Vendor ' + vendor_name + ' for ' +first_name + ' ' + last_name
            email_template = 'accounts/emails/admin_approval_email.html'
            print("__A_before_send_vendor_verification_email")
            print("__A_user")
            print(user)
            print("__A_request")
            print(request)
            print("__A_manager_email")
            print(manager_email)

            send_vendor_verification_email(request, user, mail_subject, email_template, manager_email, vendor_name,first_name,last_name, vendor_id  )



            return redirect('registerVendor')
        else:
            print('invalid form')
            print(form.errors)
    else:
            # email = self.normalize_email(email),
            # username = username,
            # password = password,
            # first_name = first_name,
            # last_name = last_name,
        mytestPass = "D23jango"

        mydata = {'email':'steve72638@gmail.com',
                  'first_name':'Ste 72638',
                  'username': 'steve72638',
                  'password': mytestPass,
                  'confirm_password': mytestPass,
                  'last_name':'Hall'}
        myvendorr = {'vendor_name': 'Larry Pizza'}
        form = UserForm(mydata)
        v_form = VendorForm(myvendorr)

    context = {
        'form': form,
        'v_form': v_form,
    }

    return render(request, 'accounts/registerVendor.html', context)


def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    print("__C_activate_user")
    print(user)
    print("__C_uidb64")
    print(uidb64)
    print("__C_token")
    print(token)
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation! Your account is activated.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myAccount')

    # print("__F_vendor_activate_user")
    # print(request)
    # print("__F_uidb64")
    # print(uidb64)
    # print("__F_token")
    # print(token)

        # print("__F_uid")
        # print(str(uid))

    # print("__F_user")
    # print(user)
        # print("__F_ready_to_approve")
        # vendor = Vendor._default_manager.get(user_id=uid)
        # print("__F_vendor")
        # print(vendor)


def vendor_activate(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        uid = 0
    if user is not None and default_token_generator.check_token(user, token):
        vendor = Vendor._default_manager.get(user_id=uid)
        if vendor is not None:
            print("__F_vendor_record_found")
            vendor.is_approved = True
            print("__F_before_save")
            vendor.save()
            messages.success(request, 'Congratulation! vendor is aproved.')
        else:
            print("__F_vendor_record_NOT_found")
            messages.error(request, 'Error record not found for user ' + str(uid))
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        print("__F_error")
        return redirect('myAccount')

    # # Activate the user by setting the is_active status to True
    # try:
    #     uid = urlsafe_base64_decode(uidb64).decode()
    #     print("__F_uid")
    #     print(uid)
    #     user = User._default_manager.get(pk=uid)
    #     print("__F_user")
    #     print(user)
    # except(TypeError, ValueError, OverflowError, User.DoesNotExist):
    #     user = None
    # # print("__C_activate_user")
    # # print(user)
    # # print("__C_uidb64")
    # # print(uidb64)
    # # print("__C_token")
    # # print(token)
    # # if user is not None and default_token_generator.check_token(user, token):
    # #     user.is_active = True
    # #     user.save()
    # #     messages.success(request, 'Congratulation! Your account is activated.')
    # #     return redirect('myAccount')
    # # else:
    # #     messages.error(request, 'Invalid activation link')
    # #     return redirect('myAccount')

    # if user is not None :
    # # and default_token_generator.check_token(user, token):
    #     # user.is_active = True
    #     # user.save()
    #     messages.success(request, 'Congratulation! in_vendor_activate.')
    #     return redirect('myAccount')
    # else:
    #     messages.error(request, 'Invalid activation link_for_vendor_activate')
    #     return redirect('myAccount')

    # return redirect('myAccount')


def vendor_2activate(request, pk=None):
    # Activate the user by setting the is_active status to True
    try:
        print("__A_id_=_"+ str(pk))
        vendor = get_object_or_404(Vendor, pk=pk)
        if vendor is not None:
            vendor.is_approved = True
            vendor.save()
            messages.success(request, 'Congratulation! Vendor account is activated.')
            return redirect('myAccount')
        else:
            print("__A_ERROR")
            messages.error(request, 'Invalid activation link')
            return redirect('myAccount')


        # uid = urlsafe_base64_decode(uidb64).decode()
        # user = User._default_manager.get(pk=uid)
        # print("__A_uid_=_"+ str(uid))
        # print("__A__request.user_=_" + str(request.user))
        # print(user)
        # user = User.objects.get(id=uid)
        # print("__BB__user")
        # print(user)

            # vendor = Vendor.objects.get(user=request.user)

        # user = Vendor._default_manager.get(user_id=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        messages.error(request, 'ERROR_unable to approve vendor')
        return redirect('myAccount')

    # print("__A_vendor_activate_user")
    # print(user)
    # print("__A_uidb64")
    # print(uidb64)
    # print("__A_token")
    # print(token)

    # if user is not None and default_token_generator.check_token(user, token):
    #     print("__A_Ready_to_set_is_approved")
    #     # vendor = Vendor._default_manager.get(user_id=uid)
    #     vendor = Vendor.objects.get(user_id=uid)
    #     print("__A_vendor")
    #     print(vendor)
    #     vendor.is_approved = True
    #     vendor.save()
    #     messages.success(request, 'Congratulation! Vendor account is activated.')
    #     return redirect('myAccount')
    # else:
    #     print("__A_ERROR")
    #     messages.error(request, 'Invalid activation link')
    #     return redirect('myAccount')


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('login')


@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders[:5]
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/custDashboard.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    print("___A___vendor.id_=_" + str(vendor.id))
    # vendor.id=20
    # print("___A___vendor.id_=_" + str(vendor.id))
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('created_at')
    recent_orders = orders[:10]

    # current month's revenue
    current_month = datetime.datetime.now().month
    # current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    current_month_orders = orders.all( )
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()['grand_total']
    

    # total revenue
    total_revenue = 0
    for i in orders:
        total_revenue += i.get_total_by_vendor()['grand_total']
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,
    }
    return render(request, 'accounts/vendorDashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')