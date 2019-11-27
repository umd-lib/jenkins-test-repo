class AddOwner < ActiveRecord::Migration[4.2]
  def change
    add_reference :requests, :user, index: true
    add_reference :archived_requests, :user, index: true 
	end
end
