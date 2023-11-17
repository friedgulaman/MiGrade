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
    # Admin
    path('home_admin', AdminViews.home_admin, name="home_admin"),
    path('add_teacher', AdminViews.add_teacher, name="add_teacher"),
    path('add_teacher_save', AdminViews.add_teacher_save, name="add_teacher_save"),
    path('assign_teacher', AdminViews.assign_teacher, name="assign_teacher"),
    path('list_of_teachers', AdminViews.teacherList, name="list_of_teachers"),
    path('submit_grade_section', AdminViews.submit_grade_section, name='submit_grade_section'),
    path('get_sections/', AdminViews.get_sections, name='get_sections'),
    path('assign_teacher', AdminViews.assign_teacher, name="assign_teacher"),
    path('save_assignment/', AdminViews.save_assignment, name='save_assignment'),
    path('add_grade_section', AdminViews.add_grade_section, name='add_grade_section'),
    path('search/', AdminViews.search_students, name='search_students'),
    path('upload_documents/', AdminViews.upload_documents_ocr, name='upload_documents'),
    path('save_edited_data/', AdminViews.save_edited_data, name='save_edited_data'),
    path('sf10/', AdminViews.sf10_views, name='sf10_view'),
    path('add_subject/', AdminViews.add_subject, name='add_subject'),
    path('subject_list/', AdminViews.subject_list, name='subject_list'),



    # Adviser Teacher
    path('home_teacher', TeacherViews.home_teacher, name="home_teacher"),
    path('home_adviser_teacher', TeacherViews.home_adviser_teacher, name="home_adviser_teacher"),
    path('dashboard', TeacherViews.dashboard, name="dashboard"),   
    path('upload_adviser_teacher', TeacherViews.upload_adviser_teacher, name="upload_adviser_teacher"),   
    path('upload', TeacherViews.upload, name='upload'),
    path('save_json_data', TeacherViews.save_json_data, name='save_json_data'),
    path('new_classrecord', TeacherViews.new_classrecord, name='new_classrecord'),
    path('classes', TeacherViews.classes, name='classes'),
    path('class_record', TeacherViews.class_record, name='class_record'),
    path('get_grades_and_sections', TeacherViews.get_grades_and_sections, name='get_grades_and_sections'),
    path('calculate_grades', TeacherViews.calculate_grades, name='calculate_grades'),
    path('get_grade_details/', TeacherViews.get_grade_details, name='get_grade_details'),
    path('students', TeacherViews.get_students_by_grade_and_section, name='students'),
    path('calculate_grades', TeacherViews.calculate_grades, name='calculate_grades'),
    path('display_classrecord', TeacherViews.display_classrecord, name='display_classrecord'),
    path('get_sections/', TeacherViews.get_sections, name='get_sections'),


    path('display_students/', TeacherViews.display_students, name='display_students'),
    path('student_list_for_class/', TeacherViews.student_list_for_class, name='student_list_for_class'),



]



 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)