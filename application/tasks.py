from celery import shared_task
from application.models import Applications, EligibilityConfig, StatusUpdate


from datetime import datetime

from django.contrib.auth import get_user_model

from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.management import call_command
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task
def check_eligibility(application_id):
    application = Applications.objects.get(id=application_id)
    eligibility_constraints = EligibilityConfig.objects.first()

    # CONSTANTS
    CONST_VOTERS_ISSUED_AT = "TAGUIG, NATIONAL CAPITAL REGION - FOURTH DISTRICT"
    subject_email = "Scholarship Application Eligibility"
    message_template = "Scholarship Application's Eligibility Status"

    # Utilities
    deficiency = []
    eligibility_status = None

    existing_status_updates = StatusUpdate.objects.filter(application_reference_id=application.application_reference_id, is_active=True)
    existing_status_updates.update(is_active=False)

    StatusUpdate.objects.create(
        application = application,
        application_reference_id = application.application_reference_id,
        description = "Your scholarship application is now undergoing our automated eligibility system.",
        current_step = 2,
        is_active = True
    )

    def check_semester(semester_applied, semester):
        return semester_applied == semester

    def get_date_year(issuance_date):
        """
        Returns the year value from a string (e.g: 10/25/23, it shall return 2023)
        """
        int_year = int(issuance_date[-4:])
        return int_year

    def get_numeric_residency_years(years_of_residency):
        """
        Extract numeric value from the years_of_residency field
        """
        numeric_value = ''.join(c for c in years_of_residency if c.isdigit())
        return int(numeric_value) if numeric_value else None

    def check_residency(years_of_residency, minimum_residency):
        """
        Compare the years of residency from the minimum years of residency according to the defined eligibility constraints
        """
        return years_of_residency >= minimum_residency

    def check_voters_certificate(issuance_date_year, validity_start, validity_end, voters_issued_at):
        """
        Compare the variables found and derived from the submitted voter's certificate to the defined eligibility constraints
        """
        return (
            issuance_date_year >= validity_start and
            issuance_date_year <= validity_end and
            voters_issued_at == CONST_VOTERS_ISSUED_AT
        )

    def process_deficiency(deficiency_list, message):
            if message:
                deficiency_list.append(message)
    
    # Set local variables
    applicant_numeric_years_of_residency = get_numeric_residency_years(application.years_of_residency)
    applicant_voters_issuance_date_year = get_date_year(application.voters_issuance_date)

    guardians_numeric_years_of_residency = get_numeric_residency_years(application.guardians_years_of_residency)
    guardians_voters_issuance_date_year = get_date_year(application.guardians_voters_issuance_date)

    # APPLICANT SIDE
    if not check_semester(application.semester, eligibility_constraints.semester):
        process_deficiency(deficiency, "The applicant applied for the WRONG SEMESTER. Please double check your inputs before submitting them.")
    if not check_residency(applicant_numeric_years_of_residency, eligibility_constraints.minimum_residency):
        process_deficiency(deficiency, "The applicant's YEARS OF RESIDENCY according to your VOTER'S CERTIFICATE is found LESS than the requirements defined by the local municipality's scholarship program.")
    if not check_voters_certificate(applicant_voters_issuance_date_year, 
                                    eligibility_constraints.voters_validity_year_start, 
                                    eligibility_constraints.voters_validity_year_end, 
                                    application.voters_issued_at):
        process_deficiency(deficiency, f"There are certain deficiencies found in your VOTER'S CERTIFICATE, it's either: \n\t(1) Your voter's issuance date does not meet the current year criteria ({eligibility_constraints.voters_validity_year_start}-{eligibility_constraints.voters_validity_year_end}) of acceptance. Please re-validate your voter's registry at ABC's City Hall.\n\t(2) The place where your voter's certificate was issued isn't the ABC City.")

    # GUARDIAN SIDE
    if not check_residency(guardians_numeric_years_of_residency, eligibility_constraints.minimum_residency):
        process_deficiency(deficiency, "The applicant's guardian's YEARS OF RESIDENCY according to his/her VOTER'S CERTIFICATE is found LESS than the requirements defined by the local municipality's scholarship program.")
    if not check_voters_certificate(guardians_voters_issuance_date_year, 
                                    eligibility_constraints.voters_validity_year_start, 
                                    eligibility_constraints.voters_validity_year_end, 
                                    application.voters_issued_at):
        process_deficiency(deficiency, f"There are certain deficiencies found in your guardian's VOTER'S CERTIFICATE, it's either:\n\t(1) Your guardian's voter's issuance date does not meet the current year criteria ({eligibility_constraints.voters_validity_year_start}-{eligibility_constraints.voters_validity_year_end}) of acceptance. Please re-validate your voter's registry at ABC's City Hall.\n\t(2) The place where your voter's certificate was issued isn't the ABC City.")

    if deficiency:
        eligibility_status = False
        print("Your application has been rejected. Reason(s): ")
        for reason in deficiency:
            print(reason)

        existing_status_updates = StatusUpdate.objects.filter(application_reference_id=application.application_reference_id, is_active=True)
        existing_status_updates.update(is_active=False)

        StatusUpdate.objects.create(
            application = application,
            application_reference_id = application.application_reference_id,
            description = "Your scholarship application failed to meet the requirements defined by the local municipality. Please try again in 3 days.",
            current_step = 3,
            is_active = True
        )

        context = {
            "message": message_template,
            "firstname": application.firstname,
            "lastname": application.lastname,
            "application_reference_id": application.application_reference_id,

            "deficiencies": deficiency
        }

        html_message = render_to_string("content/application_has_deficiencies.html", context=context)
        plain_message = strip_tags(html_message)

        message = EmailMultiAlternatives(
            subject = subject_email,
            body = plain_message,
            from_email = None,
            to = [application.email_address,]
        )

        message.attach_alternative(html_message, "text/html")
        message.send()

    if not deficiency:
        eligibility_status = True

        existing_status_updates = StatusUpdate.objects.filter(application_reference_id=application.application_reference_id, is_active=True)
        existing_status_updates.update(is_active=False)

        StatusUpdate.objects.create(
            application = application,
            application_reference_id = application.application_reference_id,
            description = "Your scholarship application has passed the requirements defined by the local municipality.",
            current_step = 3,
            is_active = True
        )

        context = {
            "message": message_template,
            "firstname": application.firstname,
            "lastname": application.lastname,
            "application_reference_id": application.application_reference_id
        }

        html_message = render_to_string("content/application_passed_eligibility.html", context=context)
        plain_message = strip_tags(html_message)

        message = EmailMultiAlternatives(
            subject = subject_email,
            body = plain_message,
            from_email = None,
            to = [application.email_address,]
        )

        message.attach_alternative(html_message, "text/html")
        message.send()

    application.is_eligible = eligibility_status
    application.save()


@shared_task
def clean_expired_instances():
    call_command('clean_expired_instances')