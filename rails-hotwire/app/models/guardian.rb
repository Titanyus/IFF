class Guardian < ApplicationRecord
  has_many :child_guardians, dependent: :restrict_with_exception
  has_many :children, through: :child_guardians
  validates :full_name, presence: true, length: { maximum: 200 }
end
