from celery import shared_task
from application.models import Applications, EligibilityConfig

@shared_task
def check_eligibility(application_id):
    application = Applications.objects.get(id=application_id)
    eligibility_constraints = EligibilityConfig.objects.first()

    # Check eligibility based on constraints
    eligibility_status = (
        
        # Conditionals for eligibility constraint
        # Shall return a boolean value

        # application.years_of_residency >= eligibility_constraints.minimum_residency and
        # application.voters_issued_at >= 'TAGUIG - ' and
        # application.voters_issuance_date <= eligibility_constraints.voters_validity_year_end
    )

    application.is_eligible = eligibility_status
    application.save()