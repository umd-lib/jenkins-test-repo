# frozen_string_literal: true

# A Labor and Assistance staffing request
class LaborRequest < Request
  VALID_EMPLOYEE_TYPES = ['Contingent 1', 'Faculty Hourly', 'Student'].freeze
  VALID_REQUEST_TYPES = %w[New Renewal].freeze

  class << self
    def human_name
      'Labor and Assistance Requests'
    end

    # all the fields associated to the model
    def fields
      %i[ position_title employee_type request_type contractor_name
          number_of_positions hourly_rate hours_per_week number_of_weeks annual_cost
          nonop_funds nonop_source justification organization__name unit__name
          review_status__name review_comment user__name created_at updated_at ]
    end

    # Returns an ordered array used in the index pages
    def index_fields
      fields - %i[nonop_source justification review_comment created_at updated_at]
    end
  end

  monetize :hourly_rate_cents

  validates :contractor_name, presence: true, if: :contractor_name_required?

  validates :number_of_positions, presence: true, numericality: true
  validates :hours_per_week, presence: true, numericality: true
  validates :number_of_weeks, presence: true, numericality: true

  # Returns the annual cost
  def annual_cost
    (number_of_positions * hourly_rate * hours_per_week * number_of_weeks)
  end

  def contractor_name_required?
    request_type == 'Renewal'
  end

  default_scope { joins("LEFT JOIN organizations as units ON units.id = #{table_name}.unit_id") }
  default_scope { includes(%i[review_status organization user]) }
  default_scope { where(request_model_type: LaborRequest.request_model_types['labor']) }
end
