from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import FormView
from django.conf import settings
# Create your views here.

from .forms import UserRegisterForm,UserUpdateForm, ProfileUpdateForm
from .models import UserProfile

User = get_user_model()



class UserRegisterView(FormView):
    template_name = 'accounts/user_register_form.html'
    form_class = UserRegisterForm
    success_url = '/login'

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get("last_name")
        interest = form.cleaned_data.get("interest")
        print(interest)
        interest = ",".join(interest)
        print(interest)
        new_user = User.objects.create(username=username, email=email , first_name = first_name , last_name = last_name )
        new_user.set_password(password)
        new_user.save()
        profile  = UserProfile.objects.filter(user = new_user).get()
        print(profile)
        profile.interest = interest
        profile.save()
        return super(UserRegisterView, self).form_valid(form)




class UserDetailView(DetailView):
    template_name = 'accounts/user_detail.html'
    queryset = User.objects.all()
    
    def get_object(self):
        return get_object_or_404(
                    User, 
                    username__iexact=self.kwargs.get("username")
                    )
    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailView, self).get_context_data(*args, **kwargs)
        following = UserProfile.objects.is_following(self.request.user, self.get_object())
        context['following'] = following
        context['recommended'] = UserProfile.objects.recommended(self.request.user)
        return context



class UserFollowView(View):
    def get(self, request, username, *args, **kwargs):
        toggle_user = get_object_or_404(User, username__iexact=username)
        if request.user.is_authenticated():
            is_following = UserProfile.objects.toggle_follow(request.user, toggle_user)
            print(is_following)
            print(toggle_user)
        return redirect("profiles:detail", username=username)
        # url = reverse("profiles:detail", kwargs={"username": username})
        # HttpResponseRedirect(ul)

# def login(request):
#     admin_username  = settings.ADMIN_USERNAME
#     admin_password = settings.ADMIN_PASSWORD
#     extra_context = {'admin_username': admin_username, 'admin_password' : admin_password}
#     if extra_context is not None:
#         context.update(extra_context)
#     return TemplateResponse(request, template_name, context)
@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            # messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'accounts/profile.html', context)

