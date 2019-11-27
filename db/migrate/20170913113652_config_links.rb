class ConfigLinks < ActiveRecord::Migration[4.2]
  def change
		create_table "links", force: :cascade do |t|
			t.string   "url"
			t.string   "text"
    end
	end
end
