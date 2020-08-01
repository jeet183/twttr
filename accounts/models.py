from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from itertools import chain
from PIL import Image

# from .forms import UserRegisterForm

# Create your models here.


class UserProfileManager(models.Manager):
    use_for_related_fields = True

    def all(self):
        qs = self.get_queryset().all()
        try:
            if self.instance:
                qs = qs.exclude(user=self.instance)
        except:
            pass
        return qs

    def toggle_follow(self, user, to_toggle_user):
        user_profile, created = UserProfile.objects.get_or_create(user=user) # (user_obj, true)
        if to_toggle_user in user_profile.following.all():
            user_profile.following.remove(to_toggle_user)
            added = False
        else:
            user_profile.following.add(to_toggle_user)
            added = True
        return added

    def is_following(self, user, followed_by_user):
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            return False
        if followed_by_user in user_profile.following.all():
            return True
        return False

    def recommended(self, user, limit_to=10):
        print(user)
        User = get_user_model()
        superuser = User.objects.filter(is_superuser=True).get()
        profile = user.profile 
        interest = profile.interest
        interest = interest.split(',')
        print(interest)
        recom_profiles = []
        profiles = UserProfile.objects.all().exclude(user=superuser).exclude(id=profile.id)
        print(profiles)
        for p in profiles:
            print(p)
            i = p.interest
            i = i.split(',')
            print(i)
            if(any(x in i for x in interest)):
                recom_profiles.append(p.id)
        print(recom_profiles)
        qs1 = UserProfile.objects.filter(pk__in=recom_profiles)
        # print(qs1)
        following = profile.following.all()
        following = profile.get_following()
        print(following)
        qs1 = qs1.exclude(user__in=following).order_by("?")[:limit_to]
        print(qs1)
        # qs = self.get_queryset().exclude(user = superuser).exclude(user__in=following).exclude(id=profile.id).order_by("?")[:limit_to]
        # print(qs)
        return qs1



class UserProfile(models.Model):
    user        = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile' , on_delete  = models.CASCADE) # user.profile 
    following   = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='followed_by')
    rating      = models.PositiveSmallIntegerField(default=0)
    interest    = models.TextField(blank=True, null=True)
    image       = models.ImageField(default='default.jpg', upload_to='profile_pics')


    # user.profile.following -- users i follow
    # user.followed_by -- users that follow me -- reverse relationship

    objects = UserProfileManager() # UserProfile.objects.all()
    # abc = UserProfileManager() # UserProfile.abc.all()
    def interest_as_list(self):
        print(self.interest.split(','))
        return self.interest.split(',')
    
    def __str__(self):
        return str(self.user.username)
    
    def save(self , *args , **kwargs ):
        super(UserProfile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)



    def get_following(self):
        users  = self.following.all() # User.objects.all().exclude(username=self.user.username)
        return users.exclude(username=self.user.username)

    def get_follow_url(self):
        return reverse_lazy("profiles:follow", kwargs={"username":self.user.username})

    def get_absolute_url(self):
        return reverse_lazy("profiles:detail", kwargs={"username":self.user.username})




# cfe = User.objects.first()
# User.objects.get_or_create() # (user_obj, true/false)
# cfe.save()

def post_save_user_receiver(sender, instance, created, *args, **kwargs):
    if created:
        new_profile = UserProfile.objects.get_or_create(user=instance)
        
        # celery + redis
        # deferred task


post_save.connect(post_save_user_receiver, sender=settings.AUTH_USER_MODEL )






