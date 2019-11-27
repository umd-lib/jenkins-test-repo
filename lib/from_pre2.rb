module FromPre2

  module ClassMethods
    def from_pre2(obj)
      obj.delete("id") 
      obj.delete("department") 
      
      org = Organization.find_by(name: obj["organization"],  organization_type: Organization.organization_types["department"]  )
      unless org
        puts "Cannot find Organization with #{obj['organization']}"
      end
      obj["organization"] = org 
      
      unit =  Organization.find_by(name: obj["unit"], organization_type: Organization.organization_types["unit"]  )
      obj["unit"] = unit 
      
      obj["review_status"] = ReviewStatus.find_by(name: obj["review_status"]) 
      new obj 
    end
  end

  class << self
    def included klass
      klass.extend ClassMethods
    end
  end

end
