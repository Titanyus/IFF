class CreatePocTables < ActiveRecord::Migration[8.1]
  def change
    create_table :users do |t|
      t.string :email, null: false
      t.string :password_digest, null: false
      t.timestamps
    end
    add_index :users, :email, unique: true

    create_table :groups do |t|
      t.string :slug, null: false
      t.string :label, null: false
      t.timestamps
    end
    add_index :groups, :slug, unique: true

    create_table :group_memberships do |t|
      t.references :user, null: false, foreign_key: true
      t.references :group, null: false, foreign_key: true
      t.timestamps
    end
    add_index :group_memberships, [:user_id, :group_id], unique: true

    create_table :children do |t|
      t.string :first_name, null: false
      t.string :last_name, null: false
      t.date :birth_date
      t.timestamps
    end
    create_table :guardians do |t|
      t.string :full_name, null: false
      t.string :phone
      t.timestamps
    end
    create_table :child_guardians do |t|
      t.references :child, null: false, foreign_key: true
      t.references :guardian, null: false, foreign_key: true
      t.string :relation, null: false, default: "Sorgeberechtigt"
      t.timestamps
    end
    add_index :child_guardians, [:child_id, :guardian_id], unique: true

    create_table :care_cases do |t|
      t.references :child, null: false, foreign_key: true
      t.string :status, null: false, default: "waiting"
      t.date :requested_on, null: false
      t.date :started_on
      t.date :ended_on
      t.datetime :deleted_at
      t.timestamps
    end
    add_index :care_cases, :status
    add_index :care_cases, :deleted_at

    create_table :case_assignments do |t|
      t.references :care_case, null: false, foreign_key: true
      t.references :user, null: false, foreign_key: true
      t.timestamps
    end
    add_index :case_assignments, [:care_case_id, :user_id], unique: true

    create_table :audit_events do |t|
      t.references :care_case, null: false, foreign_key: true
      t.references :actor, null: false, foreign_key: { to_table: :users }
      t.string :action, null: false
      t.string :from_status
      t.string :to_status
      t.timestamps
    end
  end
end
