from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_('категория'), max_length=128, unique=True)
    order = models.SmallIntegerField(_('порядок'))
    is_hidden = models.BooleanField(_('доска скрыта'), default=False)

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('категории')

    def __str__(self):
        return f'{self.name}'


class Board(models.Model):
    category = models.ForeignKey(
        Category, verbose_name=_('категория'), related_name='boards',
        on_delete=models.CASCADE
    )
    name = models.CharField(_('название'), max_length=32, unique=True)
    description = models.TextField(_('описание'), blank=True, default='')
    bump_limit = models.PositiveSmallIntegerField(
        _('бамп лимит'), default=500
    )
    thread_limit = models.PositiveSmallIntegerField(
        _('максимум тредов'), default=200
    )
    filesize_limit = models.PositiveIntegerField(
        _('лимит на размер файла'), default=2 ** 20 * 5
    )
    trip_permit = models.BooleanField(_('разрешены трип коды'), default=False)

    class Meta:
        verbose_name = _('доска')
        verbose_name_plural = _('доски')

    def __str__(self):
        return f'{self.name}'

    @property
    def last_pid(self):
        try:
            pid = Post.objects.filter(thread__board=self.id).latest().post_id
        except Post.DoesNotExist:
            pid = 0
        return pid


class Thread(models.Model):
    board = models.ForeignKey(
        Board, verbose_name=_('доска'),
        related_name='threads',
        on_delete=models.CASCADE
    )
    is_pinned = models.BooleanField(_('закреплен'), default=False)
    is_closed = models.BooleanField(_('закрыт'), default=False)
    is_deleted = models.BooleanField(_('удален'), default=False)
    lasthit = models.DateTimeField(_('последний пост'), auto_now=True)

    class Meta:
        verbose_name = _('тред')
        verbose_name_plural = _('треды')

    def __str__(self):
        return f'{self.op_post}'

    @cached_property
    def op_post(self):
        for post in self.posts.all():  # Для Prefetch
            if post.is_op_post:
                return post
            else:
                return None

    @cached_property
    def thread_id(self):
        if self.op_post:
            return self.op_post.post_id
        else:
            return -1

    @property
    def last_posts(self):
        thread_posts = self.posts.all()
        t_length = thread_posts.count()
        if t_length == 1:
            return None
        elif t_length < 5:
            return thread_posts[1:t_length]
        elif t_length >= 5:
            return thread_posts[t_length - 3:t_length]

    @property
    def posts_count(self):
        return self.posts.count()


class Post(models.Model):
    post_id = models.PositiveIntegerField(
        _('id поста'), blank=True,
        db_index=True
    )
    thread = models.ForeignKey(
        Thread, verbose_name=_('тред'),
        related_name='posts',
        on_delete=models.CASCADE
    )
    is_op_post = models.BooleanField(_('первый пост в треде'), default=False)
    date = models.DateTimeField(_('время'), auto_now_add=True)
    is_deleted = models.BooleanField(_('удален'), default=False)
    ip = models.GenericIPAddressField('IP', blank=True, null=True)
    name = models.CharField(
        _('имя'), max_length=48, blank=True,
        default=_('Аноним')
    )
    tripcode = models.CharField(
        _('трипкод'), max_length=48, blank=True,
        default=''
    )
    email = models.EmailField(_('email'), blank=True)
    subject = models.CharField(
        _('тема'), max_length=128, blank=True,
        default=''
    )
    password = models.CharField(
        _('пароль'), max_length=64, blank=True,
        default=''
    )
    comment = models.TextField(_('сообщение'), blank=True, default='')

    class Meta:
        verbose_name = _('пост')
        verbose_name_plural = _('посты')
        get_latest_by = 'id'
        ordering = ['id']

    def __str__(self):
        return f'{self.post_id}'

    def save(self, **kwargs):
        self.post_id = self.thread.board.last_pid + 1
        # TODO: Проверить на race condition при сохранении
        self.thread.lasthit = timezone.now()
        self.thread.save()
        super(Post, self).save(**kwargs)

    def delete(self, **kwargs):
        super(Post, self).delete(**kwargs)
        if self.is_op_post:
            self.thread.delete()
