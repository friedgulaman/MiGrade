from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from CuyabSRMS.models import CustomUser, Admin, Teacher, Student, Grade, Section

# Extend the UserAdmin for CustomUser
class UserModel(UserAdmin):
    pass

# Register CustomUser with UserModel
admin.site.register(CustomUser, UserModel)

# Register the Admin model
@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'created_at', 'updated_at')

    def get_username(self, obj):
        return obj.user.username if obj.user else ""

    def get_email(self, obj):
        return obj.user.email if obj.user else ""

    get_username.short_description = 'Username'
    get_email.short_description = 'Email'


# Register the Teacher model
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')

# Register the Student model
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'lrn', 'sex', 'birthday', 'teacher', 'grade', 'section')

# Register the Grade model
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name',)

# Register the Section model
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'teacher')
