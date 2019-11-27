# frozen_string_literal: true

# The Cutoff date tied to a organization type
# A bit of AR trickery here. The primary_key for this model
# is the organization_type, which we are reusing the enum from the
# organization model. This allows us to have one cutoff for each type
# and allows us to get that assocation with AR's finders.
class OrganizationCutoff < ApplicationRecord
  include Cutoffable

  def id
    OrganizationCutoff.organization_types[organization_type]
  end

  self.primary_key = :organization_type

  has_many :organizations, foreign_key: :organization_type, primary_key: :organization_type,
                           inverse_of: :organization_cutoff, dependent: :restrict_with_exception

  def humanize
    cutoff_date.strftime('%F')
  end
end
