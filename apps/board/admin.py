from django.contrib import admin

from .models import Ban, Board, Category, Post, SpamWord, Thread


class PostsInline(admin.TabularInline):
    model = Post
    fields = ('is_op_post', 'timestamp', 'subject', 'comment', 'ip')
    readonly_fields = ('timestamp', 'is_op_post')
    fk_name = 'thread'


class ThreadAdmin(admin.ModelAdmin):
    inlines = (PostsInline,)
    list_display = (
        'board', 'thread_num', 'is_pinned',
        'is_closed', 'bump_limit', 'lasthit'
    )
    ordering = ('-lasthit',)

    def save_related(self, request, form, formsets, change):
        op_post = formsets[0][0].instance
        if op_post:
            obj = op_post
            obj.is_op_post = True
            super().save_related(
                request, form, formsets, change
            )

    def delete_queryset(self, request, queryset):
        Post.objects.filter(thread__in=queryset).update(is_removed=True)
        super().delete_queryset(request, queryset)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('posts')


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'num', 'thread', 'subject',
        'name', 'tripcode', 'ip',
        'is_op_post', 'timestamp',
    )
    list_filter = ('is_op_post', 'timestamp',)
    list_select_related = ('thread',)
    readonly_fields = ('parent', 'is_op_post',)
    ordering = ('-timestamp',)


class SpamWordAdmin(admin.ModelAdmin):
    list_display = ('pattern', 'for_all_boards', 'created',)
    list_filter = ('boards', 'created', 'for_all_boards')
    search_fields = ('expression',)
    readonly_fields = ('created',)
    ordering = ('-created',)


class BoardAdmin(admin.ModelAdmin):
    list_display = (
        'board', 'board_name', 'category', 'bump_limit',
        'thread_limit', 'get_filesize',
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'order', 'is_hidden',
    )


class BanAdmin(admin.ModelAdmin):
    list_display = (
        'inet', 'board', 'for_all_boards',
        'duration', 'created',
    )
    list_filter = ('board', 'for_all_boards', 'created',)
    search_fields = ('inet',)
    readonly_fields = ('created',)
    ordering = ('-created',)

    list_select_related = ('board',)


admin.site.register(Post, PostAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Board, BoardAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SpamWord, SpamWordAdmin)
admin.site.register(Ban, BanAdmin)
