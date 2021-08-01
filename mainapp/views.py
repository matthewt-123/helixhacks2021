from django.http.response import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import os
from django.db import IntegrityError
from .models import User, Team, AboutMe, Event
from dotenv import load_dotenv
import requests
import json
from .forms import TeamForm, AboutForm, EventForm
from django.contrib.auth.decorators import login_required
import datetime


load_dotenv()
# Create your views here.
def index(request):
    return render(request, 'mainapp/index.html')
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if request.GET.get('next') is not None:
                return HttpResponseRedirect(request.GET.get('next'))
            return HttpResponseRedirect(reverse("index"), status=302)
        else:
            return render(request, "mainapp/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.GET.get('next'):
            next = request.GET.get('next')
        else:
            next=None
        return render(request, "mainapp/login.html", {
            "next": next
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "hwapp/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "mainapp/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        if request.GET.get('next') is not None:
            return HttpResponseRedirect(request.GET.get('next'))
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "mainapp/register.html")

def lookup(request):
    try:
        zipcode = request.GET.get('zipcode')
        zip = int(zipcode)
        len(str(zip)) == 5
    except:
        return JsonResponse({
            "error": "invalid US zip code"
        })
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{zip}.json?access_token={os.environ.get('mapbox_private')}"
    response = requests.get(url)
    formatted = json.loads(response.text)
    coordinates = formatted['features'][0]['center']
    url = f"https://api.breezometer.com/fires/v1/current-conditions?lat={coordinates[1]}&lon={coordinates[0]}&key={os.environ.get('breezometer_fire')}&radius=50"
    response = requests.get(url)
    formatted = json.loads(response.text)
    if formatted['data'] == 'false':
        return JsonResponse({"error": "BreezoMeter Fire Error"})
    fires = formatted['data']['fires']
    features = "breezometer_aqi,local_aqi"
    url = f"https://api.breezometer.com/air-quality/v2/current-conditions?lat={coordinates[1]}&lon={coordinates[0]}&key={os.environ.get('breezometer_fire')}&features={features}&breezometer_aqi_color=indiper_dark"
    response = requests.get(url)
    formatted = json.loads(response.text)
    color = formatted['data']['indexes']['baqi']['color']
    print(color)
    print(formatted['data']['indexes']['usa_epa'])
    if formatted['data'] == 'false':
        return JsonResponse({"error": "BreezoMeter AQI Error"})
    aqi = formatted['data']['indexes']['usa_epa']
    aqi_val = aqi['aqi']
    return render(request, 'mainapp/lookup.html', {
        "fires": fires,
        "aqi": aqi,
        "color": color,
        'aqi_val': aqi_val,
        "zipcode": zipcode
    })

def environmental_impact(request):
    return render(request, "mainapp/env_impact.html")
def impact(request):
    if request.method == "POST":
        zip = int(request.POST['zipcode'])
        zip_list = [zip+1, zip, zip-1]
        teams_list = Team.objects.all()
        local = []
        for team in teams_list:
            for zipcode in zip_list:
                if team.zip_code == zipcode:
                    try:
                        time = datetime.datetime.now()
                        new_time = time.strftime("%Y-%m-%d")
                        next_ev = Event.objects.filter(team=team, date__gt = new_time).order_by('-date','-time')
                    except:
                        next_ev = None
                    local.append([team, next_ev])
        print(local[0][1][0].id)
        return render(request, "mainapp/impact_results.html", {
            "local_teams": local,
        })
    else:
        return render(request, "mainapp/impact.html")
def credits(request):
    return render(request, "mainapp/credits.html")

@login_required(login_url='/login')
def addteam(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team_name = form.cleaned_data['team_name']
            zip_code = form.cleaned_data['zip_code']
            if len(str(zip_code)) != 5:
                return render(request, 'mainapp/teamform.html', {
                    'form': form,
                    'error': "Invalid Zip Code. Please enter your 5 digit US Zip Code"
                })
        new_team = Team(team_name=team_name, zip_code=zip_code)
        new_team.save()
        new_team.teammate.add(request.user)
        return HttpResponseRedirect(f'/team?id={new_team.id}')
    else:
        try:
            AboutMe.objects.get(about_user=request.user)
        except:
            return render(request, 'mainapp/error.html', {
                "error": "Please complete your profile at <a href='/profile'>this link</a>"
            })
        form = TeamForm()
        return render(request, 'mainapp/teamform.html', {
            'form': form,
            'header': 'New Team',
        })
@login_required(login_url='/login')
def teamview(request):
    t_id = request.GET.get('id')
    if t_id == None:
        return HttpResponseRedirect(reverse('index'))
    team = Team.objects.get(id=t_id)
    members = team.teammate.all()
    if request.user in members:
        link = f"{os.environ.get('base_dir')}/invite?id={team.id}&hash={hash(str(team.id))}"
        edit = True
    else:
        edit=False
        link = None
    events = Event.objects.filter(team=team)
    return render(request, 'mainapp/teamview.html', {
        'team': team,
        'edit': edit,
        'members': members,
        'link': link,
        'events': events,
        'e_length': len(events)
    })

def about_user(request):
    id = request.GET.get('id')
    if id is None:
        return HttpResponseRedirect(reverse('index'))
    try:
        profile1 = AboutMe.objects.get(about_user=User.objects.get(id=id))
    except:
        return render(request, 'mainapp/error.html', {
            'error': 'profile does not exist'
        })
    print(profile1.image)
    return render(request, 'mainapp/profile.html', {
        'profile': profile1
    })
def profile(request):
    if request.method == 'POST':
        form = AboutForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            age = form.cleaned_data['age']
            image = form.cleaned_data['image']
            self_blurb = form.cleaned_data['self_blurb']
            zip_code = form.cleaned_data['zip_code']
        if int(age) < 13:
            return render(request, 'mainapp/error.html', {
                'error': 'Sorry, all users must be over 13 years of age'
            })
        new_profile = AboutMe(about_user=request.user, first_name=first_name, age=age, image=image, self_blurb=self_blurb, zip_code=zip_code)
        new_profile.save()
        return HttpResponseRedirect(reverse('index'))
    else:
        form = AboutForm()
        return render(request, 'mainapp/profileform.html', {
            'form': form,
            'header': "Profile",
        })
@login_required(login_url='/login')
def invite(request):
    try:
        try:
            profile = AboutMe.objects.get(about_user=request.user)
        except:
            return render(request, 'mainapp/error.html', {
                'error': "Please create your profile <a href='/profile'>at this link</a>"
            })
        id = request.GET.get('id')
        hash_val = request.GET.get('hash')
        print(hash(str(id)))
        if id==None or hash_val==None:
            return HttpResponseRedirect(reverse('index'))
        print(hash(str(id)))
        print(str(hash_val))
        if str(hash(str(id))) == str(hash_val):
            team = Team.objects.get(id=id)
            team.teammate.add(request.user)
            print(team)
        else:
            return render(request, 'mainapp/error.html', {
                'error': 'Invalid link'
            })
        return render(request, 'mainapp/success.html', {
            'message': f"Success! You have joined {team.team_name}"
        })
    except:
        return HttpResponseRedirect(reverse('index'))

@login_required(login_url='/login')
def addevent(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event_name = form.cleaned_data['event_name']
            time = form.cleaned_data['time']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            zip_code = form.cleaned_data['zip_code']
            description = form.cleaned_data['description']
        id = request.GET.get('id')
        team = Team.objects.get(id=id)
        if request.user not in team.teammate.all():
            return render(request,'mainapp/error.html', {
                'error': 'Access Denied: You are not in this team!!'
            })
        n_event = Event(time=time, address=address, zip_code=zip_code, description=description, city=city, event_name=event_name, team=team)
        n_event.save()
        n_event.attendees.add(request.user)
        n_event.save()
        return render(request, 'mainapp/success.html', {
            'message': f'Event Successfully Added. <a href="/team?id={team.id}">Return to Team Home</a>'
        })
    else:
        id = request.GET.get('id')
        if id == None:
            return render(request, 'mainapp/error.html', {
                'error': 'Invalid ID'
            })
        form = EventForm()
        return render(request, 'mainapp/addevent.html', {
            'team_id': id,
            'form': form,
            'team': Team.objects.get(id=id)
        })
@login_required(login_url='/login')
def event_details(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            e_id = data['event']
            updated = data['updated']
            if int(updated) != 1:
                return JsonResponse({'message': 'Bad request', 'status': 400}, status=400)
        except:
            return JsonResponse({'message': 'Bad Request', 'status': 400}, status=400)
        event = Event.objects.get(id=e_id)
        if request.user in event.attendees.all():
            inner = "Register"
            event.attendees.remove(request.user)
            event.save()
        else:
            inner = "Cancel Registration"
            event.attendees.add(request.user)
            event.save()
        return JsonResponse({"message": "success", 'status': 200, "inner": inner}, status=200)
    else:
        id = request.GET.get('id')
        if id is None:
            return render(request, 'mainapp/error.html', {
                'error': 'Invalid ID'
            })
        event = Event.objects.get(id=id)
        if request.user in event.attendees.all():
            registered = True
        else:
            registered=False    
        return render(request, 'mainapp/event_details.html', {
            'event': event,
            'registered': registered
        })