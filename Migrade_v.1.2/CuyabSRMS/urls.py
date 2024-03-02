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
    path('assign_teacher', admin_required(AdminViews.assign_teacher), name="assign_teacher"),
    path('save_assignment/', admin_required(AdminViews.save_assignment), name='save_assignment'),
    path('search/', admin_required(AdminViews.search_students), name='search_students'),
    path('upload_documents/', admin_required(AdminViews.upload_documents_ocr), name='upload_documents'),
    path('save_edited_data/', admin_required(AdminViews.save_edited_data), name='save_edited_data'),
    path('sf10/', admin_required(AdminViews.sf10_views), name='sf10_view'),
    path('add_subject/', admin_required(AdminViews.add_subject), name='add_subject'),
    path('subject_list/', admin_required(AdminViews.subject_list), name='subject_list'),
    # path('edit/', AdminViews.edit_extracted_data, name='edit_extracted_data'),
    path('save/', admin_required( AdminViews.save_edited_data), name='save_edited_data'),
    path('announcement', admin_required(AdminViews.announcement), name="announcement"),
    path('create/', admin_required(AdminViews.create_announcement), name='create_announcement'),
    path('announcement/delete/<int:announcement_id>/', admin_required(AdminViews.delete_announcement), name='delete_announcement'),
    path('users/', admin_required(AdminViews.user_list), name='user_list'),
    path('user_activities', admin_required(AdminViews.user_activities), name='user_activities'),
    path('school-information/', AdminViews.school_information_view, name='school_information'),
    path('sf10/edit_view/<int:id>/',AdminViews.sf10_edit_view, name='sf10_edit_view'),
    path('sf10/edit/<int:id>/', AdminViews.sf10_edit, name='sf10_edit'),
    path('sf10/delete/', AdminViews.sf10_delete, name='sf10_delete'),
    path('download/<int:id>/', AdminViews.download_processed_document, name='download_processed_document'),
    path('school-information/', AdminViews.school_information_view, name='school_information'),
    path('add/', AdminViews.add_school_view, name='add_school'),
    path('edit/<int:school_id>/', AdminViews.edit_school_view, name='edit_school'),
    path('delete/<int:school_id>/', AdminViews.delete_school_view, name='delete_school'),
    path('sf10/edit_view/<int:id>/',AdminViews.sf10_edit_view, name='sf10_edit_view'),
    path('sf10/edit/<int:id>/', AdminViews.sf10_edit, name='sf10_edit'),
    path('sf10/delete/', AdminViews.sf10_delete, name='sf10_delete'),
    path('download/<int:id>/', AdminViews.download_processed_document, name='download_processed_document'),
    path('school-information/', AdminViews.school_information_view, name='school_information'),
    path('add/', AdminViews.add_school_view, name='add_school'),
    path('edit/<int:school_id>/', AdminViews.edit_school_view, name='edit_school'),
    path('delete/<int:school_id>/', AdminViews.delete_school_view, name='delete_school'),
    path('batch_process_documents/', AdminViews.batch_process_documents, name='batch_process_documents'),
    path('detect-and-convert-tables/', AdminViews.detect_and_convert_tables, name='detect_and_convert_tables'),



    path('school-information/', AdminViews.school_information_view, name='school_information'),
    path('sf10/edit_view/<int:id>/',AdminViews.sf10_edit_view, name='sf10_edit_view'),
    path('sf10/edit/<int:id>/', AdminViews.sf10_edit, name='sf10_edit'),
    path('sf10/delete/', AdminViews.sf10_delete, name='sf10_delete'),
    path('download/<int:id>/', AdminViews.download_processed_document, name='download_processed_document'),
    path('school-information/', AdminViews.school_information_view, name='school_information'),
    path('add/', AdminViews.add_school_view, name='add_school'),
    path('edit/<int:school_id>/', AdminViews.edit_school_view, name='edit_school'),
    path('delete/<int:school_id>/', AdminViews.delete_school_view, name='delete_school'),
    path('sf10/edit_view/<int:id>/',AdminViews.sf10_edit_view, name='sf10_edit_view'),
    path('sf10/edit/<int:id>/', AdminViews.sf10_edit, name='sf10_edit'),
    path('sf10/delete/', AdminViews.sf10_delete, name='sf10_delete'),
    path('download/<int:id>/', AdminViews.download_processed_document, name='download_processed_document'),
    path('school-information/', AdminViews.school_information_view, name='school_information'),
    path('add/', AdminViews.add_school_view, name='add_school'),
    path('edit/<int:school_id>/', AdminViews.edit_school_view, name='edit_school'),
    path('delete/<int:school_id>/', AdminViews.delete_school_view, name='delete_school'),
    path('batch_process_documents/', AdminViews.batch_process_documents, name='batch_process_documents'),
    path('detect-and-convert-tables/', AdminViews.detect_and_convert_tables, name='detect_and_convert_tables'),
    path('manage_master_teacher', AdminViews.manage_master_teacher, name='manage_master_teacher'),
    path('add_mt', AdminViews.add_mt, name='add_mt'),


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
    path('display_classrecord', teacher_required(TeacherViews.display_classrecord), name='display_classrecord'),
    path('get_sections/', teacher_required(TeacherViews.get_sections), name='get_sections'),
    path('display_students/', teacher_required(TeacherViews.display_students), name='display_students'),
    path('student_list_for_subject', teacher_required(TeacherViews.student_list_for_subject), name='student_list_for_subject'),
    path('student_list_for_advisory', teacher_required(TeacherViews.student_list_for_advisory), name='student_list_for_advisory'),
    path('toggle_class_type/', teacher_required(TeacherViews.toggle_class_type), name='toggle_class_type'),
    path('display_advisory_data', teacher_required(TeacherViews.display_advisory_data), name='display_advisory_data'),
    path('display_student_transmuted_grades/', teacher_required(TeacherViews.display_student_transmuted_grades), name='display_student_transmuted_grades'),

    path('class_record_upload', teacher_required(TeacherViews.class_record_upload), name='class_record_upload'),

    path('update_final_grade/', teacher_required(TeacherViews.update_final_grade), name='update_final_grade'),

    path('tempo_newupload', teacher_required(TeacherViews.tempo_newupload), name='tempo_newupload'),
    path('submit-json', teacher_required(TransferRecordViews.submit_json), name='submit_json'),
    path('inbox_open', teacher_required(TransferRecordViews.inbox_open), name='inbox_open'),
    path('transfer_quarterly_grade/<str:grade>/<str:section>/<str:subject>/<int:class_record_id>/', teacher_required(TransferRecordViews.transfer_quarterly_grade), name='transfer_quarterly_grade'),
    path('transfer-json',  teacher_required(TransferRecordViews.transfer_json_to_teacher), name='transfer_json_to_teacher'),
    path('accept_message', teacher_required(TransferRecordViews.accept_message), name='accept_message'),
    path('final_grade_details', teacher_required(TransferRecordViews.final_grade_details), name='final_grade_details'),
    

    path('inbox/', teacher_required(TransferRecordViews.inbox), name='inbox'),
    path('transfer_details', teacher_required(TransferRecordViews.transfer_details), name='transfer_details'),
    path('transfer_record', teacher_required(TransferRecordViews.transfer_record), name='transfer_record'),
    # path('transfer_class_record/<int:class_record_id>/', teacher_required(TransferRecordViews.transfer_class_record), name='transfer_class_record'),
    path('get_teacher_list/', teacher_required(TransferRecordViews.get_teacher_list), name='get_teacher_list'),

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
    # path('students', TeacherViews.get_students_by_grade_and_section, name='students'),
    path('calculate_grades', TeacherViews.calculate_grades, name='calculate_grades'),
    path('get_sections/', TeacherViews.get_sections, name='get_sections'),
    path('display_classrecord/<int:class_record_id>/', teacher_required(TeacherViews.display_classrecord), name='display_classrecord'),
    path('display_students', TeacherViews.display_students, name='display_students'),
    path('delete_class/<str:grade>/<str:section>/',TeacherViews.delete_class, name='delete_class'),
    path('delete_class_subject/<str:grade>/<str:section>/',TeacherViews.delete_class_subject, name='delete_class_subject'),
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
    path('sf9/', TeacherViews.sf9, name='sf9'),
    path('get_sections_classrecord/', TeacherViews.get_sections_classrecord, name='get_sections_classrecord'),

   
   # urls.py
    # Generation

    path('generate_excel_for_grades/<str:grade>/<str:section>/<str:subject>/<str:quarter>/', GenerationViews.generate_excel_for_grades, 
         name='generate_excel_for_grades'),
    path('generate-excel-sf9/<int:student_id>/', GenerationViews.generate_excel_for_sf9, name='generate_excel_for_sf9'),
    path('generate-per-subject/', GenerationViews.generate_per_subject_view, name='generate_per_subject'),
    path('generate_grade_section_list/', GenerationViews.generate_grade_section_list, name='generate_grade_section_list'),
    path('generate-per-all-subject/', GenerationViews.generate_per_all_subject_view, name='generate_per_all_subject'),
    path('generate-excel/<str:grade>/<str:section>/<str:quarter>/', GenerationViews.generate_excel_for_all_subjects, name='generate_excel_for_all_subjects'),
    path('generate_summary_of_quarterly_grades/<str:grade>/<str:section>/<str:quarter>/', GenerationViews.generate_summary_of_quarterly_grades, 
         name='generate_summary_of_quarterly_grades'),
    path('generate_final_and_general_grades/<str:grade>/<str:section>/', GenerationViews.generate_final_and_general_grades, name='generate_final_and_general_grades'),

    #Archived
    path('archived-records/', ArchivedViews.archived_records, name='archived_records'),
    path('restore-archived-record/<int:archived_record_id>/', ArchivedViews.restore_archived_record, name='restore_archived_record'),
    path('archive-class-record/<int:class_record_id>/', ArchivedViews.archive_class_record, name='archive_class_record'),
    path('archive_students_with_grade_and_section/<str:grade>/<str:section>/', ArchivedViews.archive_students_with_grade_and_section, name='archive_students_with_grade_and_section'),
    path('restore_archived_students/<str:grade>/<str:section>/', ArchivedViews.restore_archived_students, name='restore_archived_students'),



    # superadmin
    path('home_superadmin', SuperAdminViews.home_superadmin, name='home_superadmin'),
    path('manage_admin', SuperAdminViews.manage_admin, name='manage_admin'),
    path('super_manage_master_teacher', SuperAdminViews.super_manage_master_teacher, name='super_manage_master_teacher'),
    path('manage_teacher', SuperAdminViews.manage_teacher, name='manage_teacher'),
    path('add_admin', SuperAdminViews.add_admin, name='add_admin'),    
    path('get-admin-data/', SuperAdminViews.get_admin_data, name='get_admin_data'),
    path('update-admin/', SuperAdminViews.update_admin, name='update_admin'),
    path('delete-admin/', SuperAdminViews.delete_admin, name='delete_admin'),


    # master teacher
    path('home_mt', MasterTeacherViews.home_mt, name='home_mt'),
    path('add_master', MasterTeacherViews.add_master, name='add_master'),    
    path('get-master-data/', MasterTeacherViews.get_master_data, name='get_master_data'),
    path('update-master/', MasterTeacherViews.update_master, name='update_master'),
    path('delete-master/', MasterTeacherViews.delete_master, name='delete_master'),
    path('inbox_open_mt/', MasterTeacherViews.inbox_open_mt, name='inbox_open_mt'),
    path('accept_message_mt', MasterTeacherViews.accept_message_mt, name='accept_message_mt'),


    path('chart-data/', StudentChartDataView.as_view(), name='chart_data'),
]



 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)