# lib/tasks/add_cas_user.rake
require_relative '../counter_cache_manager'
namespace :db do
  task :migrate do
    CounterCacheManager.run 
  end

  task :reset_counter_cache do
    CounterCacheManager.run
  end
end
