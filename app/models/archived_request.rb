# frozen_string_literal: true

# A Request that has been moved to the archived table
# This is a generic classs used for certain functions. Most of the time,
# archived records will be cast as ArchivedLaborRequest and whatnot, which
# inherit from their source classes ( like LaborRequest ).
class ArchivedRequest < ApplicationRecord
  include Requestable

  def self.policy_class
    ArchivedRequestPolicy
  end

  belongs_to :review_status, counter_cache: true
  belongs_to :organization, required: true, counter_cache: true
  belongs_to :unit, class_name: 'Organization',
                    foreign_key: :unit_id, counter_cache: true,
                    inverse_of: :archived_unit_requests, optional: true
  belongs_to :user, optional: true

  def current_table_name
    self.class.current_table_name
  end

  default_scope(lambda do
    joins('LEFT JOIN organizations as units ON units.id = archived_requests.unit_id')
      .includes(%i[review_status organization user])
  end)
end
