import datetime, random
from hashlib import sha1

from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf

from mediaExchange.users.models import UserProfile
from mediaExchange.users.forms import RegistrationForm, LoginForm
from mediaExchange.index.views import indexindex

def usersregistration(request):
    c = {}
    c.update(csrf(request))

    if request.user.is_authenticated():
        c.update({'error':'You are already registered.'})
    elif request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            if form.arePasswordsEqual():
                if form.isValidUsername():
                    new_user = form.save()
                    salt = sha1(str(random.random())).hexdigest()[:5]
                    activation_key = sha1(salt+new_user.username).hexdigest()
                    key_expires = datetime.datetime.today() + datetime.timedelta(3)

                    # Create and save their profile
                    new_profile = UserProfile(user=new_user, activation_key=activation_key, key_expires=key_expires)
                    new_profile.save()

                    # Send an email with the confirmation link

                    c.update({'error':'Thank you for registering.'})
                else:
                    c.update({'error':'User already registered.', 'regform':form})
            else:
                c.update({'error':'The passwords do not match.', 'regform':form})
        else:
            form = RegistrationForm()
            c.update({'error':'There was an error with the registration form.', 'regform':form})
    else:
        form = RegistrationForm()
        c.update({'regform':form})
    response = render_to_response('users/registration.html', c)
    return response

def userslogin(request):
    c = {}
    c.update(csrf(request))

    if request.user.is_authenticated():
        response = indexindex(request)
    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                if user is not None and user.is_active:
                    login(request, user)
                    response = indexindex(request)
                else:
                    c.update({'loginform':form, 'error':'Wrong credentials.'})
                    response = render_to_response('users/login.html', c)
            else:
                c.update({'loginform':form, 'error':'Invalid login attempt.'})
                response = render_to_response('users/login.html', c)
        else:
            form = LoginForm()
            c.update({'loginform':form})
            response = render_to_response('users/login.html', c)
    return response

def userslogout(request):
    c = {}
    c.update(csrf(request))

    logout(request)
    c.update({'loginform':LoginForm(), 'error':'Successfully logged out.'})
    return render_to_response('users/login.html', c)

@login_required
def usersconfirmation(request, activation_key):
    if request.user.is_authenticated() and request.user.name in ['chriz', 'root']:
        user_profile = get_object_or_404(UserProfile, activation_key=activation_key)
        user_account = user_profile.user
        user_account.is_active = True
        user_account.save()
        response = render_to_response('confirm.html', {'error': 'Account Activated.'})
    else:
        response = render_to_response('confirm.html', {'error':'Not authorized.'})
    return response
