# this prepopulated required cutoff values, but only if we've actually run our
# migrations and the tables exists...
if ActiveRecord::Base.connection.table_exists? 'organization_cutoffs'
  Organization.organization_types.values.each do |org|
    oc = OrganizationCutoff.find_or_create_by(organization_type: org)
    next if oc.cutoff_date
    oc.update_columns(cutoff_date: Time.zone.now + 1.year)
  end
end
