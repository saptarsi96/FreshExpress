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