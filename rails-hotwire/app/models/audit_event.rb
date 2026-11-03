class AuditEvent < ApplicationRecord
  belongs_to :care_case
  belongs_to :actor, class_name: "User"
end
