# lib/tasks/sample_data.rake
namespace :db do
  desc 'Drop, create, migrate, seed and populate sample data'
  task reset_with_sample_data: [:drop, :create, :migrate, :seed, :populate_sample_data] do
    puts 'Ready to go!'
  end

  desc 'Populates the database with sample data'
  task populate_sample_data: :environment do

    num_users = 12
    num_users.times do
      create_user.save!
    end

    num_staff_requests = 50
    num_staff_requests.times do
      create_staff_request.save!
    end

    num_labor_requests = 50
    num_labor_requests.times do
      create_labor_request.save!
    end

    num_contractor_requests = 50
    num_contractor_requests.times do
      create_contractor_request.save!
    end
  end

  def create_user
    user = User.new( name: Faker::Name.name, cas_directory_id: Faker::Internet.email.split("@").first, admin: false  )
    user.roles.build organization:  Organization.offset( rand( Organization.count ) ).first
    user
  end

  def random_user
    User.offset( rand( User.count ) ).first
  end

  # Returns a valid StaffRequest object
  def create_staff_request
    staff_request = StaffRequest.new
    generate_common_fields(staff_request)
    staff_request.employee_name = Faker::Name.name if staff_request.employee_name_required?
    staff_request.annual_base_pay = (rand * 500_000.00).round(2)
    generate_nonop_fields(staff_request, staff_request.annual_base_pay)
    staff_request
  end

  # Returns a valid LaborRequest object
  def create_labor_request
    labor_request = LaborRequest.new
    generate_common_fields(labor_request)
    if labor_request.contractor_name_required?
      labor_request.contractor_name = Faker::Name.name
      labor_request.number_of_positions = 1
    else
      labor_request.number_of_positions = rand(20) + 1
    end

    generate_hourly_wage_fields(labor_request)
    max_funds = labor_request.hourly_rate * labor_request.hours_per_week * labor_request.number_of_weeks
    generate_nonop_fields(labor_request, max_funds)

    labor_request
  end

  # Returns a valid ContractorRequest object
  def create_contractor_request
    contractor_request = ContractorRequest.new
    generate_common_fields(contractor_request)

    if contractor_request.contractor_name_required?
      contractor_request.contractor_name = Faker::Name.name
    end
    contractor_request.number_of_months = rand(12) + 1
    contractor_request.annual_base_pay =  (rand * 500_000.00).round(2)
    generate_nonop_fields(contractor_request, contractor_request.annual_base_pay)
    contractor_request
  end

  # Randomly populates the fields common to all requests for the given
  # +request+
  def generate_common_fields(request)
    request.user = random_user
    request.position_title = Faker::Job.title
    request.employee_type = request.class::VALID_EMPLOYEE_TYPES.sample
    request.request_type = request.class::VALID_REQUEST_TYPES.sample
    depts = Organization.where( organization_type: Organization.organization_types["department"])
    dept = depts.offset(rand(depts.count)).first
    request.organization = dept
    if rand < 0.75 && dept.children.any?
      random_unit_index = rand(dept.children.count)
      request.unit = dept.children[random_unit_index]
    end
    request.justification = Faker::Lorem.words(rand(50) + 1).join(' ')
    request.review_status = ReviewStatus.offset(rand(ReviewStatus.count)).first
  end

  # Randomly chooses to add nonop_funds and nonop_source entries to the given
  # +request+. The+max_funds+ parameter controls the maximum amount to use in
  # nonop_funds.
  def generate_nonop_fields(request, max_funds)
    has_nonop = rand > 0.6
    return unless has_nonop
    request.nonop_funds = (max_funds * rand).round(2)
    request.nonop_source = Faker::Company.name
  end


  # Randomly add hourly wage fields to the given +request+
  def generate_hourly_wage_fields(request)
    request.hourly_rate = (rand * 100.0).round(2)
    request.hours_per_week = (rand * 40.0).to_i + 1
    request.number_of_weeks = (rand * 52).to_i + 1
  end

end

Rake::Task["db:populate_sample_data"].enhance do
  Rake::Task["db:migrate"].invoke
end
