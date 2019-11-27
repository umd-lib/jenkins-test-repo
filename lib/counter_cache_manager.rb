# this resets the magic counter cache column
# setup to run after db:migrate and in tests
# after fixtures load

class CounterCacheManager
  class << self
    def run
      Rails.application.eager_load!
      logger ||= Logger.new(STDOUT)
      logger.info("Resetting counter cache fields..") unless Rails.env === 'test'
      # get all reflections
      ActiveRecord::Base.descendants.each do |klass|
        next if klass == Organization # too much trouble...we'll brute force it later. 
        klass.reflections.each do |_name, ref|
          # find those using counter cache
          next unless ref.options[:counter_cache]
          # get reflection class
          one_klass = ref.class_name.constantize
          one_table, many_table = [one_klass, klass].map(&:table_name)
          # get all the ids for the cache
          ids = one_klass
                .joins(many_table.to_sym)
                .group("#{one_table}.id", "#{many_table}_count")
                .having("#{one_table}.#{many_table}_count != COUNT(#{many_table}.id)")
                .pluck("#{one_table}.id")
          # logger.info  "Resetting cache for #{one_klass} for #{klass} ( #{ids.length.to_s} #{many_table} records)"
          ids.each do |id|
            one_klass.reset_counters id, many_table
          end
        end
      end
      Organization.all.pluck(:id).each { |o| Organization.reset_counters o, :requests }
    end
  end
end
