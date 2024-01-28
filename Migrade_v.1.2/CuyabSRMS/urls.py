from django import forms
from django.contrib import admin
from django.urls import URLPattern, path, include


from CuyabSRMS import AdminViews, TeacherViews, GenerationViews

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
    path('update_profile_photo', views.update_profile_photo, name='update_profile_photo'),
    path('update_teacher_profile', views.update_teacher_profile, name='update_teacher_profile'),
    path('change_password/', views.change_password, name='change_password'), 
    path('admin_profile_page/', views.admin_profile_page, name='admin_profile_page'),
    path('admin_update_profile_photo', views.admin_update_profile_photo, name='admin_update_profile_photo'),
    path('admin_update_profile', views.admin_update_profile, name='admin_update_profile'), 
    path('admin_change_password/', views.admin_change_password, name='admin_change_password'),
    path('password_reset_sent', views.password_reset_sent, name='password_reset_sent'),
    path('teachers_activity', views.teachers_activity, name='teachers_activity'),
    path('admin_activity', views.admin_activity, name='admin_activity'),
    

    




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
    path('sf10/', AdminViews.sf10_views, name='sf10_view'),
    path('add_subject/', AdminViews.add_subject, name='add_subject'),
    path('subject_list/', AdminViews.subject_list, name='subject_list'),
    # path('edit/', AdminViews.edit_extracted_data, name='edit_extracted_data'),
    path('save/', AdminViews.save_edited_data, name='save_edited_data'),
    path('update_subject/<int:subject_id>/', AdminViews.update_subject, name='update_subject'),
    path('delete_subject/<int:subject_id>/', AdminViews.delete_subject, name='delete_subject'),




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
    path('get_grade_details', teacher_required(TeacherViews.get_grade_details), name='get_grade_details'),
    path('students', teacher_required(TeacherViews.get_students_by_grade_and_section), name='students'),
    path('calculate_grades', teacher_required(TeacherViews.calculate_grades), name='calculate_grades'),
    path('display_classrecord', teacher_required(TeacherViews.display_classrecord), name='display_classrecord'),
    path('get_sections/', teacher_required(TeacherViews.get_sections), name='get_sections'),
    path('display_students/', teacher_required(TeacherViews.display_students), name='display_students'),
    path('student_list_for_class', teacher_required(TeacherViews.student_list_for_class), name='student_list_for_class'),

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
    path('get_grade_details', TeacherViews.get_grade_details, name='get_grade_details'),
    path('students', TeacherViews.get_students_by_grade_and_section, name='students'),
    path('calculate_grades', TeacherViews.calculate_grades, name='calculate_grades'),
    path('get_sections/', TeacherViews.get_sections, name='get_sections'),
    path('display_classrecord/<int:class_record_id>/', TeacherViews.display_classrecord, name='display_classrecord'),
    path('display_students', TeacherViews.display_students, name='display_students'),
    path('delete_student/<str:grade>/<str:section>/',TeacherViews.delete_student, name='delete_student'),
    path('view_classrecord', TeacherViews.view_classrecord, name='view_classrecord'),
    path('edit_record/<int:record_id>/', TeacherViews.edit_record, name='edit_record'),
    path('display_quarterly_summary/<str:grade>/<str:section>/<str:subject>/<int:class_record_id>/', TeacherViews.display_quarterly_summary, name='display_quarterly_summary'),
    path('display_final_grades/<str:grade>/<str:section>/<str:subject>/', TeacherViews.display_final_grades, name='display_final_grades'),
    path('update_score/', TeacherViews.update_score, name='update_score'),
    path('update_highest_possible_scores/', TeacherViews.update_highest_possible_scores, name='update_highest_possible_scores'),
    path('class_records/<int:class_record_id>/delete/', TeacherViews.delete_classrecord, name='delete_classrecord'),
    path('class_records/', TeacherViews.class_records_list, name='class_records_list'),
    path('grade_summary/<str:grade>/<str:section>/<str:quarter>/', TeacherViews.grade_summary, name='grade_summary'),
    path('all_final_grades/<str:grade>/<str:section>/', TeacherViews.display_all_final_grades, name='all_final_grades'),
    path('update_total_max_quarterly/', TeacherViews.update_total_max_quarterly, name='update_total_max_quarterly'),
    path('validate_score/', TeacherViews.validate_score, name='validate_score'),
    # path('sf9/', TeacherViews.sf9, name='sf9'),
   # urls.py

    # Generation

    path('generate_excel_for_grades/<str:grade>/<str:section>/<str:subject>/', GenerationViews.generate_excel_for_grades, 
         name='generate_excel_for_grades'),
    path('generate-excel-sf9/<int:student_id>/', GenerationViews.generate_excel_for_sf9, name='generate_excel_for_sf9')



    # # Student
    # path('student_list/', StudentViews.student_list, name='student_list'),

]



 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)