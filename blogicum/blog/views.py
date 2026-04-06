from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest
from django.core.paginator import Paginator
from django import forms
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView

from core.forms import UserEditForm
from .forms import CommentForm
from .models import Post, Category, Comment

User = get_user_model()


# Create your views here.
def index(request: HttpRequest):
    posts = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).order_by('-pub_date')
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request: HttpRequest, id: int):
    post = get_object_or_404(Post, id=id)
    if not post.is_viewable_by(request.user):
        raise Http404()

    comments = Comment.objects.filter(post=post).order_by('created_at')
    return render(
        request,
        'blog/detail.html',
        {'post': post, 'form': CommentForm(), 'comments': comments},
    )


def category_posts(request: HttpRequest, category_slug: str):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    posts = (
        Post.objects.filter(
            category=category, is_published=True, pub_date__lte=timezone.now()
        )
        .order_by('-pub_date')
        .select_related('category')
    )
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj},
    )


def profile(request: HttpRequest, username: str):
    usr = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=usr).order_by('-pub_date')
    if usr != request.user:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(
        request, 'blog/profile.html', {'profile': usr, 'page_obj': page_obj}
    )


@login_required
def edit_profile(request: HttpRequest):
    user = request.user
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserEditForm(instance=user)

    return render(request, 'blog/user.html', {'form': form})


class CreatePost(LoginRequiredMixin, CreateView):
    model = Post
    fields = [
        'title',
        'text',
        'pub_date',
        'is_published',
        'location',
        'category',
        'image',
    ]
    template_name = 'blog/create.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Use Django's built-in DateTimeInput with proper type
        form.fields['pub_date'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'},
            format='%Y-%m-%dT%H:%M',
        )
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class EditPost(LoginRequiredMixin, UpdateView):
    model = Post
    fields = [
        'title',
        'text',
        'pub_date',
        'is_published',
        'location',
        'category',
        'image',
    ]
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.author != request.user:
            return redirect('blog:post_detail', id=obj.id)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'id': self.get_object().id})


class DeletePost(LoginRequiredMixin, DeleteView):
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        return super().get_object(queryset.filter(author=self.request.user))

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = forms.Form()
        ctx['form'].instance = self.object
        return ctx


@login_required
def add_comment(request: HttpRequest, post_id: int):
    if request.method != 'POST':
        return HttpResponse(status=405)
    post = get_object_or_404(Post, id=post_id)
    if not post.is_viewable_by(request.user):
        raise Http404()

    form = CommentForm(request.POST)
    if not form.is_valid():
        raise BadRequest()

    comment = Comment(
        post=post, author=request.user, text=form.cleaned_data['text']
    )
    comment.save()

    return redirect('blog:post_detail', post_id)


class CommentMixin(LoginRequiredMixin):
    model = Comment
    fields = ['text']
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        return super().get_object(
            queryset.filter(
                author=self.request.user, post_id=self.kwargs['post_id']
            )
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs['post_id']},
        )


class EditComment(CommentMixin, UpdateView):
    pass


class DeleteComment(CommentMixin, DeleteView):
    pass
