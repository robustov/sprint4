from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Добавлено"
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text="Идентификатор страницы для URL; разрешены "
        "символы латиницы, цифры, дефис и подчёркивание.",
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(max_length=256, verbose_name="Название места")

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text="Если установить дату и время в будущем "
        "— можно делать отложенные публикации.",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор публикации"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Местоположение",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
    )
    image = models.ImageField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Изображение",
        upload_to="post_images/",
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"

    def is_viewable_by(self, user: User) -> bool:
        return self.author == user or (
            self.is_published
            and self.category.is_published
            and self.pub_date <= timezone.now()
        )

    @property
    def comment_count(self) -> int:
        return self.comments.count()


class Comment(BaseModel):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор комментария"
    )
    text = models.TextField(verbose_name="Текст")
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
