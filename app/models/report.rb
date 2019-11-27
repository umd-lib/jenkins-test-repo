# frozen_string_literal: true

# A basic generic report to be run
class Report < ApplicationRecord
  belongs_to :user, optional: true
  alias_attribute :creator, :user
  serialize :parameters

  # Provides a short human-readable description for this record, for GUI prompts
  alias_attribute :description, :name

  enum status: {
    pending: 0,
    running: 1,
    error: 2,
    completed: 3
  }

  enum format: {
    xlsx: 0,
    pdf: 1
  }

  %i[format status name].each { |f| validates f, presence: true }

  # sugary method to get the report manager
  def manager
    Manager
  end

  def self.policy_class
    ReportPolicy
  end

  # registers the available reports
  class Manager
    class << self
      # Add the report to our list of registered reports...
      def register_report(klass)
        @reports ||= []
        @reports.unshift(klass) if klass.include?(Reportable) # last in, first up
      end

      def allowed_parameters
        @reports.map(&:allowed_parameters).flatten
      end

      # really just a sanity check for Rails autoloading
      def load_reports!
        Dir[Rails.root.join('app', 'models', 'reports', '*_report.rb')].each { |f| require_dependency f }
      end

      def reports
        load_reports! if @reports.blank?
        @reports.map { |r| r.name.underscore }
      end

      # we go through our registered reports and see if we can get and
      # instance.. to get and instance of TheCoolReport you pass the_cool_report
      def report_for(report, *args)
        load_reports! if @reports.blank?
        @reports.each do |klass|
          return klass.new(*args) if report == klass.name.underscore
        end
      end
    end
  end
end
