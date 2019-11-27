# frozen_string_literal: true

# The Organization the the request is associated to
class Organization < ApplicationRecord
  include Cutoffable
  include Resettable
  include Flattenable

  class << self
    def policy_class
      AdminOnlyPolicy
    end

    def root_org
      root.first
    end
  end

  belongs_to :parent, class_name: 'Organization', foreign_key: 'organization_id',
                      optional: true, inverse_of: :children
  validates :organization_id, presence: true, unless: :root?

  has_many :children, foreign_key: :organization_id, class_name: 'Organization', inverse_of: :parent,
                      dependent: :restrict_with_error
  # a more basic AR way of getting children
  has_many :organizations, dependent: :restrict_with_error

  # a weird one. Rubocop wants use to have a dependent, but we don't want one
  # actually. This is bc our has_one here is just some "association trickery",
  # because the forign_key is being set to the cutoff :organization_type. When
  # the org record is deleted, we shouldn't do anything to the Cutoff.
  # rubocop:disable Rails/HasManyOrHasOneDependent
  has_one :organization_cutoff, foreign_key: :organization_type, primary_key: :organization_type,
                                inverse_of: :organizations
  # rubocop:enable Rails/HasManyOrHasOneDependent

  has_many :requests, dependent: :restrict_with_error
  has_many :archived_requests, dependent: :restrict_with_error

  has_many :unit_requests, dependent: :restrict_with_error, class_name: 'Request', foreign_key: :unit_id,
                           inverse_of: :unit
  has_many :archived_unit_requests, dependent: :restrict_with_error,
                                    class_name: 'ArchivedRequest', foreign_key: :unit_id, inverse_of: :unit

  def requests_count
    unit? ? unit_requests.count : attributes['requests_count']
  end

  def archived_requests_count
    unit? ? archived_unit_requests.count : attributes['archived_requests_count']
  end

  has_many :roles, dependent: :delete_all
  validates_associated :roles
  accepts_nested_attributes_for :roles, reject_if: :all_blank, allow_destroy: true
  has_many :users, through: :roles

  validates :code, :organization_type, :name, presence: true
  validates :code, uniqueness: { scope: :organization_type }

  validate :only_one_root, :no_edits_if_archive

  # this makes sure we only have one root record
  def only_one_root
    return if organization_type != 'root'

    org =  Organization.find_by(organization_type: Organization.organization_types[:root])
    return if org.nil? || org.id == id

    errors.add(:organization_type, 'There can be only one root')
  end

  # this makes an org immutable if in archive. We can only activate/deactivate
  def no_edits_if_archive
    uneditable = changes.keys & UNEDITABLE_IF_ARCHIVED
    return unless persisted?
    return unless archived_records?
    return if uneditable.empty?

    uneditable.each do |k|
      msg = "#{description} has #{archived_requests.count} in the archive. Editing #{k} is not allowed."
      errors.add(k.intern, msg)
    end
  end

  def archived_records?
    if organization_type == 'unit'
      ArchivedRequest.where(unit_id: id).count.positive?
    else
      archived_requests_count.positive?
    end
  end

  def cutoff?
    return false unless organization_cutoff

    Time.zone.today > organization_cutoff.cutoff_date
  end

  def active?
    !cutoff? && !deactivated?
  end

  # the name of the record used in the json expression
  def text
    icon = if cutoff?
             'ban-circle'
           elsif deactivated?
             'remove-circle'
           else
             'ok-circle'
           end
    "#{name} (#{code}) <i class='glyphicon glyphicon-#{icon}'></i>"
  end

  def grandchildren
    children.map(&:children).flatten || []
  end

  def great_grandchildren
    grandchildren.map(&:children).flatten || []
  end

  # returns an array of the organizations up the tree
  def ancestors
    mom = parent
    ancestors = []
    while mom
      ancestors << mom
      mom = mom.parent
    end
    ancestors
  end

  def type_icon
    "glyphicon glyphicon-#{TYPE_MAPPING[organization_type]}"
  end

  def description
    "#{name} ( #{organization_type} )"
  end
end
