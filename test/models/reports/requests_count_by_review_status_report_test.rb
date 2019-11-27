# frozen_string_literal: true

require 'test_helper'

# Tests Requests Counts By Review Status report
class RequestsCountByReviewStatusReportTest < ActiveSupport::TestCase
  def setup
    @report = RequestsCountByReviewStatusReport.new
  end

  test 'should give a description of itself' do
    assert_not @report.class.description.empty?
  end

  test 'total number of records should equal total number of active requests' do
    query_result = @report.query

    expected_total_records = Request.count

    actual_total_records = 0
    query_result.each do |v|
      actual_total_records += v[:under_review]
      actual_total_records += v[:approved]
      actual_total_records += v[:not_approved]
      actual_total_records += v[:contingent]
    end

    assert_equal expected_total_records, actual_total_records
  end
end
