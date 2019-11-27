# frozen_string_literal: true

require 'test_helper'

# Tests for the "User" model
class FiscalYearTest < ActiveSupport::TestCase
  def format_fy(year)
    "FY#{year.to_s.match(/\d\d$/)}"
  end

  def setup
    @year = Time.zone.today.financial_year
  end

  test 'should return the correct values' do
    assert_equal FiscalYear.current_year, @year
    assert_equal FiscalYear.current, format_fy(@year)
    assert_equal FiscalYear.next_year, @year + 1
    assert_equal FiscalYear.next, format_fy(@year + 1)
    assert_equal FiscalYear.previous_year, @year - 1
    assert_equal FiscalYear.previous, format_fy(@year - 1)
  end
end
