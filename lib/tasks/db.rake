namespace :db do


  def update_version
    version_file = "#{Rails.root}/config/initializers/version.rb"

    git_tag = `git show --pretty=%H`[0..39]
    git_version = `git describe --always --tags` 

    version_string = "APP_VERSION = '#{git_version.chomp.strip}'\nGIT_TAG = '#{ git_tag.chomp.strip }'"
    File.open(version_file, "w") {|f| f.print(version_string)}
    $stderr.print(version_string)

  end

  task :migrate, [:environment, :load_config] do
    update_version
  end

end
