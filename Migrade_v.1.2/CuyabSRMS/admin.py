from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from CuyabSRMS.models import CustomUser
from CuyabSRMS.models import CustomUser, Admin, Teacher, Student, Grade, Section

class UserModel(UserAdmin):
    pass

admin.site.register(CustomUser, UserModel)


# Register the Admin model
@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'created_at', 'updated_at')

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
