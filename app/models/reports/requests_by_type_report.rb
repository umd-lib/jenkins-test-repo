# frozen_string_literal: true

require 'reportable'

# A basic report that just gets all the request types
class RequestsByTypeReport
  include Reportable

  class << self
    # @return [String] human-readable description of the report, displayed in
    #   the GUI.
    def description
      'A basic report that collects all requests by type'
    end

    # @return [Array<String, Symbol>] the output formats this report is
    #   available in.
    def formats
      %w[xlsx]
    end

    # @return [Array<String>] the worksheet names (for spreadsheet output)
    def worksheets
      %w[StaffRequest ContractorRequest LaborRequest]
    end

    # @return [String] the view template to use in formatting the report output
    def template
      'requests/index'
    end
  end

  # @return [Object] the data used by the template
  def query
    [StaffRequest.enum_for(:find_each), ContractorRequest.enum_for(:find_each), LaborRequest.enum_for(:find_each)]
  end
end
