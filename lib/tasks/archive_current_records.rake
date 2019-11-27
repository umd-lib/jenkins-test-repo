# lib/tasks/archive_current_records.rake
namespace :db do
  desc 'Move records to archive tables'
  task :archive_current_records, [:fiscal_year] => :environment do |_t, args|
    fy  = Time.new(args[:fiscal_year]).to_date.end_of_financial_year
    abort "No fiscal year indicated." unless fy 
    %w( LaborRequest ContractorRequest StaffRequest ).each do |model|
      source_klass = model.constantize
      target_klass = "Archived#{model}".constantize
      source_klass.all.each do |record|
        target_klass.create!( record.attributes.slice(*target_klass.attribute_names).merge( fiscal_year: fy ) ) 
        record.delete 
      end
    end
  end
end

Rake::Task["db:archive_current_records"].enhance do
  Rake::Task["db:migrate"].invoke
end
