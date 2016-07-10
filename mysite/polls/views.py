from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from polls.models import Question, Choice, UserProfile
from django.template import RequestContext, loader
from django.http import Http404
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.models import User
from polls.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

class IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'latest_question_list'

	def get_queryset(self):
		"""Return the last five published questions."""
		return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]



class DetailView(generic.DetailView):
	model = Question
	template_name = 'polls/detail.html'

class ResultsView(generic.DetailView):
	model = Question
	template_name = 'polls/results.html'




def index(request):
	return HttpResponse("Hello world. you are at the polls index.")


def results(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	return render(request, 'polls/results.html', {'question': question})



def questions(request):
	latest_question_list = Question.objects.order_by('-pub_date')[:5]
	template = loader.get_template('polls/questions.html')
	context = RequestContext(request, {'latest_question_list': latest_question_list,})
	#output = ', '.join([p.question_text for p in latest_question_list])
	return HttpResponse(template.render(context))

def detail(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	return render(request, 'polls/detail.html', {'question': question})


def selectquestion(request):
	latest_question_list = Question.objects.order_by('-pub_date')[:5]
	template = loader.get_template('polls/selectquestion.html')
	context = RequestContext(request, {'latest_question_list': latest_question_list,})
	#output = ', '.join([p.question_text for p in latest_question_list])
	return HttpResponse(template.render(context))


@login_required
def vote(request, question_id):

	p = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = p.choice_set.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		return render(request, 'polls/detail.html', {
			'question': p,
			'error_message': "You didn't select a choice.",
		})
	
	else:
		selected_choice.votes += 1
		selected_choice.save()
       
		return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))



def register(request):
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		pass1 = request.POST.get('password')
		pass2 = request.POST.get('p2')
		if user_form.is_valid() and profile_form.is_valid():
			if (pass1 != pass2 ):
				user_form.non_field_errors = 'Passwords did not match.'
				print user_form.non_field_errors
			else:
				user = user_form.save()
				user.set_password(user.password)
				user.save()
	
				profile = profile_form.save(commit=False)
				profile.user = user
				profile.save()
				registered = True
		else:
			print user_form.errors, profile_form.errors

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
	
	return render(request,
		'polls/register.html',
		{'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def editprofile(request):
	edited = False
	errormsg = ""
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		fn = request.POST.get('first_name')
		ln = request.POST.get('last_name')
		emailid = request.POST.get('email')
		u = User.objects.get(username = username)
		user = authenticate(username=username, password=password)
		if user:		
			u.first_name = fn
			u.last_name = ln
			u.email = emailid	
			u.save()
			edited = True
		else:
			errormsg = "Wrong Password. Please Try Again."
			print errormsg			
	else:
		return render(request, 'polls/editprofile.html', {})

	return render(request,
		'polls/editprofile.html',
		{'edited': edited, 'errormsg':errormsg})



def changepassword(request):
	errormsg = ""
	changed = False
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		p1 = request.POST.get('p1')
		p2 = request.POST.get('p2')
		u = User.objects.get(username = username)
		user = authenticate(username=username, password=password)
		if user:
			if (p1 != p2):
				errormsg = "new passwords did not match.."
				print errormsg
			else:
				if (p1 == ""):
					errormsg = "new password field can't be empty"
					print errormsg
				else:
					u.set_password(p1)
					u.save()
					changed = True
		else:
			errormsg = "Wrong Password. Please Try Again."
			print errormsg			
	else:			
		return render(request, 'polls/changepassword.html', {})

	return render(request,
		'polls/changepassword.html',
		{'changed': changed, 'errormsg':errormsg})





	

def user_login(request):
	errormsg = ""
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/polls/')
			else:
				return HttpResponse("your polls account is disabled.")

		else:
			errormsg = "Inavalid Login Details.."
			print errormsg
	else:
		return render(request, 'polls/login.html', {})

	return render(request,
		'polls/login.html',
		{'errormsg':errormsg})



@login_required
def restricted(request):
	return HttpResponse("Since you are logged in, you can see this text!")


@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/polls/')	



# Create your views here.
