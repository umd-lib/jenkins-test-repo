# frozen_string_literal: true

require 'test_helper'

# Tests Contractor Requests Cost Summary report
class ContractorRequestsCostSummaryReportTest < ActiveSupport::TestCase
  def setup
    @report = ContractorRequestsCostSummaryReport.new

    # Set review status ids to include in the report
    review_status_ids = ReviewStatus.all.map(&:id)
    @report.parameters = { review_status_ids: review_status_ids }
  end

  test 'should give a description of itself' do
    assert_not @report.class.description.empty?
  end

  test 'should return a Hash containing various pieces of data' do
    query_result = @report.query
    summary_data = query_result[:summary_data]
    divisions = query_result[:divisions]
    current_fiscal_year = query_result[:current_fiscal_year]
    previous_fiscal_year = query_result[:previous_fiscal_year]
    allowed_review_statuses = query_result[:allowed_review_statuses]

    assert summary_data.is_a?(Array)
    assert_equal Organization.division.count, divisions.count
    assert_equal FiscalYear.next, current_fiscal_year
    assert_equal FiscalYear.current, previous_fiscal_year
    assert_equal ReviewStatus.count, allowed_review_statuses.count

    # "data" should contain an entry for each department
    assert summary_data.count == Organization.department.count
  end

  test 'totals from database should match totals provided to spreadsheet' do
    query_result = @report.query
    summary_data = query_result[:summary_data]

    # Expected totals from directly accessing records in database
    records = ContractorRequest.all
    expected_annual_base_pay_total = Money.new(records.sum(:annual_base_pay_cents), 'USD')
    expected_other_support_total = Money.new(records.sum(:nonop_funds_cents), 'USD')

    # Actual totals from what was provided for the spreadsheet
    actual_annual_base_pay_total = Money.new(0, 'USD')
    actual_other_support_total = Money.new(0, 'USD')
    summary_data.each do |datum|
      actual_annual_base_pay_total += datum[:c2]
      actual_annual_base_pay_total += datum[:cfac]

      actual_other_support_total += datum[:other_support]
    end

    assert actual_annual_base_pay_total.cents.positive?
    assert actual_other_support_total.cents.positive?
    assert_equal expected_annual_base_pay_total, actual_annual_base_pay_total
    assert_equal expected_other_support_total, actual_other_support_total
  end

  test 'departmental totals from database should match departmental totals provided to spreadsheet' do
    query_result = @report.query
    summary_data = query_result[:summary_data]

    Organization.department.each do |dept|
      dept_entries = summary_data.select { |s| s[:department] == dept.name }
      assert_equal dept_entries.size, 1
      dept_data = dept_entries.first

      # Expected totals from directly accessing records in database
      records = ContractorRequest.where(organization: dept)
      expected_annual_base_pay_total = Money.new(records.sum(:annual_base_pay_cents), 'USD')
      expected_other_support_total = Money.new(records.sum(:nonop_funds_cents), 'USD')

      # Actual totals from what was provided for the spreadsheet
      actual_annual_base_pay_total = Money.new(0, 'USD')
      actual_annual_base_pay_total += dept_data[:c2] || Money.new(0, 'USD')
      actual_annual_base_pay_total += dept_data[:cfac] || Money.new(0, 'USD')

      actual_other_support_total = dept_data[:other_support] || Money.new(0, 'USD')

      assert_equal expected_annual_base_pay_total, actual_annual_base_pay_total
      assert_equal expected_other_support_total, actual_other_support_total
    end
  end
end
