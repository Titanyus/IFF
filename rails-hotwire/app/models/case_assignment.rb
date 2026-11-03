class CaseAssignment < ApplicationRecord
  belongs_to :care_case
  belongs_to :user
  validates :user_id, uniqueness: { scope: :care_case_id }
end
