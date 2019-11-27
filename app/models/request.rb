# frozen_string_literal: true

# This is the base line model for Request that is used by all other
# request types
class Request < ApplicationRecord # rubocop:disable Metrics/ClassLength
  # This adds a bunch of class methods..
  include Requestable

  attr_accessor :archived_fiscal_year
  attr_accessor :archived_proxy
  attr_accessor :spawned
  def spawned?
    return false unless spawned

    truths = [true, 1, '1', 't', 'T', 'true', 'TRUE'].to_set
    truths.include?(spawned)
  end

  # sometimes in the app we take Archived class and cast it as a regular
  # non-archived record to display in a view.
  def archived_proxy?
    archived_proxy || false
  end

  enum request_model_type: { contractor: 0, labor: 1, staff: 2 }
  enum employee_type: { "Contingent 1": 0, "Faculty Hourly": 1, "Student": 3,
                        "Exempt": 4, "Faculty": 5, "Graduate Assistant": 6,
                        "Non-exempt": 7, "Contingent 2": 8, "Contract Faculty": 9,
                        "PTK Faculty": 10 }
  enum request_type: { ConvertC1: 0, ConvertCont: 1, New: 2, "Pay Adjustment": 3, "Backfill": 4,
                       "Renewal": 5, 'Pay Adjustment - Other': 6,
                       'Pay Adjustment - Reclass': 7, 'Pay Adjustment - Stipend': 8 }
  belongs_to :review_status, counter_cache: true
  belongs_to :organization, required: true, counter_cache: true
  belongs_to :unit, class_name: 'Organization',
                    foreign_key: :unit_id, counter_cache: true,
                    inverse_of: :unit_requests, optional: true

  has_one :division, class_name: 'Organization', through: :organization, source: :parent

  # Returns the base_pay (if Staff or Contractor) or annual_cost Labor, in
  # dollars
  def annual_cost_or_base_pay
    case request_model_type
    when 'staff', 'contractor'
      (annual_base_pay_cents / 100.0)
    when 'labor'
      (calculate_annual_cost_in_cents / 100.0)
    else
      logger.error("Unknown request model type: #{request_model_type}")
      0.00
    end
  end

  # Calculates the annual cost for Labor Requests, returning the results in
  # cents
  def calculate_annual_cost_in_cents
    (number_of_positions * hourly_rate_cents * hours_per_week.to_f * number_of_weeks)
  end

  belongs_to :user, optional: true

  validates :position_title, presence: true
  validates :employee_type, presence: true
  validates :request_type, presence: true

  validate :org_must_be_dept
  def org_must_be_dept
    return if organization && organization.organization_type == 'department'

    errors.add(:organization, 'Must have a department specified.')
  end

  validate :unit_must_be_in_dept
  def unit_must_be_in_dept
    return if unit.nil?
    return if unit.parent == organization

    errors.add(:unit, 'Unit must be in the department.')
  end

  validates :justification, presence: true
  validate :new_justifications_cant_be_long
  def new_justifications_cant_be_long
    return if self.class.name =~ /^Archive/
    return if justification && justification.split(/\s+/).length < 126

    errors.add(:justification, 'Must be 125 words or less')
  end

  alias_attribute :description, :position_title

  monetize :nonop_funds_cents, allow_nil: true

  after_initialize(lambda do
    return if has_attribute?(:review_status_id) && review_status_id

    self.review_status = ReviewStatus.find_by(code: 'UnderReview')
  end)

  # when spawning from archive, sometimes values need to be mapped. this is a
  # hook you can override.
  def self.from_archived(params)
    new(params)
  end

  # returns a list of valid values for employee types
  def valid_employee_types
    if archived_proxy?
      "Archived#{self.class}".constantize::VALID_EMPLOYEE_TYPES
    else
      self.class::VALID_EMPLOYEE_TYPES
    end
  end

  # method to call the fields expressed in .fields
  def call_field(field)
    field.to_s.split('__').inject(self) { |a, e| a&.send(e) }
  rescue NoMethodError
    ''
  end

  def cutoff?
    persisted? ? (organization&.cutoff?) : false
  end

  def source_class
    if self.class.name == 'Request'
      "#{request_model_type}_request".camelize.constantize
    else
      self.class.source_class
    end
  end

  # this casts the record as its source type
  def to_source_proxy
    return self unless self.class.name =~ /^Archive/

    attrs = attributes.slice(*source_class.attribute_names).merge(archived_proxy: true,
                                                                  archived_fiscal_year: fiscal_year)
    source_class.new(attrs)
  end

  def current_table_name
    self.class.current_table_name
  end
end
