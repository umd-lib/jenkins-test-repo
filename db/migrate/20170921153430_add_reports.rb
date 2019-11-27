class AddReports < ActiveRecord::Migration[4.2]
  def change

    create_table :reports do |t|

      t.binary :output, limit: 50.megabyte
      t.text :parameters

      t.column :format, :integer, default: 0, null: false
      t.column  :status, :integer, default: 0, null: false
      t.string :name, null: false

      t.references :user, index: true, foreign_key: true
      t.timestamps null: false
      t.string :status_message
    end

  end
end


