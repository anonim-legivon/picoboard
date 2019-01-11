import hashlib
import re

from django.core.files.images import get_image_dimensions
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_regex.fields import RegexField
from model_utils.models import SoftDeletableModel
from netfields import CidrAddressField, NetManager


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
    board = models.CharField(_('название'), max_length=32, unique=True)
    board_name = models.CharField(
        _('название доски'), max_length=48,
    )
    description = models.TextField(_('описание'), blank=True, default='')
    bump_limit = models.PositiveSmallIntegerField(
        _('бамп лимит'), default=500
    )
    thread_limit = models.PositiveSmallIntegerField(
        _('максимум тредов'), default=200
    )
    filesize_limit = models.PositiveIntegerField(
        _('лимит на размер файлов'), default=(2 ** 20) * 20
    )
    enable_trips = models.BooleanField(_('разрешены трип коды'), default=False)
    trip_required = models.BooleanField(
        _('генерировать трип код'), default=False
    )
    enable_sage = models.BooleanField(_('sage включена'), default=True)
    enable_subject = models.BooleanField(
        _('разрешены темы постов'), default=True
    )
    enable_names = models.BooleanField(_('разрешены имена'), default=False)
    default_name = models.CharField(
        _('имя в постах'), max_length=48, default=_('Аноним')
    )

    class Meta:
        verbose_name = _('доска')
        verbose_name_plural = _('доски')

    def __str__(self):
        return f'{self.board}'

    def save(self, *args, **kwargs):
        if not self.enable_names and self.enable_trips:
            self.enable_names = True

        super().save(*args, **kwargs)

    @property
    def last_num(self):
        try:
            pid = Post.objects.only("thread", "num").filter(
                thread__board=self.id
            ).latest('num').num
        except Post.DoesNotExist:
            pid = 0

        return pid

    @property
    def get_filesize(self):
        return f'{self.filesize_limit / 2 ** 20} Mb'

    get_filesize.fget.short_description = _('максимальный размер файлов')


class Thread(models.Model):
    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name='threads',
        verbose_name=_('доска'),
    )
    is_pinned = models.BooleanField(_('закреплен'), default=False)
    is_closed = models.BooleanField(_('закрыт'), default=False)
    lasthit = models.DateTimeField(_('последний пост'), auto_now=True)

    class Meta:
        verbose_name = _('тред')
        verbose_name_plural = _('треды')

    def __str__(self):
        return f'{self.op_post}'

    @cached_property
    def op_post(self):
        """
        Метод из списка всех постов в тереде
        ищет иденственный пост с пометкой `is_op_post` и возвращает его
        """
        for post in self.posts.all():
            if post.is_op_post:
                return post

    @cached_property
    def thread_num(self):
        return self.op_post.num if self.op_post else -1

    @property
    def last_posts(self):
        thread_posts = self.posts.all()
        t_length = thread_posts.count()

        if t_length == 1:
            return None

        return (
            thread_posts[1:t_length]
            if t_length < 5 else
            thread_posts[t_length - 3:t_length]
        )

    @property
    def posts_count(self):
        return self.posts.count()

    @property
    def bump_limit(self):
        return self.posts_count > self.board.bump_limit

    bump_limit.fget.short_description = _('бамп лимит')


class Post(models.Model):
    num = models.PositiveIntegerField(
        _('id поста'), blank=True,
        db_index=True
    )
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE,
        related_name='posts', verbose_name=_('тред'),
    )
    parent = models.PositiveIntegerField(
        _('родитель'), blank=True, db_index=True
    )
    is_op_post = models.BooleanField(_('первый пост в треде'), default=False)
    timestamp = models.DateTimeField(_('время'), auto_now_add=True)
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
    sage = models.BooleanField(_('sage'), default=False, blank=True)

    class Meta:
        verbose_name = _('пост')
        verbose_name_plural = _('посты')
        get_latest_by = 'id'
        ordering = ['id']

    def __str__(self):
        return f'{self.num}'

    def save(self, *args, **kwargs):
        self.num = self.thread.board.last_num + 1

        if self.is_op_post or not (self.sage or self.thread.bump_limit):
            self.thread.lasthit = timezone.now()
            self.thread.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_op_post:
            self.thread.delete()

        super().delete(*args, **kwargs)


def resolve_save_path(instance, filename):
    thread = instance.post.thread.thread_num
    board = instance.post.thread.board.board

    now = timezone.now()
    timestamp = int(now.timestamp() * 10000)
    date = now.strftime('%Y/%m/%d')
    return (
        f'{date}/{board}/{thread}/{timestamp}.{filename.split(".")[-1:]}'
    )


class File(models.Model):
    IMAGE = 0
    VIDEO = 1

    TYPES = (
        (IMAGE, _('картинка')),
        (VIDEO, _('видео'))
    )
    file = models.FileField(_('файл'), upload_to=resolve_save_path)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='files',
        verbose_name=_('пост')
    )
    fullname = models.CharField(
        _('оригинальное название'), max_length=255, db_index=True
    )
    height = models.IntegerField(_('высота'), blank=True, default=0)
    width = models.IntegerField(_('ширина'), blank=True, default=0)
    type = models.PositiveSmallIntegerField(
        choices=TYPES, verbose_name=_('тип')
    )
    md5 = models.TextField(_('MD5 хэш'), blank=True, default='')

    class Meta:
        verbose_name = _('файл')
        verbose_name_plural = _('файлы')

    def __str__(self):
        return f'{self.file.name}'

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.type == self.IMAGE:
                width, height = get_image_dimensions(self.file.file)
                self.width = width
                self.height = height
            self.fullname = self.file.name
            md5 = hashlib.md5()
            for chunk in self.file.chunks():
                md5.update(chunk)
            self.md5 = md5.hexdigest()

        super().save(*args, **kwargs)


class SpamWord(models.Model):
    expression = RegexField(
        flags=re.IGNORECASE, verbose_name=_('регулярное выражение')
    )
    boards = models.ManyToManyField(
        'Board', related_name='spam_words', blank=True,
        verbose_name=_('доски')
    )
    for_all_boards = models.BooleanField(_('для всех досок'), default=False)
    created = models.DateTimeField(_('создано'), auto_now_add=True)

    class Meta:
        verbose_name = _('спам слово')
        verbose_name_plural = _('спам слова')

    def __str__(self):
        return f'{self.expression.pattern}'

    # TODO: Условия сохранения полей
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def pattern(self):
        return self.expression.pattern

    pattern.fget.short_description = _('паттерн')


class Ban(models.Model):
    objects = NetManager()

    inet = CidrAddressField(verbose_name=_('CIDR'), db_index=True)
    board = models.ForeignKey(
        'Board', on_delete=models.CASCADE, null=True,
        related_name='bans', blank=True, verbose_name=_('доска')
    )
    for_all_boards = models.BooleanField(_('для всех досок'), default=False)
    reason = models.TextField(_('причина'), blank=True, default='')
    duration = models.DurationField(_('длительность'))
    created = models.DateTimeField(_('создан'), auto_now_add=True)

    class Meta:
        verbose_name = _('бан')
        verbose_name_plural = _('баны')

    def __str__(self):
        return f'Бан: {self.inet} [{self.duration}]'

    def save(self, *args, **kwargs):
        if self.for_all_boards:
            self.board = None
        if not self.board:
            self.for_all_boards = True

        super().save(*args, **kwargs)
