require_relative '../from_pre2'
require 'json'
namespace :db do

  desc "Loads data from pre-2.0 json ( tmp/requests.json and tmp/users.json ) into current db"
  task load_data: :environment do
    Rails.application.eager_load!
    Request.include FromPre2
    JSON.parse(IO.read(Rails.root.join('tmp/requests.json'))).each do |json|
      model = "#{json["request_model_type"]}_request".camelcase.constantize
      record = model.from_pre2(json)
      unless record.save
        puts "Errors for #{record.position_title} : #{record.errors.messages.inspect}"
      end
    end
    JSON.parse(IO.read(Rails.root.join('tmp/users.json'))).each do |json|
      roles = json.delete "roles"
      user = User.new json
      roles.each do |r|
        org = Organization.find_by_name(r)
        if org
          user.roles.new organization: org 
        else 
          puts "Unable to find #{r} organization associated to #{json['name']}" unless org
        end
      end
      unless user.save
        puts "Errors for User #{user.name} : #{user.errors.message.inspect}"
      end
    end
  end
end
