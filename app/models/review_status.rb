# frozen_string_literal: true

# Admins can record review status of a request
class ReviewStatus < ApplicationRecord
  validates :name, presence: true
  validates :code, presence: true, uniqueness: { case_sensitive: false }

  has_many :requests, dependent: :restrict_with_error
  has_many :archived_requests, dependent: :restrict_with_exception
  # Provides a short human-readable description for this record, for GUI prompts
  alias_attribute :description, :name

  def self.policy_class
    AdminOnlyPolicy
  end
end
