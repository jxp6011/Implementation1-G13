from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.db.models import Q


from allauth.account.views import PasswordChangeView
from allauth.account.models import EmailAddress

from .models import Post, User, Comment, Like
from .forms import PostCreateForm, PostUpdateForm, ProfileForm, CommentForm
from .functions import confirmation_required_redirect
from .mixins import LoginAndVerificationRequiredMixin, LoginAndOwnershipRequiredMixin

from braces.views import LoginRequiredMixin, UserPassesTestMixin

# Create your views here.
def index(request):
    return render(request, 'yours/index.html')



class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    def get_success_url(self):
        return reverse('profile', kwargs={'user_id': self.request.user.id})



class IndexView(ListView):
    model = Post
    template_name = 'yours/index.html'
    context_object_name = 'posts'
    paginate_by = 8
    
    def get_queryset(self):
        return Post.objects.filter(is_sold=False)
    


class WishlistView(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = 'liked_posts'
    template_name = 'yours/wishlist.html'
    paginate_by = 8

    def get_queryset(self):
        return Post.objects.filter(likes__user=self.request.user)




class FollowingPostListView(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = 'following_posts'
    template_name = 'yours/following_post_list.html'
    paginate_by = 8

    def get_queryset(self):
        return Post.objects.filter(is_sold=False).filter(author__followers=self.request.user)


class SearchView(ListView):
    model = Post
    context_object_name = 'search_results'
    template_name = 'yours/search_results.html'
    paginate_by = 8

    def get_queryset(self):
        query = self.request.GET.get('query', '') 
        return Post.objects.filter(
            is_sold=False
        ).filter(
            Q(title__contains=query) 
            | Q(item_details__contains=query)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query', '') 
        return context





class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'yours/post_detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['post_ctype_id'] = ContentType.objects.get(model='post').id
        context['comment_ctype_id'] = ContentType.objects.get(model='comment').id

        user = self.request.user
        if user.is_authenticated:
            post = self.object
            context['likes_post'] = Like.objects.filter(user=user, post=post).exists()
            context['liked_comments'] = Comment.objects.filter(post=post).filter(likes__user=user)

        return context




class PostCreateView(LoginAndVerificationRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'yours/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post-detail', kwargs={'post_id': self.object.id})

    # redirect_unauthenticated_users = True
    # raise_exception = confirmation_required_redirect

    # def get_success_url(self):
    #     return reverse('post-detail', kwargs={'post_id': self.object.id})
    
    # def form_valid(self, form):
    #     form.instance.author = self.request.user
    #     return super().form_valid(form)
    
    # def test_func(self, user):
    #     return EmailAddress.objects.filter(user=user, verified=True).exists()
    
    
    


class PostUpdateView(LoginAndOwnershipRequiredMixin, UpdateView):
    model = Post
    form_class = PostUpdateForm
    template_name = 'yours/post_form.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('post-detail', kwargs={'post_id': self.object.id})

    # raise_exception = True
    # redirect_unauthenticated_users = False

    # def get_success_url(self):
    #     return reverse('post-detail', kwargs={'post_id': self.object.id})
    
    # def test_func(self, user):
    #     post = self.get_object()
    #     return post.author == user
    
    



class PostDeleteView(LoginAndOwnershipRequiredMixin, DeleteView):
    model = Post
    template_name = 'yours/post_confirm_delete.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('index')

    # raise_exception = True
    # redirect_unauthenticated_users = False

    # def get_success_url(self):
    #     return reverse('index')
    
    # def test_func(self, user):
    #     post = self.get_object()
    #     return post.author == user
    


class CommentCreateView(LoginAndVerificationRequiredMixin, CreateView):
    http_method_names = ['post']

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(id=self.kwargs.get('post_id'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post-detail', kwargs={'post_id': self.kwargs.get('post_id')})

    # redirect_unauthenticated_users = True
    # raise_exception = confirmation_required_redirect

    # def form_valid(self, form):
    #     form.instance.author = self.request.user
    #     form.instance.post = Post.objects.get(id=self.kwargs.get('post_id'))
    #     return super().form_valid(form)
    
    # def get_success_url(self):
    #     return reverse('post-detail', kwargs={'post_id': self.kwargs.get('post_id')})
    
    # def test_func(self, user):
    #     return EmailAddress.objects.filter(user=user, verified=True).exists()



class CommentUpdateView(LoginAndOwnershipRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'yours/comment_update_form.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('post-detail', kwargs={'post_id': self.object.post.id})



class CommentDeleteView(LoginAndOwnershipRequiredMixin, DeleteView):
    model = Comment
    template_name = 'yours/comment_confirm_delete.html'
    pk_url_kwarg = 'comment_id'
    
    def get_success_url(self):
        return reverse('post-detail', kwargs={'post_id': self.object.post.id})


class ProcessLikeView(LoginAndVerificationRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type_id=kwargs.get('content_type_id'), 
            object_id=kwargs.get('object_id'),
        )
        if not created:
            like.delete()

        return redirect(request.META['HTTP_REFERER'])




class ProfileView(DetailView):
    model = User
    template_name = 'yours/profile.html'
    pk_url_kwarg = 'user_id'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile_user_id = self.kwargs.get('user_id')
        if user.is_authenticated:
            context['is_following'] = user.following.filter(id=profile_user_id).exists()
        context['user_posts'] = Post.objects.filter(author__id=profile_user_id)[:8]
        return context



class ProcessFollowView(LoginAndVerificationRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        user = request.user
        profile_user_id = kwargs.get('user_id')
        if user.following.filter(id=profile_user_id).exists():
            user.following.remove(profile_user_id)
        else:
            user.following.add(profile_user_id)
        return redirect('profile', user_id=profile_user_id)




class ProfileSetView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'yours/profile_set_form.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('index')




class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'yours/profile_update_form.html'

    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        return reverse('profile', kwargs={'user_id': self.request.user.id})




class UserPostListView(ListView):
    model = Post
    template_name = 'yours/user_post_list.html'
    context_object_name = 'user_posts'
    paginate_by = 8

    def get_queryset(self):
        #user_id = self.kwargs.get('user_id')
        return Post.objects.filter(author__id=self.kwargs.get('user_id'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = get_object_or_404(User, id=self.kwargs.get('user_id'))
        return context




