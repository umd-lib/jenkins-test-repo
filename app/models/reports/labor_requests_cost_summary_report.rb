# frozen_string_literal: true

require 'reportable'
# A summary report for the costs of Labor and Assistance requests
class LaborRequestsCostSummaryReport
  include Reportable

  attr_reader :error_message

  class << self
    # @return [String] human-readable description of the report, displayed in
    #   the GUI.
    def description
      'A summary report for the costs of Labor and Assistance requests, by division'
    end

    # @return [Array<String, Symbol>] the output formats this report is
    #   available in.
    def formats
      %w[xlsx]
    end

    # @return [String] the view template to use in formatting the report output
    def template
      'shared/labor_requests_cost_summary'
    end
  end

  def parameters_valid?
    valid = parameters&.key?(:review_status_ids)
    return true if valid

    @error_message = 'At least one review status must be specified!'
    false
  end

  # @return [Object] the data used by the template
  def query # rubocop:disable Metrics/AbcSize, Metrics/MethodLength
    # Stores annual cost totals, keyed by [department_code, emp_type_code]
    annual_cost_totals = Hash.new(0)

    # Stores nonop_fund totals, keyed by division_code
    other_support_totals = Hash.new(0)

    allowed_review_status_ids = parameters[:review_status_ids]
    allowed_review_statuses = allowed_review_status_ids.map { |id| ReviewStatus.find(id) }

    LaborRequest.includes(:organization, :review_status).find_each do |request|
      review_status = request.review_status
      next unless allowed_review_statuses.include?(review_status)

      employee_type = request.employee_type
      department_code = request.organization.code
      key = [department_code, employee_type]
      annual_cost = request.annual_cost
      nonop_funds = request.nonop_funds
      annual_cost_totals[key] += annual_cost unless annual_cost.nil?
      other_support_key = [department_code, 'other_support']
      other_support_totals[other_support_key] += nonop_funds unless nonop_funds.nil?
    end

    # Stores in an array (to preserve the department ordering), a "value" Hash
    # representing that department's row in the table.
    summary_data = []
    Organization.department.order(:code).each do |dept|
      department_code = dept.code
      division_code = dept.parent.code
      c1_key = [department_code, 'Contingent 1']
      hourly_faculty_key = [department_code, 'Faculty Hourly']
      students_key = [department_code, 'Student']
      other_support_key = [department_code, 'other_support']
      value = { department: dept.name,
                division: division_code,
                c1: annual_cost_totals[c1_key],
                hourly_faculty: annual_cost_totals[hourly_faculty_key],
                students: annual_cost_totals[students_key],
                other_support: other_support_totals[other_support_key] }
      summary_data << value
    end

    divisions = Organization.division
    # A bit confusing...in this context:
    # current_fiscal_year = The year currently taking requests (ie next FY)
    # previous_fiscal_year = The previous year that took requests (ie last FY)
    current_fiscal_year = FiscalYear.next
    previous_fiscal_year = FiscalYear.current

    { summary_data: summary_data, divisions: divisions,
      current_fiscal_year: current_fiscal_year,
      previous_fiscal_year: previous_fiscal_year,
      allowed_review_statuses: allowed_review_statuses }
  end
end
