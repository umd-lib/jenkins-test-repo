# frozen_string_literal: true

require 'test_helper'

# Tests Requests By Department report
class RequestsByDepartmentReportTest < ActiveSupport::TestCase
  def setup
    @report = RequestsByDepartmentReport.new

    # The department to use for the report
    organization_id = Organization.department.first
    @report.parameters = { organization_id: organization_id }
  end

  test 'should give a description of itself' do
    assert_not @report.class.description.empty?
  end

  test 'should return an enumerable-like / iterable object with a query' do
    assert @report.query.respond_to? :each
  end
end
