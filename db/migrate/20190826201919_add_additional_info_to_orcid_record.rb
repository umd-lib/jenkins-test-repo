class AddAdditionalInfoToOrcidRecord < ActiveRecord::Migration[5.2]
  def change
    add_column :orcid_records, :access_token, :string
    add_column :orcid_records, :expires_in, :bigint
    add_column :orcid_records, :refresh_token, :string
    add_column :orcid_records, :token_type, :string
    add_column :orcid_records, :scope, :string
  end
end
