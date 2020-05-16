from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, EmailMultiAlternatives
# Create your views here.
def signup(request):
	if request.method == 'POST':
		obj = User.objects.create_user(username = request.POST['username'], email = request.POST['email'], password = request.POST['password'])
		obj.is_active = False
		obj.save()
		current_site = get_current_site(request)
		mail_subject = 'Akkountni faollashtirish'
		message = render_to_string('acc_active_email.html', {
                'user': obj,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(obj.pk)),
                'token':account_activation_token.make_token(obj),})
		to_email = obj.email
		email = EmailMultiAlternatives(
                        mail_subject, to=[to_email])
		email.attach_alternative(message, "text/html")
		email.send()
		return HttpResponse('Registratsiyani tugatish uchun emailni kodini tasdiqlang')
	else:
		return render(request, "home.html")

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        text = 'Faollashdi. Kirish mumkin'
        return HttpResponse(text) #redirect('login', {'text' : text}) #render(request, 'login.html', {'text' : text})
    else:
        return HttpResponse('Faollashtirish kodi xato!')

def mylogin(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username = username, password = password)
		if user is not None:
			login(request, user)
			return HttpResponse("Xush kelibsiz!")
		else:
			return HttpResponse("Parol/Login xato yoki email tasdiqlanmagan")
	else:
		return render(request, 'login.html')
