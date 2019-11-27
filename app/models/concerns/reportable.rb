# frozen_string_literal: true

# Generic for all report type objects.
#
# Including this in your report adds common functionality and registers it in
# the ReportManager
module Reportable
  extend ActiveSupport::Concern

  class << self
    def included(report)
      report.extend ClassMethods
      Report::Manager.register_report(report)
    end
  end

  # These are class methods that are extended
  module ClassMethods
    # @return [Array<Symbol>] the parameters allowed for user input
    def allowed_parameters
      %i[]
    end

    # @return [Array<String, Symbol>] the output formats this report is
    #   available in.
    def formats
      %w[xlsx]
    end

    # @return [String] human-readable description of the report, displayed in
    #   the GUI.
    def description
      'Text to be overridden in the Reportable subclass'
    end

    # @return [String] the view template to use in formatting the report output
    def template
      'requests/index'
    end
  end

  attr_accessor :parameters

  # @param parameters the parameters serialized in the master Report instance
  def initialize(parameters = nil)
    @parameters = parameters
  end

  # Override this method to define your query
  # @return [Object] the data used by the template
  def query; end

  # alias to .formats
  def formats
    self.class.formats
  end

  # alias to .description
  def description
    self.class.description
  end

  # alias to .template
  def template
    self.class.template
  end

  # @return [Boolean] true if the provided parameters are valid, false
  # otherwise. This default implementation always returns true.
  def parameters_valid?
    true
  end

  # @return [String,nil] a human-readable error message, or nil.
  #   Typically used in conjunction with the "parameters_valid?" method to
  #   describe why the parameters are invalid. This default implementation
  #   returns nil.
  def error_message
    nil
  end
end
