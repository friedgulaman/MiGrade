from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from CuyabSRMS.models import CustomUser, Admin, Teacher, Student, Grade, Section
from .models import *

# Extend the UserAdmin for CustomUser
class UserModel(UserAdmin):
    list_display = ('username', 'first_name', 'middle_ini', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined', 'user_type')

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

# Admin class for SuperAdmin
@admin.register(SuperAdmin)
class SuperAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')


# Admin class for MT
@admin.register(MT)
class MTAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')


# Admin class for SchoolInformation
@admin.register(SchoolInformation)
class SchoolInformationAdmin(admin.ModelAdmin):
    list_display = ('region', 'division', 'school_id', 'school_name', 'district', 'school_year', 'principal_name')


# Admin class for ArchivedStudent
@admin.register(ArchivedStudent)
class ArchivedStudentAdmin(admin.ModelAdmin):
    list_display = ('archived_name', 'archived_lrn', 'archived_sex', 'archived_birthday', 'archived_teacher')

# Admin class for Quarters
@admin.register(Quarters)
class QuartersAdmin(admin.ModelAdmin):
    list_display = ('quarters',)

# Admin class for Subject
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)

# Admin class for ClassRecord
@admin.register(ClassRecord)
class ClassRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'section', 'subject', 'teacher', 'quarters', 'date_modified', 'school_year')

# Admin class for ArchivedClassRecord
@admin.register(ArchivedClassRecord)
class ArchivedClassRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'section', 'subject', 'teacher', 'quarters', 'date_archived', 'school_year')

# Admin class for GradeScores
@admin.register(GradeScores)
class GradeScoresAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_record', 'initial_grades', 'transmuted_grades', 'grade_scores')

# Admin class for ArchivedGradeScores
@admin.register(ArchivedGradeScores)
class ArchivedGradeScoresAdmin(admin.ModelAdmin):
    list_display = ('archived_class_record', 'student', 'initial_grades', 'transmuted_grades', 'grade_scores')

# Admin class for FinalGrade
@admin.register(FinalGrade)
class FinalGradeAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'student', 'grade', 'section', 'subject', 'final_grade')

# Admin class for ArchivedFinalGrade
@admin.register(ArchivedFinalGrade)
class ArchivedFinalGradeAdmin(admin.ModelAdmin):
    list_display = ('archived_teacher', 'archived_student', 'archived_grade', 'archived_section', 'archived_final_grade')

# Admin class for GeneralAverage
@admin.register(GeneralAverage)
class GeneralAverageAdmin(admin.ModelAdmin):
    list_display = ('student', 'grade', 'section', 'general_average', 'remarks', 'status')

# Admin class for QuarterlyGrades
@admin.register(QuarterlyGrades)
class QuarterlyGradesAdmin(admin.ModelAdmin):
    list_display = ('student', 'quarter', 'grades')

# Admin class for ArchivedGeneralAverage
@admin.register(ArchivedGeneralAverage)
class ArchivedGeneralAverageAdmin(admin.ModelAdmin):
    list_display = ('archived_student', 'archived_grade', 'archived_section', 'archived_general_average')

# Admin class for ArchivedQuarterlyGrades
@admin.register(ArchivedQuarterlyGrades)
class ArchivedQuarterlyGradesAdmin(admin.ModelAdmin):
    list_display = ('archived_student', 'archived_quarter', 'archived_grades')

# Admin class for ProcessedDocument
@admin.register(ProcessedDocument)
class ProcessedDocumentAdmin(admin.ModelAdmin):
    list_display = ('document', 'upload_date', 'teacher')

# Admin class for ExtractedData
@admin.register(ExtractedData)
class ExtractedDataAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'lrn', 'school_year', 'birthdate', 'classified_as_grade', 'general_average', 'sex', 'name_of_school')

# Admin class for ActivityLog
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'action', 'details')

# Admin class for InboxMessage
@admin.register(InboxMessage)
class InboxMessageAdmin(admin.ModelAdmin):
    list_display = ('to_teacher', 'from_teacher', 'file_name', 'json_data', 'date_received')

# Admin class for AcceptedMessage
@admin.register(AcceptedMessage)
class AcceptedMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'file_name', 'json_data', 'accepted_by', 'accepted_at')

# Admin class for AdvisoryClass
@admin.register(AdvisoryClass)
class AdvisoryClassAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'grade', 'section')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'timestamp')

# Admin class for AttendanceRecord
@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'attendance_record')

# Admin class for CoreValues
@admin.register(CoreValues)
class CoreValuesAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

# Admin class for BehaviorStatement
@admin.register(BehaviorStatement)
class BehaviorStatementAdmin(admin.ModelAdmin):
    list_display = ('core_value','statement')

# Admin class for LearnersObservation
@admin.register(LearnersObservation)
class LearnersObservationAdmin(admin.ModelAdmin):
    list_display = ('student', 'quarter_1', 'quarter_2', 'quarter_3', 'quarter_4')
