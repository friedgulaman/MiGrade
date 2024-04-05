from django import forms
from django.contrib import admin
from django.urls import URLPattern, path, include


from CuyabSRMS import AdminViews, TeacherViews, GenerationViews, ArchivedViews, TransferRecordViews, SuperAdminViews, MasterTeacherViews

from .DashboardViews import StudentChartDataView
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
from .mt_required import mt_required
from .super_required import super_required
from django.urls import path  #eto saka sa baba
from . import TeacherViews






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
    path('mt_profile_page/', views.mt_profile_page, name='mt_profile_page'),
    path('mt_update_profile_photo', views.mt_update_profile_photo, name='mt_update_profile_photo'),
    path('mt_update_profile', views.mt_update_profile, name='mt_update_profile'), 
    path('mt_change_password/', views.mt_change_password, name='mt_change_password'),
    path('mt_profile_page/', views.mt_profile_page, name='mt_profile_page'),
    path('mt_update_profile_photo', views.mt_update_profile_photo, name='mt_update_profile_photo'),
    path('mt_update_profile', views.mt_update_profile, name='mt_update_profile'), 
    path('mt_change_password/', views.mt_change_password, name='mt_change_password'),
    path('super_profile_page/', views.super_profile_page, name='super_profile_page'),
    path('super_update_profile_photo', views.super_update_profile_photo, name='super_update_profile_photo'),
    path('super_update_profile', views.super_update_profile, name='super_update_profile'), 
    path('super_change_password/', views.super_change_password, name='super_change_password'),
    path('super_profile_page/', views.super_profile_page, name='super_profile_page'),
    path('super_update_profile_photo', views.super_update_profile_photo, name='super_update_profile_photo'),
    path('super_update_profile', views.super_update_profile, name='super_update_profile'), 
    path('super_change_password/', views.super_change_password, name='super_change_password'),
    path('password_reset_sent', views.password_reset_sent, name='password_reset_sent'),
    path('activity', views.activity, name='activity'),

    path('faqs', teacher_required(TeacherViews.faqs), name='faqs'),  # etoo gar
    path('documentation', teacher_required(TeacherViews.documentation), name='documentation'),  # etoo gar
    path('about', teacher_required(TeacherViews.about), name='about'),  # etoo gar
    path('adviser_manual', teacher_required(TeacherViews.adviser_manual), name='adviser_manual'),  # etoo gar
    path('subject_manual', teacher_required(TeacherViews.subject_manual), name='subject_manual'),  # etoo gar
    path('submit_feedback', teacher_required(TeacherViews.submit_feedback), name='submit_feedback'),
    path('privacy-policy/', teacher_required(TeacherViews.privacy_policy_view), name='privacy_policy'),
    path('terms-and-conditions/', teacher_required(TeacherViews.terms_and_conditions_view), name='terms_and_conditions'),



    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

   
    # Admin Views
    path('home_admin', admin_required(AdminViews.home_admin), name="home_admin"),
    path('teachers', admin_required(AdminViews.teachers), name="teachers"),
    path('grade_and_section', admin_required(AdminViews.grade_and_section), name="grade_and_section"),
    path('subjects', admin_required(AdminViews.subjects), name="subjects"),
    path('students', admin_required(AdminViews.students), name="students"),
    path('add_student', admin_required(AdminViews.add_student), name="add_student"),
    path('student_lists', admin_required(AdminViews.student_lists), name="student_lists"),
    path('get_student_details', admin_required(AdminViews.get_student_details), name='get_student_details'),
    path('update_student_details', admin_required(AdminViews.update_student_details), name='update_student_details'),
    path('delete_student', admin_required(AdminViews.delete_student), name='delete_student'),
    path('quarters', admin_required(AdminViews.quarters), name="quarters"),
    path('get_quarters_data/', admin_required(AdminViews.get_quarters_data), name='get_quarters_data'),
    path('add_quarter/', admin_required(AdminViews.add_quarter), name='add_quarter'),
    path('update_quarter/', admin_required(AdminViews.update_quarter), name='update_quarter'),
    path('delete_quarter/', admin_required(AdminViews.delete_quarter), name='delete_quarter'),
    path('student_lists/<str:grade>/<str:section>/', admin_required(AdminViews.student_lists_grade_section), name='student_lists'),
    path('get-subject-data/', admin_required(AdminViews.get_subject_data), name='get_subject_data'),
    path('update_subject', admin_required(AdminViews.update_subject), name='update_subject'),
    path('delete_subject/', admin_required(AdminViews.delete_subject), name='delete_subject'),
    path('get-teacher-data/', admin_required(AdminViews.get_teacher_data), name='get_teacher_data'),
    path('update-teacher/', admin_required(AdminViews.update_teacher), name='update_teacher'),
    path('delete-teacher/', admin_required(AdminViews.delete_teacher), name='delete_teacher'),
    path('add_teacher', admin_required(AdminViews.add_teacher), name="add_teacher"),
    path('add_teacher_save', admin_required(AdminViews.add_teacher_save), name="add_teacher_save"),
    path('get_sections/', admin_required(AdminViews.get_sections), name='get_sections'),
    path('search/', admin_required(AdminViews.search_students), name='search_students'),
    path('upload_documents/', admin_required(AdminViews.upload_documents_ocr), name='upload_documents'),
    path('save_edited_data/', admin_required(AdminViews.save_edited_data), name='save_edited_data'),
    path('sf10/', admin_required(AdminViews.sf10_views), name='sf10_view'),
    path('add_subject/', admin_required(AdminViews.add_subject), name='add_subject'),
    path('subject_list/', admin_required(AdminViews.subject_list), name='subject_list'),
    path('save/', admin_required( AdminViews.save_edited_data), name='save_edited_data'),
    path('announcement', admin_required(AdminViews.announcement), name="announcement"),
    path('create/', admin_required(AdminViews.create_announcement), name='create_announcement'),
    path('announcement/delete/<int:announcement_id>/', admin_required(AdminViews.delete_announcement), name='delete_announcement'),
    path('users/', admin_required(AdminViews.user_list), name='user_list'),
    path('user_activities', admin_required(AdminViews.user_activities), name='user_activities'),
    path('school-information/',admin_required(AdminViews.school_information_view), name='school_information'),
    path('sf10/edit_view/<int:id>/',admin_required(AdminViews.sf10_edit_view), name='sf10_edit_view'),
    path('sf10/edit/<int:id>/', admin_required(AdminViews.sf10_edit), name='sf10_edit'),
    path('sf10/delete/', admin_required(AdminViews.sf10_delete), name='sf10_delete'),
    path('download/<int:id>/', admin_required(AdminViews.download_processed_document), name='download_processed_document'),
    path('add/', admin_required(AdminViews.add_school_view), name='add_school'),
    path('edit/<int:school_id>/', admin_required(AdminViews.edit_school_view), name='edit_school'),
    path('delete/<int:school_id>/', admin_required(AdminViews.delete_school_view), name='delete_school'),    
    path('sf10/delete/', admin_required(AdminViews.sf10_delete), name='sf10_delete'),     
    path('batch_process_documents/', admin_required(AdminViews.batch_process_documents), name='batch_process_documents'),
    path('detect-and-convert-tables/', admin_required(AdminViews.detect_and_convert_tables), name='detect_and_convert_tables'),
    path('manage_master_teacher', admin_required(AdminViews.manage_master_teacher), name='manage_master_teacher'),
    path('assign_master', admin_required(AdminViews.assign_master), name='assign_master'),
    path('save_assignment/', admin_required(AdminViews.save_assignment), name='save_assignment'),
    path('add_master', admin_required(AdminViews.add_master), name='add_master'),    
    path('get-master-data/', admin_required(AdminViews.get_master_data), name='get_master_data'),
    path('update-master/', admin_required(AdminViews.update_master), name='update_master'),
    path('delete-master/', admin_required(AdminViews.delete_master), name='delete_master'),
    path('download-activities/', admin_required(AdminViews.download_activities), name='download_activities'),
    path('school-information/', admin_required(AdminViews.school_information_view), name='school_information'),
    path('sf10/edit_view/<int:id>/', admin_required(AdminViews.sf10_edit_view), name='sf10_edit_view'),
    path('sf10/edit/<int:id>/', admin_required(AdminViews.sf10_edit), name='sf10_edit'),
    path('sf10/delete/', admin_required(AdminViews.sf10_delete), name='sf10_delete'),
    path('download/<int:id>/', admin_required(AdminViews.download_processed_document), name='download_processed_document'),
    path('add/', admin_required(AdminViews.add_school_view), name='add_school'),
    path('edit/<int:school_id>/', admin_required(AdminViews.edit_school_view), name='edit_school'),
    path('delete/<int:school_id>/',  admin_required(AdminViews.delete_school_view), name='delete_school'),
    path('school-information/', admin_required(AdminViews.school_information_view), name='school_information'),
    path('sf10/edit_view/<int:id>/', admin_required(AdminViews.sf10_edit_view), name='sf10_edit_view'),
    path('sf10/edit/<int:id>/', admin_required(AdminViews.sf10_edit), name='sf10_edit'),
    path('sf10/delete/', admin_required(AdminViews.sf10_delete), name='sf10_delete'),
    path('download/<int:id>/', admin_required(AdminViews.download_processed_document), name='download_processed_document'),
    # path('add/', admin_required(AdminViews.AdminViews.add_school_view), name='add_school'),
    path('edit/<int:school_id>/', admin_required(AdminViews.edit_school_view), name='edit_school'),
    path('delete/<int:school_id>/',  admin_required(AdminViews.delete_school_view), name='delete_school'),
    path('remove_grade/', admin_required(AdminViews.remove_grade), name='remove_grade'),
    path('create/core_values/', admin_required(AdminViews.create_core_values), name='create_core_values'),
    path('display/', admin_required(AdminViews.display_core_values), name='display_core_values'),
    path('update/<int:core_values_id>/', admin_required(AdminViews.update_core_values), name='update_core_values'),
    path('delete_core_values/<int:core_values_id>/', admin_required(AdminViews.delete_core_values), name='delete_core_values'),
    path('create/behavior_statements/', admin_required(AdminViews.create_behavior_statements), name='create_behavior_statements'),
    path('display/behavior_statements/', admin_required(AdminViews.display_behavior_statements), name='display_behavior_statements'),
    path('update/behavior_statements/<int:behavior_statement_id>/', admin_required(AdminViews.update_behavior_statement), name='update_behavior_statement'),
    path('delete/behavior_statements/<int:behavior_statement_id>/', admin_required(AdminViews.delete_behavior_statement), name='delete_behavior_statement'),

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
    path('students_classrecord', teacher_required(TeacherViews.get_students_by_grade_and_section), name='students_classrecord'),
    path('calculate_grades', teacher_required(TeacherViews.calculate_grades), name='calculate_grades'),
    path('display_classrecord/', teacher_required(TeacherViews.display_classrecord), name='display_classrecord'),
    #  path('process_assessment_type/', TeacherViews.process_assessment_Type, name='process_assessment_type'),
    # path('get-assessment-type/<str:assessment_type_processed>/', TeacherViews.get_assessment_type, name='get_assessment_type'),
    path('get_sections/', teacher_required(TeacherViews.get_sections), name='get_sections'),
    path('display_students/', teacher_required(TeacherViews.display_students), name='display_students'),
    path('student_list_for_subject', teacher_required(TeacherViews.student_list_for_subject), name='student_list_for_subject'),
    path('student_list_for_advisory', teacher_required(TeacherViews.student_list_for_advisory), name='student_list_for_advisory'),
    path('advisory_quarterly_grades', teacher_required(TeacherViews.advisory_quarterly_grades), name='advisory_quarterly_grades'),
    path('advisory_final_all_subject', teacher_required(TeacherViews.advisory_final_all_subject), name='advisory_final_all_subject'),
    path('toggle_class_type/', teacher_required(TeacherViews.toggle_class_type), name='toggle_class_type'),
    path('display_advisory_data', teacher_required(TeacherViews.display_advisory_data), name='display_advisory_data'),
    path('display_student_transmuted_grades/', teacher_required(TeacherViews.display_student_transmuted_grades), name='display_student_transmuted_grades'),

    path('class_record_upload', teacher_required(TeacherViews.class_record_upload), name='class_record_upload'),
    path('upload_sf2/', teacher_required(TeacherViews.sf2_upload), name='upload_sf2'),
    
    path('update_final_grade/', teacher_required(TeacherViews.update_final_grade), name='update_final_grade'),

    path('tempo_newupload', teacher_required(TeacherViews.tempo_newupload), name='tempo_newupload'),
    path('submit-json', teacher_required(TransferRecordViews.submit_json), name='submit_json'),
    path('inbox_open', teacher_required(TransferRecordViews.inbox_open), name='inbox_open'),
    path('transfer_quarterly_grade/<str:grade>/<str:section>/<str:subject>/<int:class_record_id>/', teacher_required(TransferRecordViews.transfer_quarterly_grade), name='transfer_quarterly_grade'),
    path('transfer-json',  teacher_required(TransferRecordViews.transfer_json_to_teacher), name='transfer_json_to_teacher'),
    path('accept_message', teacher_required(TransferRecordViews.accept_message), name='accept_message'),
    path('reject_message', teacher_required(TransferRecordViews.reject_message), name='reject_message'),
    path('final_grade_details', teacher_required(TransferRecordViews.final_grade_details), name='final_grade_details'),
    
    path('transfer_details', teacher_required(TransferRecordViews.transfer_details), name='transfer_details'),
    path('transfer_record', teacher_required(TransferRecordViews.transfer_record), name='transfer_record'),
    # path('transfer_class_record/<int:class_record_id>/', teacher_required(TransferRecordViews.transfer_class_record), name='transfer_class_record'),
    path('get_teacher_list/', teacher_required(TransferRecordViews.get_teacher_list), name='get_teacher_list'),


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
    # path('students', TeacherViews.get_students_by_grade_and_section, name='students'),
    path('calculate_grades', teacher_required(TeacherViews.calculate_grades), name='calculate_grades'),
    path('get_sections/', teacher_required(TeacherViews.get_sections), name='get_sections'),
    path('display_classrecord/<int:class_record_id>/', teacher_required(TeacherViews.display_classrecord), name='display_classrecord'),
    path('display_students', teacher_required(TeacherViews.display_students), name='display_students'),
    path('delete_class/<str:grade>/<str:section>/',teacher_required(TeacherViews.delete_class), name='delete_class'),
    path('delete_class_subject/<str:grade>/<str:section>/',teacher_required(TeacherViews.delete_class_subject), name='delete_class_subject'),
    path('view_classrecord', teacher_required(TeacherViews.view_classrecord), name='view_classrecord'),
    path('edit_record/<int:record_id>/', teacher_required(TeacherViews.edit_record), name='edit_record'),
    path('display_quarterly_summary/<str:grade>/<str:section>/<str:subject>/<int:class_record_id>/', teacher_required(TeacherViews.display_quarterly_summary), name='display_quarterly_summary'),
    path('display_final_grades/<str:grade>/<str:section>/<str:subject>/', teacher_required(TeacherViews.display_final_grades), name='display_final_grades'),
    path('update_score/', teacher_required(TeacherViews.update_score), name='update_score'),
    path('update_highest_possible_scores/', teacher_required(TeacherViews.update_highest_possible_scores), name='update_highest_possible_scores'),
    path('class_records/<int:class_record_id>/delete/', teacher_required(TeacherViews.delete_classrecord), name='delete_classrecord'),
    path('class_records/', teacher_required(TeacherViews.class_records_list), name='class_records_list'),
    path('grade_summary/<str:grade>/<str:section>/<str:quarter>/', teacher_required(TeacherViews.grade_summary), name='grade_summary'),
    path('all_final_grades/<str:grade>/<str:section>/', teacher_required(TeacherViews.display_all_final_grades), name='all_final_grades'),
    path('update_total_max_quarterly/', teacher_required(TeacherViews.update_total_max_quarterly), name='update_total_max_quarterly'),
    path('validate_score/', teacher_required(TeacherViews.validate_score), name='validate_score'),
    path('sf9/', teacher_required(TeacherViews.sf9), name='sf9'),
    path('get_sections_classrecord/', teacher_required(TeacherViews.get_sections_classrecord), name='get_sections_classrecord'),
     path('create-attendance/', teacher_required(TeacherViews.create_attendance_view), name='create_attendance_view'),
    path('save_attendance_record/', teacher_required(TeacherViews.save_attendance_record), name='save_attendance_record'),
      path('attendance-records/<str:grade>/<str:section>/', teacher_required(TeacherViews.attendance_record_view), name='attendance_records'),
       path('update-attendance-record/', teacher_required(TeacherViews.update_attendance_record), name='update_attendance_record'),
      path('delete-month/', teacher_required(TeacherViews.delete_month), name='delete_month'),
     path('teacher_upload_documents/', teacher_required(TeacherViews.teacher_upload_documents_ocr), name='teacher_upload_documents'),
         path('teacher_sf10_views/', teacher_required(TeacherViews.teacher_sf10_views), name='teacher_sf10_views'),
     path('teacher_batch_process_documents/', teacher_required(TeacherViews.teacher_batch_process_documents), name='teacher_batch_process_documents'),
    path('teacher_sf10_edit_view/<int:id>/', teacher_required(TeacherViews.teacher_sf10_edit_view), name='teacher_sf10_edit_view'),
    path('teacher_sf10/edit/<int:id>/', teacher_required(TeacherViews.teacher_sf10_edit), name='teacher_sf10_edit'),
    # path('create_learners_observation/<str:grade>/<str:section>/', TeacherViews.create_learners_observation, name='create_learners_observation'),
    path('students_behavior/<str:grade>/<str:section>/', teacher_required(TeacherViews.students_behavior_view), name='students_behavior'),
    path('save-observations/', teacher_required(TeacherViews.save_observations), name='save_observations'),
    path('display-observation/<str:grade>/<str:section>/', teacher_required(TeacherViews.display_learners_observation), name='display_learners_observation'),
    path('update-markings/', teacher_required(TeacherViews.update_markings), name='update_markings'),
    path('grades/<str:grade>/<str:section>/delete_subject/<str:subject>/', teacher_required(TeacherViews.delete_grade_data_subject), name='delete_grade_data_subject'),

   # urls.py
    # Generation

    path('generate_excel_for_grades/<str:grade>/<str:section>/<str:subject>/<str:quarter>/', teacher_required(GenerationViews.generate_excel_for_grades), 
         name='generate_excel_for_grades'),
    path('generate-excel-sf9/<int:student_id>/', teacher_required(GenerationViews.generate_excel_for_sf9), name='generate_excel_for_sf9'),
    path('generate-per-subject/', teacher_required(GenerationViews.generate_per_subject_view), name='generate_per_subject'),
    path('generate_grade_section_list/', teacher_required(GenerationViews.generate_grade_section_list), name='generate_grade_section_list'),
    path('generate-per-all-subject/', teacher_required(GenerationViews.generate_per_all_subject_view), name='generate_per_all_subject'),
    path('generate-excel/<str:grade>/<str:section>/<str:quarter>/', teacher_required(GenerationViews.generate_excel_for_all_subjects), name='generate_excel_for_all_subjects'),
    path('generate_summary_of_quarterly_grades/<str:grade>/<str:section>/<str:quarter>/', teacher_required(GenerationViews.generate_summary_of_quarterly_grades), name='generate_summary_of_quarterly_grades'),

    path('generate_final_and_general_grades/<str:grade>/<str:section>/', teacher_required(GenerationViews.generate_final_and_general_grades), name='generate_final_and_general_grades'),
    path('generate-summary-for-grades-4-to-6/<str:grade>/<str:section>/<str:subject>/<str:quarter>/', teacher_required(GenerationViews.generate_summary_for_grades_4_to_6), name='generate_summary_for_grades_4_to_6'),
    path('generate-final-grade/', teacher_required(GenerationViews.generate_final_grade_view), name='generate_final_grade'),



    #Archived
    path('archived-records/', teacher_required(ArchivedViews.archived_records), name='archived_records'),
    path('display_archived_classrecord/<int:class_record_id>/', admin_required(ArchivedViews.display_archived_classrecord), name='display_archived_classrecord'),
    path('restore-archived-record/<int:archived_record_id>/', admin_required(ArchivedViews.restore_archived_record), name='restore_archived_record'),
    path('archive-class-record/<int:class_record_id>/', teacher_required(ArchivedViews.archive_class_record), name='archive_class_record'),
    path('archive_students_with_grade_and_section/<str:grade>/<str:section>/', teacher_required(ArchivedViews.archive_students_with_grade_and_section), name='archive_students_with_grade_and_section'),
    path('restore_archived_students/<str:grade>/<str:section>/', teacher_required(ArchivedViews.restore_archived_students), name='restore_archived_students'),
    path('admin_archived-records/', admin_required(ArchivedViews.admin_archived_records), name='admin_archived_records'),
    # path('confirm_restore/<int:archived_record_id>/', ArchivedViews.confirm_restore, name='confirm_restore'),
    # path('view_restore_request/<int:request_id>/', ArchivedViews.view_restore_request, name='view_restore_request'),
    # path('approve_restore_request/<int:request_id>/', ArchivedViews.approve_restore_request, name='approve_restore_request'),
    # path('deny_restore_request/<int:request_id>/', ArchivedViews.deny_restore_request, name='deny_restore_request'),
    # path('restore-requests/', ArchivedViews.restore_requests, name='restore_requests'), 
    # path('initiate-restore/<int:archived_record_id>/', ArchivedViews.initiate_restore_request, name='initiate_restore_request'),


    # superadmin
    path('home_superadmin', super_required(SuperAdminViews.home_superadmin), name='home_superadmin'),
    path('manage_admin', super_required(SuperAdminViews.manage_admin), name='manage_admin'),
    path('super_manage_master_teacher', super_required(SuperAdminViews.super_manage_master_teacher), name='super_manage_master_teacher'),
    path('manage_teacher', super_required(SuperAdminViews.manage_teacher), name='manage_teacher'),
    path('add_admin', super_required(SuperAdminViews.add_admin), name='add_admin'),    
    path('get-admin-data/', super_required(SuperAdminViews.get_admin_data), name='get_admin_data'),
    path('update-admin/', super_required(SuperAdminViews.update_admin), name='update_admin'),
    path('delete-admin/', super_required(SuperAdminViews.delete_admin), name='delete_admin'),
    path('home_superadmin', super_required(SuperAdminViews.home_superadmin), name='home_superadmin'),
    path('manage_admin', super_required(SuperAdminViews.manage_admin), name='manage_admin'),
    path('super_manage_master_teacher', super_required(SuperAdminViews.super_manage_master_teacher), name='super_manage_master_teacher'),
    path('manage_teacher', super_required(SuperAdminViews.manage_teacher), name='manage_teacher'),
    path('add_admin', super_required(SuperAdminViews.add_admin), name='add_admin'),    
    path('get-admin-data/', super_required(SuperAdminViews.get_admin_data), name='get_admin_data'),
    path('update-admin/', super_required(SuperAdminViews.update_admin), name='update_admin'),
    path('delete-admin/', super_required(SuperAdminViews.delete_admin), name='delete_admin'),
    path('backup/', super_required(SuperAdminViews.backup_database), name='backup_database'),

   
# transfer record Views
    path('submit-json', teacher_required(TransferRecordViews.submit_json), name='submit_json'),
    path('inbox_open', teacher_required(TransferRecordViews.inbox_open), name='inbox_open'),
    path('inbox_count', teacher_required(TransferRecordViews.inbox_count), name='inbox_count'),
    path('inbox_count', teacher_required(TransferRecordViews.inbox_count), name='inbox_count'),
    path('transfer_quarterly_grade/<str:grade>/<str:section>/<str:subject>/<int:class_record_id>/', teacher_required(TransferRecordViews.transfer_quarterly_grade), name='transfer_quarterly_grade'),
    path('transfer-json',  teacher_required(TransferRecordViews.transfer_json_to_teacher), name='transfer_json_to_teacher'),
    path('accept_message', teacher_required(TransferRecordViews.accept_message), name='accept_message'),
    path('reject-btn_message', teacher_required(TransferRecordViews.reject_message), name='reject_message'),
    path('final_grade_details', teacher_required(TransferRecordViews.final_grade_details), name='final_grade_details'),
    

        
    path('transfer_details', teacher_required(TransferRecordViews.transfer_details), name='transfer_details'),
    path('transfer_record', teacher_required(TransferRecordViews.transfer_record), name='transfer_record'),
    # path('transfer_class_record/<int:class_record_id>/', teacher_required(TransferRecordViews.transfer_class_record), name='transfer_class_record'),
    path('get_teacher_list/', teacher_required(TransferRecordViews.get_teacher_list), name='get_teacher_list'),

    # master teacher
    path('home_mt', mt_required(MasterTeacherViews.home_mt), name='home_mt'),
    path('advisory_classes_mt', mt_required(MasterTeacherViews.advisory_classes_mt), name='advisory_classes_mt'),
    path('subject_classes_mt', mt_required(MasterTeacherViews.subject_classes_mt), name='subject_classes_mt'),
    path('distinct_sections', mt_required(MasterTeacherViews.distinct_sections), name='distinct_sections'),
    path('subject_quarters', mt_required(MasterTeacherViews.subject_quarters), name='subject_quarters'),
    path('subject_subjects', mt_required(MasterTeacherViews.subject_subjects), name='subject_subjects'),
    path('home_mt', mt_required(MasterTeacherViews.home_mt), name='home_mt'),
    path('advisory_classes_mt', mt_required(MasterTeacherViews.advisory_classes_mt), name='advisory_classes_mt'),
    path('subject_classes_mt', mt_required(MasterTeacherViews.subject_classes_mt), name='subject_classes_mt'),
    path('distinct_sections', mt_required(MasterTeacherViews.distinct_sections), name='distinct_sections'),
    path('subject_quarters', mt_required(MasterTeacherViews.subject_quarters), name='subject_quarters'),
    path('subject_subjects', mt_required(MasterTeacherViews.subject_subjects), name='subject_subjects'),
    path('summary_per_quarter', mt_required(MasterTeacherViews.summary_per_quarter), name='summary_per_quarter'),
    path('advisory_sections', mt_required(MasterTeacherViews.advisory_sections), name='advisory_sections'),
    path('advisory_summary', mt_required(MasterTeacherViews.advisory_summary), name='advisory_summary'),

    path('chart-data/', StudentChartDataView.as_view(), name='chart_data'),
]



 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)