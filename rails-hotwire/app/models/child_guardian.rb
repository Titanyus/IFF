class ChildGuardian < ApplicationRecord
  belongs_to :child
  belongs_to :guardian
  validates :guardian_id, uniqueness: { scope: :child_id }
end
