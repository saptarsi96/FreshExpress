from accounts.models import UserAddress
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.forms import modelform_factory, widgets
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .forms import UserAddressForm
from django.http.response import HttpResponse
from django.contrib import messages
from django.http import HttpResponseRedirect
import smtplib, ssl
# Create your views here.


class Register(SuccessMessageMixin, generic.CreateView):
    form_class = UserCreationForm
    success_message = "Registration Successfull you can now login."
    template_name = "registration/register.html"
    success_url = reverse_lazy('login')


@login_required
def profile(req):
    UserEditForm = modelform_factory(
        get_user_model(), fields=('first_name', 'last_name', 'username'))
    form = UserEditForm(instance=req.user)
    if req.method == "POST":
        form = UserEditForm(instance=req.user, data=req.POST)
        if form.is_valid():
            form.save()
    return render(req, 'registration/profile.html', {'form': form})


@login_required
def changeAddress(request):
    form = UserAddressForm(request.POST)
    if form.is_valid():
        addr = form.save(commit=False)
        addr.user = request.user
        try:
            addr2 = UserAddress.objects.filter(user=request.user)[0]
            addr2.city  = addr.city
            addr2.pincode = addr.pincode
            addr2.address = addr.address
            addr2.save()
        except:
            addr.save()
    try:
        addr2 = UserAddress.objects.filter(user=request.user)[0]
        form = UserAddressForm(initial={'city':addr2.city,'pincode':addr2.pincode,'address':addr2.address})
    except:
        pass
    return render(request, 'useraddress.html', {'form': form})

def send(username,email,queries):
    email_id="guptahimanshu2035@gmail.com"
    password="ajyfgrezutgkypdd"
    try:
        subject ="""\
        Support FreshExpress
        """
        text="""\
        Greetings from FreshExpress,
        We have received your query regarding"{1}".Our Customer Support Executive will contact you soon.
        
        Thank you for using FreshExpress.
        Stay safe and stay connected!!
        Sincerly,
        The FreshExpress Service Team
        """.format(username,queries)
        conn=smtplib.SMTP('imap.gmail.com',587)
        conn.ehlo()
        conn.starttls()
        conn.login(email_id,password)
        message = 'Subject: {}\n\n{}'.format(subject, text)
        conn.sendmail(email_id,email,message)
        return 1
    except KeyError:
        return 0

def help(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        queries=request.POST.get('queries')
        result=send(username,email,queries)
        if result==1:
            messages.success(request, "Your query is successfully registered. We will connect with you shortly!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))