import logging
import json
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from breathecode.admissions.admin import CohortAdmin, CohortUserAdmin, AcademyAdmin
from .models import Answer, UserProxy, CohortProxy, CohortUserProxy, Survey, Review, ReviewPlatform
from .actions import send_question, send_survey_group, create_user_graduation_reviews
from django.utils.html import format_html
from breathecode.utils import AdminExportCsvMixin
from breathecode.utils.admin import change_field

logger = logging.getLogger(__name__)


def send_bulk_survey(modeladmin, request, queryset):
    # mocking tools are poor to apply it
    from django.contrib import messages

    user = queryset.all()
    errors = {}

    for u in user:
        try:
            send_question(u)
        except Exception as e:
            error = str(e)

            if error in errors:
                errors[error] += 1
            else:
                errors[error] = 1

            logger.fatal(error)

    if errors:
        message = ' - '.join([f'{error} ({errors[error]})' for error in errors.keys()])
        messages.error(request, message=message)
    else:
        messages.success(request, message='Survey was successfully sent')


send_bulk_survey.short_description = 'Send General NPS Survey'


@admin.register(UserProxy)
class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    actions = [send_bulk_survey]


def send_bulk_cohort_user_survey(modeladmin, request, queryset):
    from django.contrib import messages

    cus = queryset.all()
    errors = {}

    for cu in cus:
        try:
            send_question(cu.user, cu.cohort)
        except Exception as e:
            error = str(e)

            if error in errors:
                errors[error] += 1
            else:
                errors[error] = 1

            logger.fatal(error)

    if errors:
        message = ' - '.join([f'{error} ({errors[error]})' for error in errors.keys()])
        messages.error(request, message=message)
    else:
        messages.success(request, message='Survey was successfully sent')


send_bulk_cohort_user_survey.short_description = 'Send General NPS Survey'


def generate_review_requests(modeladmin, request, queryset):
    cus = queryset.all()
    for cu in cus:
        if cu.educational_status != 'GRADUATED':
            messages.success(request, message='All selected students must have graduated')
            return False

    try:
        for cu in cus:
            create_user_graduation_reviews(cu.user, cu.cohort)
            messages.success(request, message='Review request were successfully generated')
    except Exception as e:
        messages.error(request, message=str(e))


generate_review_requests.short_description = 'Generate review requests'


@admin.register(CohortUserProxy)
class CohortUserAdmin(CohortUserAdmin):
    actions = [
        send_bulk_cohort_user_survey,
        generate_review_requests,
    ]


@admin.register(CohortProxy)
class CohortAdmin(CohortAdmin):
    list_display = ('id', 'slug', 'stage', 'name', 'kickoff_date', 'syllabus_version', 'schedule')


def add_academy_to_answer(modeladmin, request, queryset):

    for answer in queryset:
        try:
            answer.academy = answer.cohort.academy
        except:
            answer.academy = answer.academy
        else:
            pass
        answer.save()


add_academy_to_answer.short_description = 'Add academy to answer'


class AnswerTypeFilter(admin.SimpleListFilter):

    title = 'Answer Type'

    parameter_name = 'answer_type'

    def lookups(self, request, model_admin):

        return (
            ('academy', 'Academy'),
            ('cohort', 'Cohort'),
            ('mentor', 'Mentor'),
            ('session', 'Session'),
            ('event', 'Event'),
        )

    def queryset(self, request, queryset):

        if self.value() == 'mentor':
            return queryset.filter(event__isnull=True, mentorship_session__isnull=True, mentor__isnull=False)

        if self.value() == 'session':
            return queryset.filter(mentorship_session__isnull=False)

        if self.value() == 'event':
            return queryset.filter(event__isnull=False, mentorship_session__isnull=True)

        if self.value() == 'event':
            return queryset.filter(academy__isnull=True,
                                   cohort__isnull=True,
                                   event__isnull=True,
                                   mentorship_session__isnull=True,
                                   mentor__isnull=True)

        if self.value() == 'cohort':
            return queryset.filter(academy__isnull=False,
                                   cohort__isnull=False,
                                   event__isnull=True,
                                   mentorship_session__isnull=True,
                                   mentor__isnull=True)

        if self.value() == 'academy':
            return queryset.filter(academy__isnull=False,
                                   cohort__isnull=True,
                                   event__isnull=True,
                                   mentorship_session__isnull=True,
                                   mentor__isnull=True)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin, AdminExportCsvMixin):
    list_display = ('status', 'user', 'academy', 'cohort', 'mentor', 'score', 'opened_at', 'created_at',
                    'answer_url')
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'cohort__slug']
    list_filter = [AnswerTypeFilter, 'status', 'score', 'academy__slug', 'cohort__slug']
    actions = ['export_as_csv', add_academy_to_answer]
    raw_id_fields = ['user', 'cohort', 'mentor']

    def answer_url(self, obj):
        url = 'https://nps.breatheco.de/' + str(obj.id)
        return format_html(f"<a rel='noopener noreferrer' target='_blank' href='{url}'>open answer</a>")

    # def entity(self, object):
    #     return f"{object.entity_slug} (id:{str(object.entity_id)})"


def send_big_cohort_bulk_survey(modeladmin, request, queryset):
    logger.debug(f'send_big_cohort_bulk_survey called')

    # cohort_ids = queryset.values_list('id', flat=True)
    surveys = queryset.all()
    for s in surveys:
        logger.debug(f'Sending survey {s.id}')

        try:
            result = send_survey_group(survey=s)
        except Exception as e:
            s.status = 'FATAL'
            s.status_json = json.dumps({'errors': [str(e)]})
            logger.fatal(str(e))
    if s.status != 'SENT':
        messages.error(request, message='Some surveys have not been sent')
    s.save()

    logger.info(f'All surveys scheduled to send for cohorts')


send_big_cohort_bulk_survey.short_description = 'Send survey to all cohort students'


class SentFilter(admin.SimpleListFilter):

    title = 'Sent tag'

    parameter_name = 'is_sent'

    def lookups(self, request, model_admin):

        return (
            ('yes', 'Sent'),
            ('no', 'Not yet sent'),
        )

    def queryset(self, request, queryset):

        if self.value() == 'yes':
            return queryset.filter(sent_at__isnull=False)

        if self.value() == 'no':
            return queryset.filter(sent_at__isnull=True)


def fill_sent_at_with_created_at(modeladmin, request, queryset):

    for s in queryset:
        s.sent_at = s.created_at
        s.save()


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('cohort', 'status', 'duration', 'created_at', 'sent_at', 'survey_url')
    search_fields = ['cohort__slug', 'cohort__academy__slug', 'cohort__name', 'cohort__academy__name']
    list_filter = [SentFilter, 'status', 'cohort__academy__slug']
    raw_id_fields = ['cohort']
    actions = [send_big_cohort_bulk_survey, fill_sent_at_with_created_at] + change_field(
        ['PENDING', 'SENT', 'PARTIAL', 'FATAL'], name='status')

    def survey_url(self, obj):
        url = 'https://nps.breatheco.de/survey/' + str(obj.id)
        return format_html(f"<a rel='noopener noreferrer' target='_blank' href='{url}'>open survey</a>")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    search_fields = ['author__first_name', 'author__last_name', 'author__email', 'cohort__slug']
    list_display = ('id', 'current_status', 'author', 'cohort', 'nps_previous_rating', 'total_rating',
                    'platform')
    readonly_fields = ['nps_previous_rating']
    list_filter = ['status', 'cohort__academy__slug', 'platform']
    raw_id_fields = ['author', 'cohort']

    def current_status(self, obj):
        colors = {
            'DONE': 'bg-success',
            'IGNORE': '',
            'PENDING': 'bg-warning',
        }
        return format_html(f"<span class='badge {colors[obj.status]}'>{obj.status}</span>")


@admin.register(ReviewPlatform)
class ReviewPlatformAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name')
