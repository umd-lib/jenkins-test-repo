# frozen_string_literal: true

require 'reportable'
# A summary report for the costs of Staff requests
class StaffRequestsCostSummaryReport
  include Reportable

  attr_reader :error_message

  class << self
    # @return [String] human-readable description of the report, displayed in
    #   the GUI.
    def description
      'A summary report for the costs of Staff requests, by division'
    end

    # @return [Array<String, Symbol>] the output formats this report is
    #   available in.
    def formats
      %w[xlsx]
    end

    # @return [String] the view template to use in formatting the report output
    def template
      'shared/staff_requests_cost_summary'
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
    # Stores annual base pay totals, keyed by [department_code, emp_type_code]
    annual_base_pay_totals = Hash.new(0)

    # Stores nonop_fund totals, keyed by division_code
    other_support_totals = Hash.new(0)

    allowed_review_status_ids = parameters[:review_status_ids]
    allowed_review_statuses = allowed_review_status_ids.map { |id| ReviewStatus.find(id) }

    StaffRequest.includes(:organization, :review_status).find_each do |request|
      review_status = request.review_status
      next unless allowed_review_statuses.include?(review_status)

      employee_type = request.employee_type
      department_code = request.organization.code
      key = [department_code, employee_type]
      annual_base_pay = request.annual_base_pay
      nonop_funds = request.nonop_funds
      annual_base_pay_totals[key] += annual_base_pay unless annual_base_pay.nil?
      other_support_key = [department_code, 'other_support']
      other_support_totals[other_support_key] += nonop_funds unless nonop_funds.nil?
    end

    # Stores in an array (to preserve the department ordering), a "value" Hash
    # representing that department's row in the table.
    summary_data = []
    Organization.department.order(:code).each do |dept|
      department_code = dept.code
      division_code = dept.parent.code
      ex_key = [department_code, 'Exempt']
      fac_key = [department_code, 'Faculty']
      ga_key = [department_code, 'Graduate Assistant']
      nex_key = [department_code, 'Non-exempt']
      other_support_key = [department_code, 'other_support']
      value = { department: dept.name,
                division: division_code,
                ex: annual_base_pay_totals[ex_key],
                fac: annual_base_pay_totals[fac_key],
                ga: annual_base_pay_totals[ga_key],
                nex: annual_base_pay_totals[nex_key],
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
