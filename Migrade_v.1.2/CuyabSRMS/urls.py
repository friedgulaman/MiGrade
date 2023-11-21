from django import forms
from django.contrib import admin
from django.urls import URLPattern, path, include
from CuyabSRMS import AdminViews, TeacherViews
from django.contrib import admin
from . import views

from django.conf.urls.static import static
from django.conf import settings

from django.conf import settings
from django.conf.urls.static import static
from .ForgotPassword import ResetPasswordView
from django.contrib.auth import views as auth_views
from .teacher_required import teacher_required
from .admin_required import admin_required





urlpatterns = [
    path('', views.ShowLoginPage),
    path('doLogin/', views.doLogin, name='doLogin'),
    path('doLogin', views.ShowLoginPage, name='ShowLoginPage'),
    path('get_user_details/', views.get_user_details),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('profile_page/', views.profile_page, name='profile_page'),
    path('password_reset_sent', views.password_reset_sent, name='password_reset_sent'),
    path('teachers_activity', views.teachers_activity, name='teachers_activity'),
    path('update_profile_photo', views.update_profile_photo, name='update_profile_photo'),
    path('update_teacher_profile', views.update_teacher_profile, name='update_teacher_profile'),       
    path('change_password/', views.change_password, name='change_password'),




    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
   
    # Admin Views
    path('home_admin', admin_required(AdminViews.home_admin), name="home_admin"),
    path('add_teacher', admin_required(AdminViews.add_teacher), name="add_teacher"),
    path('add_teacher_save', admin_required(AdminViews.add_teacher_save), name="add_teacher_save"),
    path('assign_teacher', admin_required(AdminViews.assign_teacher), name="assign_teacher"),
    path('list_of_teachers', admin_required(AdminViews.teacherList), name="list_of_teachers"),
    path('submit_grade_section', admin_required(AdminViews.submit_grade_section), name='submit_grade_section'),
    path('get_sections/', admin_required(AdminViews.get_sections), name='get_sections'),
    path('assign_teacher', admin_required(AdminViews.assign_teacher), name="assign_teacher"),
    path('save_assignment/', admin_required(AdminViews.save_assignment), name='save_assignment'),
    path('add_grade_section', admin_required(AdminViews.add_grade_section), name='add_grade_section'),
    path('search/', admin_required(AdminViews.search_students), name='search_students'),
    path('upload_documents/', admin_required(AdminViews.upload_documents_ocr), name='upload_documents'),
    path('save_edited_data/', admin_required(AdminViews.save_edited_data), name='save_edited_data'),
    path('sf10/', admin_required(AdminViews.sf10_views), name='sf10_view'),
    path('add_subject/', admin_required(AdminViews.add_subject), name='add_subject'),
    path('subject_list/', admin_required(AdminViews.subject_list), name='subject_list'),




    # Adviser Teacher
    path('home_teacher', teacher_required(TeacherViews.home_teacher), name="home_teacher"),
    path('home_adviser_teacher', teacher_required(TeacherViews.home_adviser_teacher), name="home_adviser_teacher"),
    path('dashboard', teacher_required(TeacherViews.dashboard), name="dashboard"),   
    path('upload_adviser_teacher', teacher_required(TeacherViews.upload_adviser_teacher), name="upload_adviser_teacher"),   
    path('upload', teacher_required(TeacherViews.upload), name='upload'),
    path('save_json_data', teacher_required(TeacherViews.save_json_data), name='save_json_data'),
    path('new_classrecord', teacher_required(TeacherViews.new_classrecord), name='new_classrecord'),
    path('classes', teacher_required(TeacherViews.classes), name='classes'),
    path('class_record', teacher_required(TeacherViews.class_record), name='class_record'),
    path('get_grades_and_sections', teacher_required(TeacherViews.get_grades_and_sections), name='get_grades_and_sections'),
    path('calculate_grades', teacher_required(TeacherViews.calculate_grades), name='calculate_grades'),
    path('get_grade_details/', teacher_required(TeacherViews.get_grade_details), name='get_grade_details'),
    path('students', teacher_required(TeacherViews.get_students_by_grade_and_section), name='students'),
    path('calculate_grades', teacher_required(TeacherViews.calculate_grades), name='calculate_grades'),
    path('display_classrecord', teacher_required(TeacherViews.display_classrecord), name='display_classrecord'),
    path('get_sections/', teacher_required(TeacherViews.get_sections), name='get_sections'),
    path('display_students/', teacher_required(TeacherViews.display_students), name='display_students'),
    path('student_list_for_class', teacher_required(TeacherViews.student_list_for_class), name='student_list_for_class'),

]



 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)