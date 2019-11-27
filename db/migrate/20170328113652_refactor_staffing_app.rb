class RefactorStaffingApp < ActiveRecord::Migration[4.2]
  def change

		create_table "organizations", force: :cascade do |t|
			t.string :name
			t.string :code
			t.integer "organization_id", index: true
		  t.integer "organization_type", index: true	
			t.integer  "requests_count",          default: 0
			t.integer  "archived_requests_count",          default: 0
      t.timestamps null: false
		end

		create_table "organization_cutoffs", primary_key: :organization_type, force: :cascade do |t|
			t.date     "cutoff_date"
			t.datetime "created_at",   null: false
			t.datetime "updated_at",   null: false
  	end
		
		create_table "review_statuses", force: :cascade do |t|
			t.string   "name"
			t.string   "color",                              default: "#ffffff"
			t.datetime "created_at",                                             null: false
			t.datetime "updated_at",                                             null: false
			t.string   "code"
			t.integer  "requests_count",          default: 0
			t.integer  "archived_requests_count",          default: 0
		end
	
		create_table "requests", force: :cascade do |t|
			t.string   "position_title"
			
			t.integer  "request_model_type"
			t.integer  "request_type"
			t.integer  "employee_type"
			
			t.decimal  "annual_base_pay_cents"
			t.string   "contractor_name"
			t.integer  "number_of_months"
			t.integer  "number_of_positions"
			t.decimal  "hourly_rate_cents"
			t.decimal  "hours_per_week"
			t.integer  "number_of_weeks"
			t.decimal  "nonop_funds_cents"
			t.string   "nonop_source"
			
			t.integer  "organization_id",  index: true
			t.integer  "unit_id",  index: true
			t.integer  "review_status_id",  index: true

			t.text     "justification"
			t.datetime "created_at"
			t.datetime "updated_at"
			t.text     "review_comment"
			t.string   "employee_name"
		end
		
    create_table "archived_requests", force: :cascade do |t|
			t.string   "position_title"
			
			t.integer  "request_model_type"
			t.integer  "request_type"
			t.integer  "employee_type"
			
			t.decimal  "annual_base_pay_cents"
			t.string   "contractor_name"
			t.integer  "number_of_months"
			t.integer  "number_of_positions"
			t.decimal  "hourly_rate_cents"
			t.decimal  "hours_per_week"
			t.integer  "number_of_weeks"
			t.decimal  "nonop_funds_cents"
			t.string   "nonop_source"
			
			t.integer  "organization_id",  index: true
			t.integer  "unit_id",  index: true
			t.integer  "review_status_id",  index: true

			t.text     "justification"
			t.datetime "created_at"
			t.datetime "updated_at"
			t.text     "review_comment"
			t.string   "employee_name"
			
      t.datetime  "fiscal_year"
		
    end
		
		create_table "users", force: :cascade do |t|
			t.string   "cas_directory_id"
			t.string   "name"
			t.datetime "created_at",                       null: false
			t.datetime "updated_at",                       null: false
			t.boolean  "admin",            default: false
		end
		
		create_table "roles", force: :cascade do |t|
			t.belongs_to  :user, index: true
			t.belongs_to  :organization, index: true
		end
  
	end
end
