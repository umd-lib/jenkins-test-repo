# frozen_string_literal: true

require 'test_helper'

# Tests for the "Report" model
class ReportTest < ActiveSupport::TestCase
  def setup
    @report = reports(:report_completed)
  end

  test 'should be valid' do
    @report = reports(:report_completed)
    assert @report.valid?
  end

  test 'name, format, status should be present' do
    %i[name format status].each do |attr|
      r = @report.dup
      r.attributes = Hash[attr, nil]
      assert_not r.valid?
    end
  end

  test 'role type without associated records can be deleted' do
    r = Report.create(name: 'AwesomeReport', format: 'xlsx', status: 'completed')
    assert r.destroy
  end

  test "should return it's manager when asked" do
    @report = reports(:report_completed)
    assert_equal(@report.manager.to_s, 'Report::Manager')
  end

  test "should return it's policy when asked" do
    @report = reports(:report_completed)
    assert_equal(@report.class.policy_class.to_s, 'ReportPolicy')
  end

  test 'should not register the reports that are not Reportable' do
    # A class that should not register
    class ::CrazyReport; end
    @report = reports(:report_completed)
    @report.manager.register_report(CrazyReport)
    assert_not_includes(@report.manager.reports, 'crazy_report')
  end

  test 'should return an instance of a report when manager is asked' do
    # A class that should register
    class ::NotCrazyReport; include Reportable end
    @report = reports(:report_completed)
    @report.manager.register_report(NotCrazyReport)
    assert_includes(@report.manager.reports, 'not_crazy_report')
    not_crazy_report = @report.manager.report_for('not_crazy_report')
    assert_instance_of(NotCrazyReport, not_crazy_report)
  end
end
