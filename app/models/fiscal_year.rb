# frozen_string_literal: true

# this is a convience class to format the fiscal year
class FiscalYear
  class << self
    def current_year
      Time.zone.today.financial_year
    end

    def next_year
      current_year + 1
    end

    def previous_year
      current_year - 1
    end

    def to_fy(year)
      year.to_s.gsub(/^\d\d/, 'FY')
    end

    def current
      to_fy(current_year)
    end

    def previous
      to_fy(previous_year)
    end

    def next
      to_fy(next_year)
    end
  end
end
