# frozen_string_literal: true

# Admins can record review status of a request
class Link < ApplicationRecord
  class << self
    def policy_class
      AdminOnlyPolicy
    end
  end

  validates :url, format: {
    message: 'please use a valid http/https URL',
    with: URI.regexp(%w[http https])
  }
  validates :url, presence: true
  validates :text, presence: true
end
