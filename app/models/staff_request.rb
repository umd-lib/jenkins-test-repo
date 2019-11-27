# frozen_string_literal: true

# A Labor and Assistance staffing request
class StaffRequest < Request
  VALID_EMPLOYEE_TYPES = ['Exempt', 'Faculty', 'Graduate Assistant', 'Non-exempt'].freeze
  VALID_REQUEST_TYPES = ['Backfill', 'New', 'ConvertCont', 'Pay Adjustment - Other',
                         'Pay Adjustment - Reclass', 'Pay Adjustment - Stipend'].freeze

  class << self
    def human_name
      'Staff Requests'
    end

    # all the fields associated to the model
    def fields
      %i[ position_title employee_name employee_type request_type
          annual_base_pay
          nonop_funds nonop_source justification organization__name unit__name
          review_status__name review_comment user__name created_at updated_at ]
    end

    # Returns an ordered array used in the index pages
    def index_fields
      fields - %i[nonop_source justification review_comment created_at updated_at]
    end
  end

  monetize :annual_base_pay_cents
  validates :annual_base_pay, presence: true
  validates :employee_name, presence: true, if: :employee_name_required?

  def employee_name_required?
    request_type == 'Pay Adjustment'
  end

  default_scope { joins("LEFT JOIN organizations as units ON units.id = #{table_name}.unit_id") }
  default_scope { includes(%i[review_status organization user]) }
  default_scope { where(request_model_type: StaffRequest.request_model_types['staff']) }
end
