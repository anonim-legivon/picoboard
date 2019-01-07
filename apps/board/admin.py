from django.contrib import admin

from .models import Board, Category, Post, SpamWord, Thread


class PostsInline(admin.TabularInline):
    model = Post
    fields = ('is_op_post', 'date', 'subject', 'comment', 'ip')
    readonly_fields = ('date', 'is_op_post')
    fk_name = 'thread'


class ThreadAdmin(admin.ModelAdmin):
    inlines = (PostsInline,)
    list_display = ('board', 'thread_id',)

    def save_related(self, request, form, formsets, change):
        op_post = formsets[0][0].instance
        if op_post:
            obj = op_post
            obj.is_op_post = True
            super().save_related(
                request, form, formsets, change
            )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('posts')


class PostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'comment', 'date')
    list_select_related = ('thread',)


class SpamWordAdmin(admin.ModelAdmin):
    list_display = ('pattern', 'for_all_boards', 'created',)
    list_filter = ('boards', 'created', 'for_all_boards')
    search_fields = ('expression',)
    readonly_fields = ('created',)


class BoardAdmin(admin.ModelAdmin):
    list_display = (
        'board', 'board_name', 'bump_limit',
        'thread_limit', 'get_filesize',
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'order', 'is_hidden',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Board, BoardAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SpamWord, SpamWordAdmin)
