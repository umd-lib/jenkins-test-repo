[Date, Time, DateTime].each do |klass|
  klass.fiscal_zone = :us
  klass.use_forward_year!
end
