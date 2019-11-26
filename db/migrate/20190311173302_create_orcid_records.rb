class CreateOrcidRecords < ActiveRecord::Migration[5.2]
  def change
    create_table :orcid_records do |t|
      t.string :uid
      t.string :orcid_id
      t.datetime :registered_at

      t.timestamps
    end
  end
end
